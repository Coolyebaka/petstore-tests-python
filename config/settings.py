import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_URL: str = os.getenv("PETSTORE_BASE_URL", "https://petstore.swagger.io/v2")

    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    CONNECT_TIMEOUT: int = int(os.getenv("CONNECT_TIMEOUT", "10"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_REQUESTS: bool = os.getenv("LOG_REQUESTS", "true").lower() == "true"
    LOG_RESPONSES: bool = os.getenv("LOG_RESPONSES", "true").lower() == "true"

    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "0.1"))

    @classmethod
    def get_base_url(cls) -> str:
        return cls.BASE_URL

    @classmethod
    def get_timeout(cls) -> tuple[int, int]:
        return (cls.CONNECT_TIMEOUT, cls.REQUEST_TIMEOUT)
