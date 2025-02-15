FROM python:3.12-slim

WORKDIR /app

ENV TZ=Europe/Warsaw
RUN apk add --no-cache tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install -y gcc libffi-dev libpq-dev python3-dev

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
