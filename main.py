import csv
import time
import random
import logging
import sqlite3
import pywhatkit.whats as kit

from tqdm import tqdm
from pathlib import Path
from datetime import datetime, timedelta
from settings import ConfigManager
from database import DatabaseManager

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

class WhatsUpBlaster:
    def __init__(self, config_file):
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.config
        self.messages = self.config["messages"]
        self.contacts = self.load_contacts(self.config["contact_file"])
        self.db = DatabaseManager(self.config["database_path"])

    def load_contacts(self, contact_file):
        if not Path(contact_file).is_file():
            raise FileNotFoundError(f"Contact file not found: {contact_file}")

        contacts = set()
        try:
            with open(contact_file, "r") as file:
                csv_reader= csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    if len(row) == 0:
                        logging.warning(f"Encountered empty row in contact file")
                        continue
                    contact = row[0].replace(' ', '').replace('-', '')
                    if contact.startswith("+"):
                        contacts.add(contact)

                logging.info(f"Loaded {len(contacts)} contacts from file")
                return list(contacts)
        except Exception as e:
            logging.error(f"Error reading contact file: {e}")
            raise
        
    def send_message(self, message, contact, dry_run=False):
        if self.db.was_message_sent(contact):
            logging.info(f"Skipping message to {contact} as it was already sent")
            return

        try:
            now = datetime.now()
            target_hour, target_minute = map(int, message["time"].split(":"))
            target_datetime = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

            # If target time is in the past, schedule it for tomorrow
            if target_datetime < now:
                target_datetime += timedelta(days=1)

            while datetime.now() < target_datetime:
                logging.info(f"Waiting for scheduled time until: {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(5)

            delay = random.randint(2, 10)
            logging.info(f"Waiting {delay} seconds before sending message")
            time.sleep(delay)

            if dry_run:
                logging.info(f"[DRY RUN] Message to {contact}: {message['content']}")
                return

            if message.get("media_path"):
                if message["media_path"] == "" or message["media_path"] == None:
                    logging.info(f"Sending image with caption to {contact}")
                    # kit.sendwhats_image(contact, message["media_path"], message["content"])
                else:
                    logging.info(f"Sending text message to {contact}")
                    # kit.sendwhatmsg_instantly(contact, message["content"])

            self.db.mark_message_status(contact, "sent")
            logging.info(f"Message sent to {contact}")

        except sqlite3.OperationalError as e:
            logging.error(f"Database error: {e}")
            self.db.mark_message_status(contact, "failed")
        except Exception as e:
            logging.error(f"Error sending message to {contact}: {e}")
            self.db.mark_message_status(contact, "failed")

    def blast(self, dry_run=False):
        self.db.cursor.execute("SELECT contact FROM messages WHERE status != 'sent'")
        sent_contacts = {row[0] for row in self.db.cursor.fetchall()}
        pending_contacts = list(set(self.contacts) - sent_contacts)

        for schedule in self.messages["schedule"]:
            send_count = 0
            if not pending_contacts:
                logging.info("No pending contacts left to send messages.")
                break

            for contact in tqdm(pending_contacts[:schedule["message_count"]]):
                message = {
                    "content": self.messages["content"],
                    "time": schedule["time"],
                    "media_path": Path(self.messages["media_path"])
                }
                self.send_message(message, contact, dry_run)
                send_count += 1
                time.sleep(1)

            logging.info(f"Finished schedule for time slot: {schedule['time']}")
            pending_contacts = [c for c in pending_contacts if not self.db.was_message_sent(c)]

    def run(self):
        self.blast(dry_run=True)


if __name__ == "__main__":
    print("Welcome to WhatsUp Blaster!")
    try:
        blaster = WhatsUpBlaster("configs/config.json")
        # blaster.db.reset_db()               # Uncomment for full reset
        blaster.db.reset_failed_messages()
        blaster.run()
        blaster.db.close()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
