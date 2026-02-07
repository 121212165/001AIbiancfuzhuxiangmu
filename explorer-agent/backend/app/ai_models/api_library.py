"""
API配置管理系统
管理多个AI提供商的API Key和配置
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import os


class APIStatus(Enum):
    """API状态"""
    ACTIVE = "active"           # 正在使用
    BACKUP = "backup"           # 备用
    TESTING = "testing"         # 测试中
    DISABLED = "disabled"       # 已禁用


@dataclass
class APIConfig:
    """API配置"""
    provider: str               # 提供商名称
    api_key: str               # API密钥
    base_url: str              # API基础URL
    status: APIStatus          # 状态
    pricing: str               # 定价类型: free/freemium/paid
    models: List[str]          # 可用模型列表
    rate_limit: Optional[int] = None  # 速率限制（请求/分钟）
    description: str = ""       # 描述

    def is_active(self) -> bool:
        return self.status == APIStatus.ACTIVE

    def is_free(self) -> bool:
        return self.pricing in ["free", "freemium"]


class APIKeyLibrary:
    """API密钥库"""

    def __init__(self):
        self.apis: Dict[str, APIConfig] = {}
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载API配置"""
        env_file = "/app/.env"

        # OpenRouter - 免费模型平台
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            self.apis["openrouter"] = APIConfig(
                provider="openrouter",
                api_key=openrouter_key,
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                status=APIStatus.ACTIVE,
                pricing="freemium",
                models=[
                    "alibaba/tongyi-deepresearch-30b-a3b:free",
                    "xiaomi/mimo-v2-flash:free",
                    "google/gemma-3-27b-it:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                ],
                description="OpenRouter - 多模型聚合平台，有免费额度"
            )

        # SiliconFlow - 硅基流动
        siliconflow_key = os.getenv("SILICONFLOW_API_KEY")
        if siliconflow_key:
            self.apis["siliconflow"] = APIConfig(
                provider="siliconflow",
                api_key=siliconflow_key,
                base_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
                status=APIStatus.ACTIVE,
                pricing="paid",
                models=[
                    "deepseek-ai/DeepSeek-V3",
                    "Qwen/Qwen2.5-72B-Instruct",
                    "Pro/deepseek-ai/DeepSeek-V3",
                ],
                description="硅基流动 - 国产AI模型，中文优化"
            )

        # Anthropic - Claude
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.apis["anthropic"] = APIConfig(
                provider="anthropic",
                api_key=anthropic_key,
                base_url="https://api.anthropic.com",
                status=APIStatus.BACKUP,
                pricing="paid",
                models=[
                    "claude-3-5-sonnet-20241022",
                    "claude-3-haiku-20240307",
                ],
                description="Anthropic - Claude系列"
            )

        # OpenAI - GPT
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.apis["openai"] = APIConfig(
                provider="openai",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                status=APIStatus.BACKUP,
                pricing="paid",
                models=[
                    "gpt-4-turbo-preview",
                    "gpt-4o",
                    "gpt-3.5-turbo",
                ],
                description="OpenAI - GPT系列"
            )

        # 字节火山引擎 - 豆包系列
        volcengine_key = os.getenv("VOLCENGINE_API_KEY")
        if volcengine_key:
            self.apis["volcengine"] = APIConfig(
                provider="volcengine",
                api_key=volcengine_key,
                base_url=os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
                status=APIStatus.ACTIVE,
                pricing="paid",
                models=[
                    "doubao-pro-32k",
                    "doubao-pro-256k",
                    "doubao-lite-32k",
                ],
                description="字节火山引擎 - 豆包系列，中文优化"
            )

        # 阿里云通义千问 - 通义家
        qwen_key = os.getenv("QWEN_API_KEY")
        if qwen_key:
            self.apis["qwen"] = APIConfig(
                provider="qwen",
                api_key=qwen_key,
                base_url=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                status=APIStatus.ACTIVE,
                pricing="paid",
                models=[
                    "qwen-plus",
                    "qwen-turbo",
                    "qwen-max",
                    "qwen-long",
                ],
                description="阿里云通义千问 - 通义家系列，中文优化"
            )

        # 智谱AI (ZhipuAI) - GLM系列
        zhipuai_key = os.getenv("ZHIPUAI_API_KEY")
        if zhipuai_key:
            self.apis["zhipuai"] = APIConfig(
                provider="zhipuai",
                api_key=zhipuai_key,
                base_url=os.getenv("ZHIPUAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
                status=APIStatus.ACTIVE,
                pricing="free",
                models=[
                    "glm-4-flash",
                    "glm-4-plus",
                    "glm-4-0520",
                    "glm-4-air",
                ],
                description="智谱AI - GLM系列，国产免费大模型"
            )

    def add_api(self, config: APIConfig):
        """添加API配置"""
        self.apis[config.provider] = config

    def get_api(self, provider: str) -> Optional[APIConfig]:
        """获取API配置"""
        return self.apis.get(provider)

    def get_active_api(self) -> Optional[APIConfig]:
        """获取当前活跃的API"""
        # 优先使用免费API
        for api in self.apis.values():
            if api.is_active() and api.is_free():
                return api

        # 如果没有免费API，使用第一个活跃API
        for api in self.apis.values():
            if api.is_active():
                return api

        return None

    def list_apis(self, status: Optional[APIStatus] = None) -> List[APIConfig]:
        """列出API，可按状态筛选"""
        apis = list(self.apis.values())

        if status:
            apis = [api for api in apis if api.status == status]

        return apis

    def list_free_apis(self) -> List[APIConfig]:
        """列出免费/Freemium API"""
        return [api for api in self.apis.values() if api.is_free()]

    def list_paid_apis(self) -> List[APIConfig]:
        """列出付费API"""
        return [api for api in self.apis.values() if not api.is_free()]

    def print_api_catalog(self):
        """打印API目录"""
        print("\n" + "=" * 80)
        print("API配置目录")
        print("=" * 80)

        # 活跃的免费API
        print("\n🆓 免费Freemium API (ACTIVE)")
        print("-" * 80)
        free_apis = [api for api in self.apis.values()
                     if api.is_active() and api.is_free()]
        if free_apis:
            for api in free_apis:
                status_icon = "✅" if api.is_active() else "💤"
                print(f"{status_icon} {api.provider.upper()}")
                print(f"   描述: {api.description}")
                print(f"   模型: {', '.join(api.models[:3])}")
                if len(api.models) > 3:
                    print(f"   ... 等共 {len(api.models)} 个模型")
        else:
            print("   (无)")

        # 备用API
        print("\n💰 付费API (BACKUP)")
        print("-" * 80)
        paid_apis = [api for api in self.apis.values() if not api.is_free()]
        if paid_apis:
            for api in paid_apis:
                status_text = "ACTIVE" if api.is_active() else "BACKUP"
                print(f"   {api.provider.upper()} - {status_text}")
                print(f"   描述: {api.description}")
                print(f"   模型: {', '.join(api.models[:2])}")
        else:
            print("   (无)")

        print("\n" + "=" * 80)
        print(f"总计: {len(self.apis)} 个API配置")
        print(f"  免费Freemium: {len(self.list_free_apis())} 个")
        print(f"  付费: {len(self.list_paid_apis())} 个")
        print("=" * 80 + "\n")

    def switch_to_free(self):
        """切换到免费API"""
        print("\n切换到免费API模式...")
        free_api = self.get_active_api()
        if free_api and free_api.is_free():
            print(f"✓ 已切换到 {free_api.provider}")
            return True
        else:
            print("✗ 没有可用的免费API")
            return False

    def switch_to_paid(self):
        """切换到付费API（更强能力）"""
        print("\n切换到付费API模式...")
        paid_api = self.get_api("siliconflow")  # 优先硅基流动
        if not paid_api:
            paid_api = self.get_api("openai")
        if not paid_api:
            paid_api = self.get_api("anthropic")

        if paid_api:
            # 设置为活跃
            for api in self.apis.values():
                if api.is_free():
                    api.status = APIStatus.BACKUP
            paid_api.status = APIStatus.ACTIVE
            print(f"✓ 已切换到 {paid_api.provider}")
            return True
        else:
            print("✗ 没有可用的付费API")
            return False


# 全局实例
api_key_library = APIKeyLibrary()


if __name__ == "__main__":
    # 打印API目录
    api_key_library.print_api_catalog()

    # 获取当前活跃API
    active = api_key_library.get_active_api()
    if active:
        print(f"\n当前活跃API: {active.provider}")
        print(f"定价类型: {active.pricing}")
        print(f"可用模型: {len(active.models)} 个")
