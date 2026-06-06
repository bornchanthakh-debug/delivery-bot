FROM python:3.10-slim

# ដំឡើង dependencies ដែលចាំបាច់សម្រាប់ OpenCV 
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ទាញយក EasyOCR Model ទុកមុន
RUN python -c "import easyocr; reader = easyocr.Reader(['en'], gpu=False)"

CMD ["python", "bot.py"]