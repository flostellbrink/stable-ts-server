FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-pip &&\
  pip install pipenv && pipenv install --system --deploy --ignore-pipfile

CMD ["pipenv", "run", "start"]
