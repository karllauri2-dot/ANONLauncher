import json
import os
from dataclasses import dataclass, field, asdict

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.json")


@dataclass
class Settings:
    java_path: str = ""
    min_memory: int = 1024
    max_memory: int = 4096
    game_directory: str = ""
    launch_visibility: str = "visible"
    close_on_launch: bool = False
    version: str = "latest"
    extra_jvm_args: str = ""
    extra_game_args: str = ""
    width: int = 854
    height: int = 480
    fullscreen: bool = False

    def get_game_directory(self) -> str:
        if self.game_directory:
            return self.game_directory
        return os.path.join(os.path.dirname(__file__), "..", ".minecraft")


class SettingsManager:
    def __init__(self):
        self.settings = Settings()
        self._load()

    def _settings_path(self) -> str:
        return os.path.normpath(SETTINGS_FILE)

    def _load(self):
        path = self._settings_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                for key, value in data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)
            except (json.JSONDecodeError, TypeError):
                pass

    def save(self):
        path = self._settings_path()
        with open(path, "w") as f:
            json.dump(asdict(self.settings), f, indent=2)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save()
