import os
from typing import Optional
try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Database Configuration
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "3306"))
    database_user: str = os.getenv("DATABASE_USER", "root")
    database_password: str = os.getenv("DATABASE_PASSWORD", "")
    database_name: str = os.getenv("DATABASE_NAME", "demo")
    
    # AI Model Configuration
    sql_model_url: str = os.getenv("SQL_MODEL_URL", "http://model-runner.docker.internal:12434")
    sql_model_name: str = os.getenv("SQL_MODEL_NAME", "hf.co/unsloth/gemma-3-270m-it-GGUF")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Data Path Configuration
    data_path: str = os.getenv("DATA_PATH", "/app/data")
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    @property
    def database_url(self) -> str:
        """Construct database URL for AWS RDS"""
        return f"mysql+pymysql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
