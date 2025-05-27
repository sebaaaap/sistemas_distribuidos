FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pymongo

CMD ["python", "filtrador.py"]
