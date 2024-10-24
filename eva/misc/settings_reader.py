import configparser
import datetime
from typing import Any, Mapping, Tuple, Type, Union

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from eva.misc.paths import BASE_DIR


def ini_file_settings(_=None) -> Mapping[str, Any]:
    """Read settings from config.ini file"""
    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources
    # Pydantic docs: 'callable should take an instance of the settings class as
    # its sole argument and return a dict.' - but this doesn't seem to work?
    # Therefore, parameter `_: Any`` was replaced by `_=None`
    config = configparser.ConfigParser()
    config.read(BASE_DIR / "config.ini")
    return {
        section: values for section, values in config.items() if section != "DEFAULT"
    }


class BotSettings(BaseModel):
    token: str
    privacy_policy_link: str


class WebhookSettings(BaseModel):
    host: str
    path: str

    @field_validator("host")
    def host_to_url(cls, v: str) -> str:
        if v.startswith("https"):
            return v
        return f"https://{v}"

    @property
    def url(self) -> str:
        if self.host and self.path:
            return f"{self.host}{self.path}"
        return ""


class WebAppSettings(BaseModel):
    host: str
    port: int


class RedisSettings(BaseModel):
    host: str
    port: int = 6379
    db: int
    password: str = ""

    @property
    def connection_uri(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"


class CaptchaSettings(BaseModel):
    duration: Union[int, datetime.timedelta]

    @field_validator("duration")
    def to_timedelta(cls, v: Union[int, datetime.timedelta]) -> datetime.timedelta:
        if isinstance(v, datetime.timedelta):
            return v
        return datetime.timedelta(seconds=v)


class Settings(BaseSettings):
    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#usage
    # If model inherits from BaseSettings, the model initialiser determines the
    # values of fields that are not passed as kwargs by reading from environment.
    bot: BotSettings
    webhook: WebhookSettings
    webapp: WebAppSettings
    redis: RedisSettings
    captcha: CaptchaSettings
    ADMINS: list = [642986667]  # я

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # Mapping[str, Any]
        env_settings: PydanticBaseSettingsSource,  # Mapping[str, Any]
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,  # Mapping[str, Any]
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            ini_file_settings,
            env_settings,
            file_secret_settings,
        )
