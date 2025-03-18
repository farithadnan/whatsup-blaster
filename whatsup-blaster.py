import os
import time
import json
import random
import platform
import logging
from click import group
import pywhatkit
import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

class WhatsAppBlaster:
    def __init__(self):
        self.OP_SYSTEM = platform.system().lower()
        self.driver = None
        self.numbers_file = "whatsapp_numbers.json"

        # Install Chrome driver if needed (Windows only)
        if self.OP_SYSTEM == "windows":
            chromedriver_autoinstaller.install()

        self.init_driver()

    def init_driver(self):
        """Initialize Selenium WebDriver with correct Chrome setup."""
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=./chrome-data") 

        if self.OP_SYSTEM == "windows":
            self.driver = webdriver.Chrome(options=options)
        else:
            from selenium.webdriver.chrome.service import Service
            self.driver = webdriver.Chrome(service=Service(), options=options)

        self.driver.get("https://web.whatsapp.com")
        logging.info("WhatsApp Web opened. Please Scan the QR code.")

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
        )
        logging.info("Logged in successfully into WhatsApp Web.")

    def extract_numbers(self, group_name=None):
        """Extract numbers from a specified group or default groups."""
        try:
            numbers = []
            time.sleep(5)

            if group_name:
                group_element = self.driver.find_element(By.XPATH, f"//span[@title='{group_name}']")
                group_element.click()
            else:
                return []
            

        except Exception as e:
            logging.error(f"Error occurred while extracting numbers: {e}")

    
    def close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed.")



if __name__ == "__main__":
    bot = WhatsAppBlaster()

    bot.close_driver()