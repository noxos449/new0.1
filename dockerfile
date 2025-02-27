FROM python:3.9-slim

# Install system dependencies and Chromium/ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libxcursor1 \
    libxrandr2 \
    libgbm1 \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables so Selenium knows where Chromium is located
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

# Copy dependency file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Run the bot
CMD ["python", "mybot.py"]
