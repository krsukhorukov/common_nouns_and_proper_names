import os
from sqlalchemy import create_engine
from langdetect import detect

SQL_USER = os.environ.get("DATABASE_USER")
SQL_PASSWORD = os.environ.get("DATABASE_PASSWORD")
SQL_DB = os.environ.get("DATABASE_NAME")
SQL_HOST = os.environ.get("DATABASE_HOST")
SQL_PORT = os.environ.get("DATABASE_PORT")
SQL_ROOT_PASSWORD = os.environ.get("DATABASE_ROOT_PASSWORD", "")
SQL_ENGINE = "mysql+mysqlconnector"
MAPPING = {
    0: "Физическое Лицо",
    1: "Юридическое Лицо",
    2: "Остальные"
}

language_dict = {
    'af': 'ner_ontonotes_bert_mult',
    'ar': 'ner_ontonotes_bert_mult',
    'bg': 'ner_collection3_bert',
    'bn': 'ner_ontonotes_bert_mult',
    'ca': 'ner_ontonotes_bert_mult',
    'cs': 'ner_collection3_bert',
    'cy': 'ner_ontonotes_bert_mult',
    'da': 'ner_ontonotes_bert_mult',
    'de': 'ner_ontonotes_bert',
    'el': 'ner_ontonotes_bert_mult',
    'en': 'ner_ontonotes_bert',
    'es': 'ner_ontonotes_bert',
    'et': 'ner_collection3_bert',
    'fa': 'ner_ontonotes_bert_mult',
    'fi': 'ner_ontonotes_bert',
    'fr': 'ner_ontonotes_bert',
    'gu': 'ner_ontonotes_bert_mult',
    'he': 'ner_ontonotes_bert_mult',
    'hi': 'ner_ontonotes_bert_mult',
    'hr': 'ner_ontonotes_bert_mult',
    'hu': 'ner_ontonotes_bert_mult',
    'id': 'ner_ontonotes_bert_mult',
    'it': 'ner_ontonotes_bert',
    'ja': 'ner_ontonotes_bert_mult',
    'kn': 'ner_ontonotes_bert',
    'ko': 'ner_ontonotes_bert_mult',
    'lt': 'ner_ontonotes_bert_mult',
    'lv': 'ner_collection3_bert',
    'mk': 'ner_ontonotes_bert_mult',
    'ml': 'ner_ontonotes_bert_mult',
    'mr': 'ner_ontonotes_bert_mult',
    'ne': 'ner_ontonotes_bert_mult',
    'nl': 'ner_ontonotes_bert_mult',
    'no': 'ner_collection3_bert',
    'pa': 'ner_ontonotes_bert_mult',
    'pl': 'ner_collection3_bert',
    'pt': 'ner_ontonotes_bert',
    'ro': 'ner_collection3_bert',
    'ru': 'ner_rus_bert',
    'sk': 'ner_collection3_bert',
    'sl': 'ner_collection3_bert',
    'so': 'ner_ontonotes_bert_mult',
    'sq': 'ner_ontonotes_bert_mult',
    'sv': 'ner_ontonotes_bert',
    'sw': 'ner_ontonotes_bert_mult',
    'ta': 'ner_ontonotes_bert_mult',
    'te': 'ner_ontonotes_bert_mult',
    'th': 'ner_ontonotes_bert_mult',
    'tl': 'ner_ontonotes_bert_mult',
    'tr': 'ner_ontonotes_bert_mult',
    'uk': 'ner_collection3_bert',
    'ur': 'ner_ontonotes_bert_mult',
    'vi': 'ner_ontonotes_bert_mult',
    'zh-cn': 'ner_ontonotes_bert_mult',
    'zh-tw': 'ner_ontonotes_bert_mult',
    'other': 'ner_ontonotes_bert_mult'
}



def get_db_conn():
    db_url = f"{SQL_ENGINE}://{SQL_USER}:{SQL_PASSWORD}" + \
             f"@{SQL_HOST}:{SQL_PORT}/{SQL_DB}"

    engine = create_engine(db_url)
    return engine


def get_model_by_detect_language(text):
    try:
        global language_dict
        language = detect(text)
        return language_dict[language]
    except:
        return 'ner_ontonotes_bert_mult'
