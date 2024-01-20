# Сервис классификации текстов с использованием FastAPI и RNN

Этот проект представляет собой worker для классификации текстов с помощью рекуррентных нейронных сетей (RNN).

Задача: классифицировать тексты на основе записи контактов в свое приложение на классы "Физичческое Лицо", "Юридическое Лицо" и "Остальные".


## Запуск приложения

Для запуска приложения необходимо выполнить следующие команды:

```bash
docker build -t rnn_worker .
docker run rnn_worker
```

## Настройка приложения через .env

Для настройки приложения необходимо создать файл .env в корне проекта и заполнить его следующим образом:

```bash

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=local
RABBITMQ_PASSWORD=1234567890
RABBITMQ_QUEUE=contact_classified
DATABASE_HOST=mysql
DATABASE_ROOT_PASSWORD=1234567890
DATABASE_NAME=local
DATABASE_USER=local
DATABASE_PASSWORD=1234567890
DATABASE_PORT=3306

```

## Отправка сообщений в очередь

Для отправки сообщений в очередь необходимо выполнить следующие команды:

```bash

import pika
import json

# RabbitMQ параметры
RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'contact_classified'
RABBITMQ_USERNAME = 'local'
RABBITMQ_PASSWORD = '1234567890'

# Создание соединения с RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672,
                                                               credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE)

# Пример сообщения для отправки
message = {"id": "идентификатор текста", "text": "текст для классификации"}

# Отправка сообщения
channel.basic_publish(exchange='',
                      routing_key=RABBITMQ_QUEUE,
                      body=json.dumps(message))

print("Sent:", message)

# Закрытие соединения
connection.close()


```

## Выгрузка результатов классификации в базу данных

Выгрузка результатов классификации в базу данных происходит автоматически при получении сообщения из очереди. В таблицу `messages` добавляются следующие поля:

* `id` - идентификатор сообщения
* `phone_number` - номер телефона сообщения
* `label` - класс сообщения (физ лицо, юр лицо, остальные)

Класс отвечающий за выгрузку результатов классификации в базу данных находится в файле `main.py` и выглядит следующим образом:

```python
class IsCompany(Model):
    __tablename__ = "is_company"

    id = Column(Integer, primary_key=True)
    phone_number = Column(Integer)
    label = Column(String)
```

При необходимости можно изменить название таблицы и названия полей.