FROM python:3.8.0-alpine3.10

WORKDIR /beer_alert

COPY Pipfile .
COPY setup.py .

COPY beer_alert ./beer_alert
COPY data.yaml .

RUN pip install pipenv \
    && pipenv lock \
    && pipenv install --deploy --system

CMD [ "python", "./beer_alert/beer_alert.py" ]
