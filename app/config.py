import yaml
import os

class ConfigLoader:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default