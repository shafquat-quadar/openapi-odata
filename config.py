import os
import yaml

class Settings:
    """Load configuration exclusively from a YAML file."""

    def __init__(self, path: str = "config.yaml") -> None:
        cfg = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}

        self.mode = cfg.get("mode", "http")
        self.port = int(cfg.get("port", 8000))
        self.dir = cfg.get("dir")
        self.db = cfg.get("db_file", "shared.sqlite")
        self.user = cfg.get("odata_user")
        self.password = cfg.get("odata_pass")
        self.base_url = cfg.get("base_url")

settings = Settings()
