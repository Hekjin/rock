from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CampusBreak API"
    environment: str = "development"
    secret_key: str | None = None
    database_url: str = (
        "postgresql+psycopg://rock_user:local_dev_password@127.0.0.1:5432/rock_db"
    )
    demo_user_email: str = "teacher@demo.kz"

    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "quizai"
    keycloak_client_id: str = "quizai-web"

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"

    @property
    def keycloak_jwks_url(self) -> str:
        return (
            f"{self.keycloak_url}/realms/{self.keycloak_realm}"
            "/protocol/openid-connect/certs"
        )

    @property
    def keycloak_audience(self) -> str:
        return "quizai-api"


settings = Settings()
