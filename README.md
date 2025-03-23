# Whatsup Blaster 

WhatsUp Blaster is an automation tool that allows you to schedule WhatsApp messages to be sent at a later time. It supports sending text messages as well as media attachments.

---

 ## ⚠️ Disclaimer ⚠️

**Use this tool at your own risk.** WhatsApp has strict policies regarding automated messaging, and using this tool **may result in account suspension or banning.**

By using Whatsup Blaster, you agree that:

- The author is **not responsible** for any bans, suspensions, or penalties imposed on your WhatsApp account.
- You understand and accept the risks associated with automated messaging.
- You are solely responsible for how you use this tool.

If you do not agree with these terms, **do not use this software.**

---

## Features 🌟

- **Scheduled Messages**: Schedule messages to be sent at a later time.
- **Supports Media**: Send images along with text messages.
- **Configurable Settings**: Adjust message content, timing, and recipients using `config.json`.
- **Random Delays**: Implements delays between messages to reduce the risk of being flagged.
- **Task Persistence**: Uses SQLite3 to handle interruptions and continue unfinished tasks.

## Installation ⚙️ 

To install Whatsup Blaster, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/farithadnan/whatsup-blaster.git
    ```
2. Navigate to the project directory:
    ```bash
    cd whatsup-blaster
    ```
3. Create a virtual environment and install the dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## File & Folder Structure 📁
```bash
whatsup-blaster/
│── configs/
│   ├── config.json          # Main configuration file
│   ├── contacts/            # Folder for storing contact lists
│   │   ├── ws_contact.csv   # Example contact file
│   ├── media/               # Folder for storing images/videos (optional)
│   ├── db/                  # Folder for storing sent log
│── main.py                  # Main script
│── database.py              # Script to handle Database
│── settings.py              # Script to static configuration
│── requirements.txt         # Dependencies list
│── README.md                # Project documentation

```

## Usage 📖

1. **Prepare Contact List:**
    - You can use a script created by ihsanalapsi called [WhatsApp Number Extractor](https://github.com/ihsanalapsi/whatsapp-number-extractor) to extract all numbers in a group. This doesn't cover extracting your saved contacts.
    - Alternatively, you can use an extension called [WA Contacts Extractor](https://chromewebstore.google.com/detail/dcidojkknfgophlmohhpdlmoiegfbkdd?utm_source=item-share-cb) that can extract both saved contacts and all unsaved contacts in your groups.
   - Create a `.csv` file containing phone numbers in the following format:
     ```
     +1234567890
     +0987654321
     ```
   - Save it in the `configs/contacts` folder.
   - Row `1` is a header.
   - All numbers must be put under the `A` column.

2. **Optional: Add Media**  
   - Place images in the `configs/media` folder.

3. **Configure `config.json`**  
   - Modify the file to match your messaging needs:
     ```json
     {
         "messages": {
             "content": "Hello World",
             "media_path": "configs/media/sample.jpg",
             "schedule": [
                 {"time": "09:00", "message_count": 30},
                 {"time": "12:00", "message_count": 30},
                 {"time": "20:00", "message_count": 30}
             ]
         },
         "contact_file": "configs/contacts/ws_contact.csv",
         "database_path": "configs/db/whatsup-blaster.db"
     }
     ```
   - `content`: Message text  
   - `media_path`: Path to an image (leave empty if not sending media)  
   - `schedule`: Define times and message limits  

4. **Run the script:**  
   ```bash
   python main.py
   ```

## Troubleshooting 🛠

- **Missing dependencies?** Run `pip install -r requirements.txt` again.
- **Incorrect contact file?** Ensure numbers are formatted with a `+` at the front and must only contain characters such as spaces, `-`, `number`, and `+`.
- **Message not sending?** Check WhatsApp Web is logged in and active on your default browser.
