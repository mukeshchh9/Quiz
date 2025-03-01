
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pytelegrambotapi

CMD ["python", "main.py"]