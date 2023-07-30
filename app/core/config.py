from typing import Any
from enum import Enum
from pydantic import PostgresDsn, RedisDsn, root_validator
from pydantic_settings import BaseSettings

class Environment(str, Enum):
    DEV = "DEV"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        return self in (self.DEV, self.TESTING)

    @property
    def is_testing(self):
        return self == self.TESTING
    
    @property
    def is_prod(self):
        return self == self.PRODUCTION

class Config(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEV

    APP_NAME: str = "app"
    APP_MODULES: list[str]

    DATABASE_URL: PostgresDsn
    DATABASE_ECHO: bool | None = False
    
    REDIS_URL: RedisDsn

    SITE_DOMAIN: str = "myapp.com"

    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]


settings = Config()

fastapi_config: dict[str, Any] = {
    "title": "App API"
}

# No OpenAPI docs in production
if not settings.ENVIRONMENT.is_debug:
    fastapi_config["openapi_url"] = None