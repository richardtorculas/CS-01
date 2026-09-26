from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    email_verification_hours: int = 24
    verification_link_base: str = "ugnay://verify-email"
    brevo_api_key: str = ""
    email_from_address: str = "no-reply@example.com"
    email_from_name: str = "UGNAY"


@lru_cache
def get_settings() -> Settings:
    return Settings()
