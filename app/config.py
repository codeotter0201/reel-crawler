from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    從 .env 文件讀取應用程序設置，並使用 Pydantic 進行類型驗證和管理。
    """

    # 使用者認證
    USER_EMAIL: str
    USER_PASSWORD: str

    # 驅動程序路徑設置
    WEB_DRIVER_PATH: str = "user_data"  # 預設值，與 .env 中的值相同

    # 配置 Pydantic 設置
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )
