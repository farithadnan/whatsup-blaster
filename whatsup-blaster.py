import os
import csv
import time
import json
import random
import logging
import sqlite3
import pywhatkit.whats as whatsApp

from tqdm import tqdm
from pathlib import Path
from datetime import datetime

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

class WhatsUpBlaster:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.messages = self.config["messages"]
        self.contacts = self.load_contacts(self.config["contact_file"])
        self.verify_media_paths()

    def load_config(self, config_file):
        if not Path(config_file).is_file():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        try:
            with open(config_file, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in config file: {config_file}")
            raise

    def load_contacts(self, contact_file):
        if not Path(contact_file).is_file():
            raise FileNotFoundError(f"Contact file not found: {contact_file}")

        contacts = []
        try:
            with open(contact_file, "r") as file:
                csv_reader= csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    if len(row) == 0:
                        logging.warning(f"Encountered empty row in contact file")
                        continue
                    contact = row[0]
                    if contact.startswith("+"):
                        contact = contact.replace(' ', '').replace('-', '')
                        contacts.append(contact)
                return contacts
        except Exception as e:
            logging.error(f"Error reading contact file: {e}")
            raise
        
    def verify_media_paths(self):
        if "media_path" in self.messages and self.messages["media_path"]:
            media_path = Path(self.messages["media_path"])
            if not media_path.is_file():
                raise FileNotFoundError(f"Media file not found: {media_path}")
        
        contact_file = self.config["contact_file"]
        if not Path(contact_file).is_file():
            raise FileNotFoundError(f"Contact file not found: {contact_file}")

    def send_message(self, message, contact):
        try:
            target_time = message["time"]

            while datetime.now().strftime("%H:%M") < target_time:
                logging.info(f"Waiting for scheduled time: {target_time}")
                time.sleep(5)

            delay = random.randint(2, 10)
            logging.info(f"Waiting {delay} seconds before sending message")
            time.sleep(delay)

            if "media_path" in message and message["media_path"]:
                logging.info(f"Sending image with caption to {contact}")
                # whatsApp.sendwhats_image(contact, message["media_path"], message["content"])
            else:
                logging.info(f"Sending text message to {contact}")
                # whatsApp.sendwhatmsg_instantly(contact, message["content"])

            logging.info(f"Message sent to {contact}")
        except Exception as e:
            logging.error(f"Error sending message to {contact}: {e}")

    def blast(self):
        for schedule in self.messages["schedule"]:
            send_count = 0
            for contact in tqdm(self.contacts):
                if send_count >= schedule["message_count"]:
                    logging.info(f"Reached limit for this time slot: {schedule['time']}")
                    break

                message = {
                    "content": self.messages["content"],
                    "time": schedule["time"],
                    "media_path": Path(self.messages["media_path"])
                }
                self.send_message(message, contact)
                send_count += 1
                time.sleep(1)

    def run(self):
        self.blast()


if __name__ == "__main__":
    print("Welcome to WhatsUp Blaster!")
    try:
        blaster = WhatsUpBlaster("configs/config.json")
        blaster.run()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
