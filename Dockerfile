FROM python:2-alpine

ADD stream.py /

RUN apk add --update

RUN pip install tweepy boto3

CMD [ "python", "./stream.py" ]
