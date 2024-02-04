from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    echo_sql: bool = True
    debug_logs: bool = True
    test: bool = False
    project_name: str = "ECG API"
    oauth_token_secret: str = "my_dev_secret"  # openssl rand -hex 32
    auth_algorithm: str = "HS256"
    auth_access_token_expire_minutes: int = 30
    cors_allow_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    auth_password_min_length: int = 4

    max_signal_buffer: int = 50


settings = Settings()  # type: ignore
