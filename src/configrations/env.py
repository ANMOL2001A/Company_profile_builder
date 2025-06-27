from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path
from utilities.pathmaker import get_env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(get_env())), env_file_encoding="utf-8"
    )
    linkedin_email: str
    linkedin_password: SecretStr
    scraperapi_key: SecretStr



env = Settings()
