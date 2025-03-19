import os
import time
import json
import random
import logging
import pywhatkit
import chromedriver_autoinstaller

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

class WhatsAppScraper:
    def __init__(self):
        self.driver = None
        self.numbers_file = "whatsapp_numbers.json"
        self.init_driver()

    def init_driver(self):
        """Initialize Selenium WebDriver with correct Chrome setup."""
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=./chrome-data") 

        self.driver = webdriver.Chrome(service=Service(), options=options)

        self.driver.get("https://web.whatsapp.com")
        logging.info("WhatsApp Web opened. Please Scan the QR code.")

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='side']"))
        )
        logging.info("Logged in successfully into WhatsApp Web.")

    def extract_group_members(self, group_names=None):
        """Extract numbers from a specified groups"""
        if not group_names:
            logging.error("No group names provided to extract numbers from.")
            return
        
        # Ensure group_names is always a list
        if isinstance(group_names, str):
            group_names = [group_names]

        try:
            group_members = []
            wait = WebDriverWait(self.driver, 20)

            for group_name in group_names:
                logging.info(f"Extracting numbers from group: {group_name}")
                # Add delay to avoid blocking
                time.sleep(random.randint(2, 5))

                # Click the input search box
                search_box_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='side']/div[1]/div/div[2]/div"))
                )
                if not search_box_element:
                    logging.error("Search box not found.")
                    return
                
                search_box_element.click()
                time.sleep(10)
                search_box_element.send_keys(group_name)

                # Wait for the group to appear
                group_name_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//span[@title='{group_name}']"))
                )
                if not group_name_element:
                    logging.error(f"Group: {group_name} not found.")
                    return
                
                group_name_element.click()

                # Wait for group info and click it
                group_header_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='main']/header"))
                )
                if not group_header_element:
                    logging.error("Group header not found.")
                    return
                
                group_header_element.click()

                # Wait and click search icon
                group_search_member_icon_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div/div[3]/div/div[5]/span/div/span/div/div/div/section/div[6]/div[1]/div/div[2]/span"))
                )
                if not group_search_member_icon_element:
                    logging.error("Group search member icon not found.")
                    return
                
                group_search_member_icon_element.click()

                # Scroll and extract all available contacts
                members_container_xpath = "//*[@id='app']/div/span[2]/div/span/div/div/div/div/div/div/div[2]/div/div/div"
                members_container = wait.until(EC.presence_of_element_located((By.XPATH, members_container_xpath)))
                if not members_container:
                    logging.error("Members container not found.")
                    return
                
                last_height = 0
                while True:
                    # Extract member details
                    member_elements = self.driver.find_elements(By.CSS_SELECTOR, "div._ak8l")

                    for member in member_elements:
                        try:
                            # Extract unsaved name & number
                            unsaved_name_elem = member.find_element(By.CSS_SELECTOR, "div._ak8l > div._ak8o[role='gridcell'] > div._ak8q > div[title]")
                            unsaved_number_elem = member.find_element(By.CSS_SELECTOR, "div._ak8j > div._ak8i[role='gridcell'] > span._ajzr > span")
                        
                            unsaved_name = unsaved_name_elem.get_attribute("title").strip()
                            unsaved_number = unsaved_number_elem.text.strip()

                            if unsaved_name and unsaved_number:
                                group_members.append(unsaved_number)
                                logging.info(f"Unsaved Contact: {unsaved_name} - {unsaved_number}")

                        except NoSuchElementException:
                            # If unsaved contact check fails, try saved contacts
                            try:
                                contact_name_elem = member.find_element(By.CSS_SELECTOR, "div._ak8l > div._ak8o[role='gridcell'] > div._ak8q > div > span[title]")
                                contact_number_elem = member.find_element(By.CSS_SELECTOR, "div._ak8j > div._ak8i[role='gridcell'] > span._ajzr > span")
                            
                                contact_name = contact_name_elem.get_attribute("title").strip()
                                contact_number = contact_number_elem.text.strip()

                                if contact_name and not contact_number:
                                    group_members.append(contact_name)
                                    logging.info(f"Saved Contact: {contact_name}")

                            except NoSuchElementException:
                                continue


                    # Scroll down
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", members_container)
                    time.sleep(2)

                    # Check if new content is loaded
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight;", members_container)
                    if new_height == last_height:
                        break  # No more contacts to load

                    last_height = new_height

                # save extracted numbers to a file
                with open(self.numbers_file, "w") as f:
                    json.dump(group_members, f, indent=4)

        except Exception as e:
            logging.error(f"Error occurred while extracting numbers: {e}")

    def close_driver(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed.")



if __name__ == "__main__":
    scraper = WhatsAppScraper()

    group_list = ["My family"]
    scraper.extract_group_members(group_list)

    scraper.close_driver()