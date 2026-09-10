"""Application configuration."""
import os


class Settings:
    PROJECT_NAME: str = "SARP — Sathapana Agricultural Risk Platform"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-powered agricultural credit early warning for proactive risk management"

    # Database — PostgreSQL + PostGIS for production, SQLite for local dev
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://sarp:sarp123@localhost:5432/sarp",
    )
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "false").lower() == "true"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "sarp-poc-secret-change-in-production")

    # SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # Google Earth Engine
    GEE_PROJECT_ID: str = os.getenv("GEE_PROJECT_ID", "")

    @property
    def effective_database_url(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./sarp.db"
        return self.DATABASE_URL


settings = Settings()
