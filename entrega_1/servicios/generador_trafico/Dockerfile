FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt watchdog

# No copiamos el código aquí, se montará en tiempo real
CMD ["python", "-m", "watchdog", "--recursive", "--interval=1", "--patterns=*.py", "--command=python app/main.py"]