from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # BaseSettings.__init__ resolves each field from env vars / env_file (in that
    # order) using a case-insensitive name match — tavily_api_key <- TAVILY_API_KEY.
    # model_config only tells it where to look; it doesn't hold any values itself.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    tavily_api_key: str
    open_router_api_key: str


settings = Settings()
