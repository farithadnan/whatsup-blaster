import csv
import time
import random
import logging
import sqlite3
import pywhatkit.whats as kit

from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from settings import ConfigManager

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
        self.db_init()

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
        
    def db_init(self):
        db_path = Path(self.config["database_path"])
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact TEXT UNIQUE,
                status TEXT CHECK(status IN ('pending', 'sent', 'failed')) DEFAULT 'pending'
            )
            """
        )

        self.conn.commit()

    def reset_db(self):
        logging.info("Resetting database")
        self.cursor.execute("DELETE FROM messages")
        self.conn.commit()

    def reset_failed_messages(self):
        logging.info("Resetting failed messages")
        self.cursor.execute("UPDATE messages SET status='pending' WHERE status='failed'")
        self.conn.commit()
    
    def was_message_sent(self, contact):
        self.cursor.execute("SELECT status FROM messages WHERE contact=?", (contact,))
        result = self.cursor.fetchone()
        return result and result[0] == "sent"
    
    def mark_message_status(self, contact, status):
        self.cursor.execute(
            """
            INSERT INTO messages (contact, status) VALUES (?, ?)
            ON CONFLICT(contact) DO UPDATE SET status=excluded.status
            """,
            (contact, status)
        )
        self.conn.commit()

    def send_message(self, message, contact):
        if self.was_message_sent(contact):
            logging.info(f"Skipping message to {contact} as it was already sent")
            return

        try:
            target_time = message["time"]

            while datetime.now().strftime("%H:%M") < target_time:
                logging.info(f"Waiting for scheduled time: {target_time}")
                time.sleep(5)

            delay = random.randint(2, 10)
            logging.info(f"Waiting {delay} seconds before sending message")
            time.sleep(delay)

            if "media_path" in message and message["media_path"]:

                if message["media_path"] == "" or message["media_path"] == None:
                    logging.info(f"Sending image with caption to {contact}")
                    # kit.sendwhats_image(contact, message["media_path"], message["content"])
                else:
                    logging.info(f"Sending text message to {contact}")
                    # kit.sendwhatmsg_instantly(contact, message["content"])

            self.mark_message_status(contact, "sent")
            logging.info(f"Message sent to {contact}")
        except Exception as e:
            logging.error(f"Error sending message to {contact}: {e}")
            self.mark_message_status(contact, "failed")

    def blast(self):
        pending_contacts = [contact for contact in self.contacts if not self.was_message_sent(contact)]

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
                self.send_message(message, contact)
                send_count += 1
                time.sleep(1)

            logging.info(f"Finished schedule for time slot: {schedule['time']}")
            pending_contacts = [c for c in pending_contacts if not self.was_message_sent(c)]

    def run(self):
        self.blast()


if __name__ == "__main__":
    print("Welcome to WhatsUp Blaster!")
    try:
        blaster = WhatsUpBlaster("configs/config.json")
        # blaster.reset_db()               # Uncomment for full reset
        blaster.reset_failed_messages()
        blaster.run()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
