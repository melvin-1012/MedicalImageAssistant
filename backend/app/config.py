from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App
    app_name: str = "MediVision AI"
    app_version: str = "1.0.0"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:5500,http://127.0.0.1:5500"

    # Supabase (default placeholders allow local app boot without crashing)
    supabase_url: str = "https://your-project-id.supabase.co"
    supabase_key: Optional[str] = None
    supabase_anon_key: str = "your-anon-key-here"
    supabase_service_role_key: str = "your-service-role-key-here"

    @property
    def effective_anon_key(self) -> str:
        if self.supabase_anon_key and self.supabase_anon_key != "your-anon-key-here":
            return self.supabase_anon_key
        return self.supabase_key or self.supabase_anon_key

    @property
    def effective_service_role_key(self) -> str:
        if self.supabase_service_role_key and self.supabase_service_role_key != "your-service-role-key-here":
            return self.supabase_service_role_key
        return self.supabase_key or self.supabase_service_role_key

    # JWT
    jwt_secret: str = "your-supabase-jwt-secret-here"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Storage
    storage_bucket_images: str = "medical-images"
    storage_bucket_reports: str = "medical-reports"
    storage_bucket_analysis: str = "analysis-results"

    # AI
    vision_ai_enabled: bool = False
    genai_enabled: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
