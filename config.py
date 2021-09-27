import pydantic


class Settings(pydantic.BaseSettings):
    database_dsn: str = "sqlite:///:memory:"


settings = Settings()
