FROM python:3.10-slim

# ដំឡើង Tesseract OCR និង dependencies ដែលចាំបាច់
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# បញ្ជាឱ្យរត់ bot.py ពេល Server ដើរ
CMD ["python", "bot.py"]
