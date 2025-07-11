FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    libnss3 libgconf-2-4 libxss1 libappindicator3-1 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
