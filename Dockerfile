FROM python:2-alpine

WORKDIR /

ADD stream.py ./
ADD Pipfile.lock ./
ADD Pipfile ./

RUN apk add --update \
&& pip install pipenv \
&& pipenv install --ignore-pipfile --deploy --system

CMD [ "python", "./stream.py" ]
