FROM python:3.8.0-alpine3.10

WORKDIR /

ADD stream.py ./
ADD Pipfile.lock ./
ADD Pipfile ./

RUN apk add --update \
&& pip install pipenv \
&& pipenv install --ignore-pipfile --deploy --system

CMD [ "python", "./stream.py" ]
