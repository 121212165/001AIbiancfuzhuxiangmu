"""Application configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://explorer:password@localhost:5432/explorer_db"
    postgres_user: str = "explorer"
    postgres_password: str = "password"
    postgres_db: str = "explorer_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI APIs
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "xiaomi/mimo-v2-flash:free"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    siliconflow_model: str = "deepseek-ai/DeepSeek-V3"
    volcengine_api_key: str = ""
    volcengine_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    volcengine_model: str = "doubao-pro-32k"
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"
    zhipuai_api_key: str = ""
    zhipuai_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    zhipuai_model: str = "glm-4-flash"

    # Google Search
    google_api_key: str = ""
    google_search_engine_id: str = ""

    # App
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Exploration
    exploration_interval_minutes: int = 30
    max_explorations_per_run: int = 5
    min_value_score: float = 0.3

    # Thinker (low-quality content processing)
    thinking_batch_size: int = 10  # Number of items to process per run
    thinking_max_pool_size: int = 200  # Maximum items in low-quality pool
    thinking_interval_minutes: int = 60  # Run thinking every N minutes

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
