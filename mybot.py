import time
import logging
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Read Telegram Bot Credentials from environment variables
TELEGRAM_BOT_TOKEN = "7935730367:AAGhHmu84OT8PMlSuW10-WH_BOTsz0BbKwk"
TELEGRAM_CHAT_ID = "2144001639"

# Kleinanzeigen URL
KLEINANZEIGEN_URL = "https://www.kleinanzeigen.de/s-fahrraeder/47053/c217l2148r35"

# Logging Configuration
logging.basicConfig(filename="bot_errors.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending Telegram message: {e}")

# Set up Chrome WebDriver
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.page_load_strategy = "eager"  # Load only essential elements

# Use CHROMEDRIVER_BIN environment variable if provided; otherwise, default to /usr/bin/chromedriver
chromedriver_path = os.environ.get("CHROMEDRIVER_BIN", "/usr/bin/chromedriver")
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# Track seen listings
seen_ads = set()

def scrape_kleinanzeigen():
    try:
        driver.get(KLEINANZEIGEN_URL)
        # Wait up to 5 seconds for ads to load
        wait = WebDriverWait(driver, 5)
        ads = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "aditem")))
        for ad in ads:
            try:
                title = ad.find_element(By.CSS_SELECTOR, "h2.text-module-begin a").text
                price = ad.find_element(By.CSS_SELECTOR, "p.aditem-main--middle--price-shipping--price").text
                location = ad.find_element(By.CSS_SELECTOR, "div.aditem-main--top--left").text
                link = ad.find_element(By.CSS_SELECTOR, "h2.text-module-begin a").get_attribute("href")
                ad_id = ad.get_attribute("data-adid")
                if ad_id not in seen_ads:
                    seen_ads.add(ad_id)
                    message = f"{title} - {price}\n📍 {location}\n🔗 {link}"
                    send_telegram_message(message)
            except Exception as e:
                logging.error(f"Error parsing ad: {e}")
    except Exception as e:
        logging.error(f"Error during scraping: {e}")

def main():
    send_telegram_message("✅ Kleinanzeigen Bot gestartet!")
    while True:
        scrape_kleinanzeigen()
        time.sleep(0.5)  # Poll every 0.5 seconds

if __name__ == "__main__":
    main()
