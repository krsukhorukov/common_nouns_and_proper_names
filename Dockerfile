FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Create directory for Deeppavlov models and True Name Recognition models
RUN mkdir -p .deeppavlov/models/ner_ontonotes_bert_torch_crf
RUN mkdir -p .deeppavlov/models/ner_ontonotes_torch_bert_mult_crf
RUN mkdir -p .deeppavlov/models/ner_rus_bert_coll3_torch
RUN mkdir -p .deeppavlov/models/ner_rus_bert_torch

# Set build arguments for AWS credentials
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

# Install boto3 library
RUN pip install --no-cache-dir boto3

# Download models from S3
RUN python -c "\
import boto3;\
s3 = boto3.client('s3', aws_access_key_id='${AWS_ACCESS_KEY_ID}', aws_secret_access_key='${AWS_SECRET_ACCESS_KEY}', region_name='eu-north-1');\
# Deeppavlov models
s3.download_file('models-cache', 'deeppavlov/models/ner_ontonotes_bert_torch_crf/model_crf.pth.tar', '.deeppavlov/models/ner_ontonotes_bert_torch_crf/model_crf.pth.tar');\
s3.download_file('models-cache', 'deeppavlov/models/ner_ontonotes_bert_torch_crf/model.pth.tar', '.deeppavlov/models/ner_ontonotes_bert_torch_crf/model.pth.tar');\
s3.download_file('models-cache', 'deeppavlov/models/ner_ontonotes_bert_torch_crf/tag.dict', '.deeppavlov/models/ner_ontonotes_bert_torch_crf/tag.dict');\
s3.download_file('models-cache', 'deeppavlov/models/ner_ontonotes_torch_bert_mult_crf/model_crf.pth.tar', '.deeppavlov/models/ner_ontonotes_torch_bert_mult_crf/model_crf.pth.tar');\
s3.download_file('models-cache', 'deeppavlov/models/ner_ontonotes_torch_bert_mult_crf/model.pth.tar', '.deeppavlov/models/ner_ontonotes_torch_bert_mult_crf/model.pth.tar');\
s3.download_file('models-cache', 'deeppavlov/models/ner_ontonotes_torch_bert_mult_crf/tag.dict', '.deeppavlov/models/ner_ontonotes_torch_bert_mult_crf/tag.dict');\
s3.download_file('models-cache', 'deeppavlov/models/ner_rus_bert_coll3_torch/model.pth.tar', '.deeppavlov/models/ner_rus_bert_coll3_torch/model.pth.tar');\
s3.download_file('models-cache', 'deeppavlov/models/ner_rus_bert_coll3_torch/tag.dict', '.deeppavlov/models/ner_rus_bert_coll3_torch/tag.dict');\
s3.download_file('models-cache', 'deeppavlov/models/ner_rus_bert_torch/model.pth.tar', '.deeppavlov/models/ner_rus_bert_torch/model.pth.tar');\
s3.download_file('models-cache', 'deeppavlov/models/ner_rus_bert_torch/tag.dict', '.deeppavlov/models/ner_rus_bert_torch/tag.dict');"

COPY . .

CMD ["python", "main.py"]
