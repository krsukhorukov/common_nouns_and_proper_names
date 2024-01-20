import os
import pika
import json
import pandas as pd
import re
import nltk
from loguru import logger
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from deeppavlov import build_model

import config

load_dotenv()
DEBUG = int(os.environ.get("DEBUG", False))


class Worker:
    def __init__(self):
        self.engine = config.get_db_conn()
        self.entity_recognitor = {
            "ner_ontonotes_bert_mult": build_model('./ner/ner_ontonotes_bert_mult.json'),
            "ner_ontonotes_bert": build_model('./ner/ner_ontonotes_bert.json'),
            "ner_rus_bert": build_model('./ner/ner_rus_bert.json'),
            "ner_collection3_bert": build_model('./ner/ner_collection3_bert.json')
        }
        if DEBUG:
            logger.info("Connected to MySQL database")

        credentials = pika.PlainCredentials(os.environ.get("RABBITMQ_USER"), os.environ.get("RABBITMQ_PASSWORD"))
        parameters = pika.ConnectionParameters(os.environ.get("RABBITMQ_HOST"), int(os.environ.get("RABBITMQ_PORT")),
                                               '/', credentials)
        self.rabbitmq = pika.BlockingConnection(parameters)
        self.channel = self.rabbitmq.channel()
        self.queue = os.environ.get("RABBITMQ_QUEUE")
        if DEBUG:
            logger.info("Connected to RabbitMQ")

        # Declare the queue
        self.channel.queue_declare(queue=self.queue)
        self.channel.basic_qos(prefetch_count=1)

    def __del__(self):
        self.rabbitmq.close()
    
    def vote(self, labels: list):
        label_mapping = {
            "person": 0,
            "org": 0,
            "other": 0
        }
        for label in labels:
            if "PER" in label:
                label_mapping["person"] += 1
            elif "ORG" in label:
                label_mapping["org"] += 1
            else:
                label_mapping["other"] += 1
        
        return max(label_mapping, key=label_mapping.get)
    
    def preprocess(self, data):
        data = data.copy()
        data["text"] = data["text"].fillna("fillna")
        data["text"] = data['text'].str.lower()
        data['text'] = data['text'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
        data['text'] = data['text'].apply(nltk.word_tokenize)
        data['text'] = data['text'].apply(lambda x: [word.title() for word in x])
        data['text'] = data['text'].apply(lambda x: ' '.join(x))
        return data
    
    def execute(self):
        def callback(ch, method, properties, body):
            message = json.loads(body.decode('utf-8'))
            if DEBUG:
                logger.info("Received message: {}".format(message))

            table_name = f"contacts.contacts_{str(message['number'])[:5]}"
            query = f"""
                SELECT first_name, last_name, COUNT(*) as count
                FROM (
                    SELECT first_name, last_name, name_hash
                    FROM {table_name}   
                    WHERE `number` = {message['number']} AND (
                        profile_id = 0 OR profile_id IS NULL OR
                        (profile_id, created_at) IN (
                            SELECT profile_id, MAX(created_at)
                            FROM {table_name}
                            WHERE profile_id != 0 AND `number` = {message['number']}
                            GROUP BY profile_id
                        )
                    )
                ) AS filtered_contacts
                GROUP BY name_hash
                ORDER BY count DESC
            """
            with self.engine.connect() as connection:
                df = pd.read_sql_query(con=connection, sql=text(query))
            df["text"] = df["first_name"] + " " + df["last_name"]
            df = self.preprocess(df)

            conversion_count = 0
            with self.engine.connect() as conn:
                sql = text(f"""
                    SELECT count(*) FROM company_detect_conversion where phone_number = {message['number']};
                """)
                results = conn.execute(sql)
                for record in results: 
                    conversion_count += record[0]

            if conversion_count == 0 or 0.85 < conversion_count  / len(df) < 1.15:
                # Counting Entities and Individuals
                res = []
                for i in range(len(df)):
                    text_i = df.loc[i, 'text']
                    pred = self.vote(
                        self.entity_recognitor[config.get_model_by_detect_language(text_i)]([text_i])[1][0])
                    res.append(pred)
                df["entity_rec"] = res

                new_df = df.groupby('entity_rec').agg({"count": "sum"}).reset_index()
                ner_result = new_df.loc[new_df['count'].argmax(), 'entity_rec']

                with self.engine.connect() as conn:
                    sql = text(f"""
                        INSERT INTO company_detect_conversion (count, phone_number) VALUES({len(df)}, {message['number']});
                    """)
                    conn.execute(sql)
                    status = int(ner_result == "org" and new_df["count"].max() >= 5)
                    sql = text(f"""
                        INSERT INTO is_company (phone_number, `type`, status, updated_at) 
                        VALUES({message['number']}, 'contacts', {status}, CURRENT_TIMESTAMP)
                        ON DUPLICATE KEY UPDATE status = {status}, updated_at = CURRENT_TIMESTAMP;
                    """)
                    conn.execute(sql)
                    conn.commit()
                    if DEBUG:
                        logger.info("Sent SQL Query")
            else:
                if DEBUG:
                    logger.info("Without conversion")


        self.channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()


if __name__ == "__main__":
    worker = Worker()
    worker.execute()
