# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /SpotOn

COPY . .
RUN pip3 install -r requirements.txt

CMD [ "python3", "./main.py"]