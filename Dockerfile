# SmartPark53 - Production-ready image (sunucu için uyumlu)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Bağımlılıklar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama
COPY app.py db.py tarife.py plaka_tanima.py ./
COPY templates/ templates/

EXPOSE 5000

# Gunicorn ile çalıştır (sunucu / Docker için)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "app:app"]
