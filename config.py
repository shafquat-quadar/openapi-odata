import os
import yaml

class Settings:
    """Load configuration from YAML file and environment variables."""
    def __init__(self, path: str = "config.yaml") -> None:
        cfg = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
        self.mode = os.getenv("MODE", cfg.get("mode", "http"))
        self.port = int(os.getenv("PORT", cfg.get("port", 8000)))
        self.dir = os.getenv("DIR", cfg.get("dir"))
        self.db = os.getenv("DB_FILE", cfg.get("db_file", "shared.sqlite"))
        self.user = os.getenv("ODATA_USER", cfg.get("odata_user"))
        self.password = os.getenv("ODATA_PASS", cfg.get("odata_pass"))

settings = Settings()
