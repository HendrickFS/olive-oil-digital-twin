FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5555

CMD ["gunicorn", "--bind", "0.0.0.0:5555", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
