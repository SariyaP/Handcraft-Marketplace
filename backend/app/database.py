from functools import lru_cache

from pydantic import computed_field
from sqlalchemy import inspect
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Settings(BaseSettings):
    app_name: str = "Handcraft Marketplace API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "handcraft_marketplace"
    mysql_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.mysql_echo,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from app.models import load_all_models

    load_all_models()
    Base.metadata.create_all(bind=engine)
    _migrate_maker_profiles()
    _migrate_commissions()


def _migrate_maker_profiles() -> None:
    inspector = inspect(engine)
    if "maker_profiles" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("maker_profiles")}
    statements = []

    if "specialization" not in existing_columns:
        statements.append("ALTER TABLE maker_profiles ADD COLUMN specialization VARCHAR(150) NULL")
    if "profile_image_url" not in existing_columns:
        statements.append("ALTER TABLE maker_profiles ADD COLUMN profile_image_url VARCHAR(255) NULL")
    if "verification_status" not in existing_columns:
        statements.append(
            "ALTER TABLE maker_profiles ADD COLUMN verification_status VARCHAR(50) NOT NULL DEFAULT 'unverified'"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def _migrate_commissions() -> None:
    inspector = inspect(engine)
    if "commissions" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("commissions")}
    statements = []

    if "customization_notes" not in existing_columns:
        statements.append("ALTER TABLE commissions ADD COLUMN customization_notes TEXT NULL")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
