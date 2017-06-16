FROM python:2-alpine

ADD stream.py /

RUN apk add --update \
    gcc \
    libffi-dev \
    python-dev \
    openssl-dev \
    musl-dev \
    py-mysqldb

RUN pip install tweepy boto3 credstash PyMySQL

CMD [ "python", "./stream.py" ]
