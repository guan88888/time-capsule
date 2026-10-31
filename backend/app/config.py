"""
配置管理
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# 获取项目根目录（backend目录）
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """应用配置"""
    
    # 火山方舟AI配置
    volcano_ark_api_key: str = ""
    volcano_ark_api_url: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    volcano_ark_model: str = "doubao-seed-1-8-251228"
    
    # AI配置
    ai_max_tokens: int = 500
    ai_temperature: float = 0.7
    ai_enable_thinking: bool = False
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# 全局配置实例
settings = Settings()

# 验证配置
def validate_config():
    """验证必需的配置项"""
    if not settings.volcano_ark_api_key:
        raise ValueError("VOLCANO_ARK_API_KEY 未配置，请在 .env 文件中设置")

# 初始化时验证
try:
    validate_config()
except ValueError as e:
    print(f"⚠️  配置警告: {e}")
    print("提示: 某些AI功能可能无法正常工作")
