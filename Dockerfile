FROM python:3.8.0-alpine3.10

WORKDIR /

ADD stream.py ./
ADD Pipfile ./

RUN apk add --update \
    && pip install pipenv \
    && pipenv lock \
    && pipenv install --deploy --system

CMD [ "python", "./stream.py" ]
