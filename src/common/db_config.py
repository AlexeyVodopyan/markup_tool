# thirdparty
from pydantic import BaseSettings, Field
from sqlalchemy.orm import declarative_base


class PostgresSettings(BaseSettings):
    host: str = Field(env="POSTGRES_HOST")
    port: str = Field(env="POSTGRES_PORT")
    db: str = Field(env="POSTGRES_DB")
    user: str = Field(env="POSTGRES_USER")
    password: str = Field(env="POSTGRES_PASSWORD")


pg_settings = PostgresSettings()
Base = declarative_base()
