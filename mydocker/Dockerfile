FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev

COPY app.py .

RUN pip install psycopg2-binary

CMD ["python3", "app.py"]
