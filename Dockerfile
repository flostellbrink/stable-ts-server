FROM python:3.12

COPY . /app
WORKDIR /app

RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

CMD ["pipenv", "run", "start"]
