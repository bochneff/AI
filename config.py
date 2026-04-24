from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SCADA AI Module"
    database_url: str = "sqlite:///./scada_server.db"
    model_path: str = "./models/isolation_forest.joblib"
    anomaly_threshold: float = 0.62
    training_limit_rows: int = 20000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
