import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./revenus.db")
    CORS_ORIGINS: list = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    ADMIN_EMAILS: list = [o.strip() for o in os.getenv("ADMIN_EMAILS", "").split(",") if o.strip()]


settings = Settings()
