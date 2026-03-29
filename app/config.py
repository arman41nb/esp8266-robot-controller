import json
import os

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.defaults = {
            "esp_ws_url": "ws://192.168.4.1:81",
            "esp_ip": "192.168.4.1",
            "udp_port": 12345,
            "theme": {
                "white": "#FFFFFF",
                "purple": "#C742F0",
                "purple_dark": "#9828D9",
                "purple_light": "#EEE6FF",
                "glass_white": "#FFFFFFE0"
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = self.defaults.copy()
            self.save()

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

config = Config()