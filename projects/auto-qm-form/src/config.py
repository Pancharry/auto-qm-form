# src/config.py
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Optional
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# 採用 APP_ENV 決定預設 env 檔路徑
def _default_env_file() -> str:
    app_env = os.getenv("APP_ENV", "dev").lower()
    if app_env in ("test", "ci"):
        return ".env.test"
    return ".env"

class Settings(BaseSettings):
    # 核心應用設定
    APP_NAME: str = "AutoQM"
    APP_ENV: str = "dev"  # dev / test / prod

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    # 資料庫：預設 SQLite，會被 .env / 環境變數 覆蓋
    DATABASE_URL: str = "sqlite:///./local.db"
    # 測試專用可選
    TEST_DATABASE_URL: Optional[str] = None

    # 檔案/LLM
    FILE_STORAGE_ROOT: str = "./data/files"
    LLM_PROVIDER: str = "stub"
    LLM_MODEL: str = "gpt-4o-mini"
    MAX_LLM_TOKENS: int = 2000

    # 其他可能參數（保留擴充）
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=_default_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def effective_database_url(self) -> str:
        """
        回傳實際使用的 DB URL（依優先序）：
        1. APP_ENV 為 test/ci 且 TEST_DATABASE_URL 存在
        2. DATABASE_URL
        3. （理論上不會 None）預設值
        """
        if self.APP_ENV.lower() in ("test", "ci") and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL

def _compute_settings(
    *,
    override_db_url: Optional[str] = None,
    force_env_file: Optional[str] = None,
) -> Settings:
    """
    產生設定實例，可在需要時局部覆蓋（例如指令列工具 / 單元測試）。
    """
    env: dict[str, str] = {}
    if override_db_url:
        # 直接覆蓋環境變數輸入，優先於 .env
        env["DATABASE_URL"] = override_db_url

    if force_env_file:
        # 建立暫時模型繞過原本 model_config 的 env_file
        class _AltSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=force_env_file,
                env_file_encoding="utf-8",
                extra="ignore",
                case_sensitive=False,
            )
        return _AltSettings(**env)
    else:
        return Settings(**env)

@lru_cache
def get_settings(
    override_db_url: Optional[str] = None,
    force_env_file: Optional[str] = None,
) -> Settings:
    """
    快取後的設定取得。對大多數情境使用 get_settings() 即可。
    注意：若傳入參數將破壞快取（因為函式簽章含參數），
    建議在測試時直接 new Settings() 或加上 force_env_file。
    """
    return _compute_settings(
        override_db_url=override_db_url,
        force_env_file=force_env_file,
    )

# 供一般匯入使用
settings = get_settings()

if __name__ == "__main__":
    s = settings
    print("APP_ENV=", s.APP_ENV)
    print("env file chosen =", _default_env_file())
    print("DATABASE_URL =", s.DATABASE_URL)
    print("effective DB =", s.effective_database_url)
