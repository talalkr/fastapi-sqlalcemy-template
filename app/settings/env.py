from pydantic_settings import BaseSettings

class EnvSettings(BaseSettings):
    log_level: str | None = "info"

env_settings = EnvSettings()
