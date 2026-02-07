"""
AI模型配置库
支持多个AI提供商和模型，按付费/免费分类
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PricingType(Enum):
    """定价类型"""
    FREE = "free"           # 完全免费
    FREEMIUM = "freemium"   # 免费额度 + 付费
    PAID = "paid"           # 仅付费


class ProviderType(Enum):
    """提供商类型"""
    OPENROUTER = "openrouter"
    SILICONFLOW = "siliconflow"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    CUSTOM = "custom"


@dataclass
class AIModel:
    """AI模型配置"""
    provider: str
    model_id: str
    display_name: str
    pricing: PricingType
    context_length: int
    description: str
    base_url: Optional[str] = None
    requires_key: bool = True

    def __str__(self):
        pricing_icon = {
            PricingType.FREE: "🆓",
            PricingType.FREEMIUM: "🎁",
            PricingType.PAID: "💰"
        }
        icon = pricing_icon.get(self.pricing, "")
        return f"{icon} {self.display_name} ({self.model_id})"


class AIModelLibrary:
    """AI模型库"""

    def __init__(self):
        self.models: Dict[str, AIModel] = {}
        self._initialize_models()

    def _initialize_models(self):
        """初始化所有可用模型"""

        # ===== OpenRouter 模型 =====
        self.register_model(AIModel(
            provider="openrouter",
            model_id="alibaba/tongyi-deepresearch-30b-a3b:free",
            display_name="阿里通义深度研究",
            pricing=PricingType.FREE,
            context_length=32000,
            description="深度研究专用模型，适合长文本分析",
            base_url="https://openrouter.ai/api/v1",
            requires_key=True
        ))

        self.register_model(AIModel(
            provider="openrouter",
            model_id="xiaomi/mimo-v2-flash:free",
            display_name="小米Mimo V2 Flash",
            pricing=PricingType.FREE,
            context_length=32000,
            description="快速响应模型，适合简单任务",
            base_url="https://openrouter.ai/api/v1",
            requires_key=True
        ))

        self.register_model(AIModel(
            provider="openrouter",
            model_id="google/gemma-3-27b-it:free",
            display_name="Google Gemma 3 27B",
            pricing=PricingType.FREE,
            context_length=128000,
            description="Google开源模型，长上下文",
            base_url="https://openrouter.ai/api/v1",
            requires_key=True
        ))

        self.register_model(AIModel(
            provider="openrouter",
            model_id="meta-llama/llama-3.3-70b-instruct:free",
            display_name="Llama 3.3 70B",
            pricing=PricingType.FREE,
            context_length=131072,
            description="Meta开源，超长上下文",
            base_url="https://openrouter.ai/api/v1",
            requires_key=True
        ))

        # 付费模型
        self.register_model(AIModel(
            provider="openrouter",
            model_id="anthropic/claude-3.5-sonnet",
            display_name="Claude 3.5 Sonnet",
            pricing=PricingType.PAID,
            context_length=200000,
            description="Anthropic最强模型，推理能力强",
            base_url="https://openrouter.ai/api/v1",
            requires_key=True
        ))

        self.register_model(AIModel(
            provider="openrouter",
            model_id="openai/gpt-4o",
            display_name="GPT-4o",
            pricing=PricingType.PAID,
            context_length=128000,
            description="OpenAI最新模型",
            base_url="https://openrouter.ai/api/v1",
            requires_key=True
        ))

        # ===== SiliconFlow 模型 =====
        self.register_model(AIModel(
            provider="siliconflow",
            model_id="deepseek-ai/DeepSeek-V3",
            display_name="DeepSeek V3",
            pricing=PricingType.FREEMIUM,
            context_length=64000,
            description="深度求索V3，中文优化",
            base_url="https://api.siliconflow.cn/v1",
            requires_key=True
        ))

        self.register_model(AIModel(
            provider="siliconflow",
            model_id="Qwen/Qwen2.5-72B-Instruct",
            display_name="Qwen 2.5 72B",
            pricing=PricingType.FREEMIUM,
            context_length=131072,
            description="通义千问2.5，长上下文",
            base_url="https://api.siliconflow.cn/v1",
            requires_key=True
        ))

        # ===== Anthropic 直接API =====
        self.register_model(AIModel(
            provider="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            display_name="Claude 3.5 Sonnet (官方)",
            pricing=PricingType.PAID,
            context_length=200000,
            description="Anthropic官方API",
            base_url="https://api.anthropic.com",
            requires_key=True
        ))

        # ===== OpenAI 直接API =====
        self.register_model(AIModel(
            provider="openai",
            model_id="gpt-4-turbo-preview",
            display_name="GPT-4 Turbo (官方)",
            pricing=PricingType.PAID,
            context_length=128000,
            description="OpenAI官方API",
            base_url="https://api.openai.com/v1",
            requires_key=True
        ))

    def register_model(self, model: AIModel):
        """注册新模型"""
        key = f"{model.provider}/{model.model_id}"
        self.models[key] = model

    def get_model(self, model_id: str, provider: str = "openrouter") -> Optional[AIModel]:
        """获取模型配置"""
        key = f"{provider}/{model_id}"
        return self.models.get(key)

    def list_models(self,
                    pricing: Optional[PricingType] = None,
                    provider: Optional[str] = None) -> List[AIModel]:
        """列出模型，可按定价/提供商筛选"""
        models = list(self.models.values())

        if pricing:
            models = [m for m in models if m.pricing == pricing]

        if provider:
            models = [m for m in models if m.provider == provider]

        return models

    def list_free_models(self) -> List[AIModel]:
        """列出所有免费模型"""
        return self.list_models(pricing=PricingType.FREE)

    def list_paid_models(self) -> List[AIModel]:
        """列出所有付费模型"""
        return [m for m in self.models.values()
                if m.pricing in [PricingType.PAID, PricingType.FREEMIUM]]

    def get_recommended_free_model(self) -> Optional[AIModel]:
        """获取推荐的免费模型（优先阿里通义）"""
        # 优先推荐：阿里通义 > Google Gemma > Llama > 小米
        priority = [
            "alibaba/tongyi-deepresearch-30b-a3b:free",
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "xiaomi/mimo-v2-flash:free"
        ]

        for model_id in priority:
            model = self.get_model(model_id)
            if model and model.pricing == PricingType.FREE:
                return model

        # 如果优先模型都不可用，返回第一个免费模型
        free_models = self.list_free_models()
        return free_models[0] if free_models else None

    def print_catalog(self):
        """打印模型目录"""
        print("\n" + "=" * 80)
        print("AI模型目录")
        print("=" * 80)

        # 免费模型
        print("\n🆓 免费模型 (FREE)")
        print("-" * 80)
        free_models = self.list_free_models()
        for i, model in enumerate(free_models, 1):
            print(f"{i}. {model}")
            print(f"   描述: {model.description}")
            print(f"   上下文: {model.context_length:,} tokens")

        # Freemium模型
        print("\n🎁 Freemium模型 (免费额度)")
        print("-" * 80)
        freemium_models = self.list_models(pricing=PricingType.FREEMIUM)
        for i, model in enumerate(freemium_models, 1):
            print(f"{i}. {model}")
            print(f"   描述: {model.description}")
            print(f"   上下文: {model.context_length:,} tokens")

        # 付费模型
        print("\n💰 付费模型 (PAID)")
        print("-" * 80)
        paid_models = self.list_models(pricing=PricingType.PAID)
        for i, model in enumerate(paid_models, 1):
            print(f"{i}. {model}")
            print(f"   描述: {model.description}")
            print(f"   上下文: {model.context_length:,} tokens")

        print("\n" + "=" * 80)
        print(f"总计: {len(self.models)} 个模型")
        print(f"  免费: {len(free_models)} 个")
        print(f"  Freemium: {len(freemium_models)} 个")
        print(f"  付费: {len(paid_models)} 个")
        print("=" * 80 + "\n")


# 全局实例
ai_model_library = AIModelLibrary()


if __name__ == "__main__":
    # 打印模型目录
    ai_model_library.print_catalog()

    # 获取推荐模型
    recommended = ai_model_library.get_recommended_free_model()
    if recommended:
        print(f"\n推荐免费模型: {recommended}")
