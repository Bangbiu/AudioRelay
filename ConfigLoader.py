import json


class AppConfig:
    def __init__(self, path):
        with open(path, 'r') as file:
            info = json.load(file)
            self.audio_file_paths = info["audio_file_paths"]
            self.log_dir_paths = info["log_dir_paths"]


config = AppConfig("./config/config.json")
