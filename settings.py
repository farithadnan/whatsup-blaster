import json
import logging
from pathlib import Path

class ConfigManager:
    DEFAULT_CONFIG ={
        "messages": {
            "content": "Hello World",
            "media_path": "",
            "schedule": [{
                "time": "09:00",
                "message_count": 30
            },
            {
                "time": "12:00",
                "message_count": 30
            },
            {
                "time": "20:00",
                "message_count": 30
            }]
        },
        "contact_file": "configs/contacts/ws_contact.csv",
        "database_path": "configs/db/whatsup-blaster.db"
    }

    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.verify_paths()

    def load_config(self):
        """Loads the configuration file or creates a default one if missing."""
        if not self.config_path.is_file():
            logging.warning(f"Config file not found, creating default config at {self.config_path}")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG

        try:
            with open(self.config_path, "r") as file:
                config = json.load(file)

            self.validate_config(config)
            return config

        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Invalid config file: {e}. Using default config.")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
        
    def validate_config(self, config):
        """Ensures required keys exist in the config."""
        required_keys = ["contact_file", "database_path", "messages"]
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required key in config: {key}")

        if "schedule" not in config["messages"]:
            raise KeyError("Missing 'schedule' in messages config.")
        
        if "content" not in config["messages"]:
            raise KeyError("Missing 'content' in messages config.")

    def save_config(self, config):
        """Writes config to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as file:
            json.dump(config, file, indent=4)

    def get(self, key, default=None):
        """Returns a config value by key."""
        return self.config.get(key, default)

    def verify_paths(self):
        """Ensures required directories exist and checks media file."""
        required_dirs = [
            "configs/contacts",
            "configs/db",
            "configs/media"
        ]
        for directory in required_dirs:
            path = Path(directory)
            if not path.exists():
                logging.info(f"Creating directory: {directory}")
                path.mkdir(parents=True, exist_ok=True)

        contact_file = self.config["contact_file"]
        if contact_file and not Path(contact_file).is_file():
            logging.warning(f"Contact file not found: {contact_file}")

        if "media_path" in self.config["messages"] and self.config["messages"]["media_path"]:
            media_path = Path(self.config["messages"]["media_path"])
            if not media_path.is_file():
                logging.warning(f"Media file not found: {media_path}")