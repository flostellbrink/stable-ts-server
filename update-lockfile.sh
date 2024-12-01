#!/bin/bash

docker run -it --rm -v ./:/app --platform=linux/amd64 nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 /bin/bash -c "cd /app && apt-get update && apt-get install -y python3 python3-pip && pip install pipenv && pipenv lock"
 