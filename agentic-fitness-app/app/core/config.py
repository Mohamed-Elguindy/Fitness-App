from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "dummy_testing_key_for_ci"
    NEON_DATABASE_URL: str = "sqlite:///./test.db"  # Fallback to local sqlite for dev if missing

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
