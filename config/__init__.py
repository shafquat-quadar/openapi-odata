import os
from dotenv import load_dotenv


class Settings:
    """Load configuration from a .env file or environment."""

    def __init__(self) -> None:
        load_dotenv()
        self.dir = os.getenv("DIR")
        self.db = os.getenv("DB_FILE", "shared.sqlite")
        self.user = os.getenv("ODATA_USER")
        self.password = os.getenv("ODATA_PASS")


settings = Settings()
