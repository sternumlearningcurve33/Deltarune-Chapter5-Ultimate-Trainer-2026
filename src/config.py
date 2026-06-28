"""
Configuration module using Pydantic.
"""
from pydantic import BaseModel, Field
import json
from pathlib import Path

class AppConfig(BaseModel):
    theme: str = "dark"
    hotkey_toggle: str = "f1"
    hotkey_exit: str = "f2"
    memory_scan_interval: float = 0.1
    enable_discord_rp: bool = True
    web_dashboard_port: int = 4200

    @classmethod
    def load(cls, path: Path = Path("config.json")) -> "AppConfig":
        if path.exists():
            data = json.loads(path.read_text())
            return cls(**data)
        return cls()

    def save(self, path: Path = Path("config.json")):
        path.write_text(self.model_dump_json(indent=2))

config = AppConfig.load()
