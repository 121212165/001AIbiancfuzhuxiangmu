"""
快速查看API配置
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.ai_models.library import ai_model_library
from app.ai_models.api_library import api_key_library

print("\n" + "█" * 80)
print("█" + " " * 78 + "█")
print("█" + "  当前API配置总览".center(78) + "█")
print("█" + " " * 78 + "█")
print("█" * 80)

# 1. API配置
print("\n【API配置】")
print("-" * 80)
active_api = api_key_library.get_active_api()
if active_api:
    print(f"活跃API: {active_api.provider}")
    print(f"  描述: {active_api.description}")
    print(f"  类型: {'🆓 免费' if active_api.is_free() else '💰 付费'}")
    print(f"  状态: ✅ {active_api.status.value}")
    print(f"  API URL: {active_api.base_url}")
    print(f"  模型数: {len(active_api.models)}")
else:
    print("⚠️  未配置活跃API")

# 2. 所有API
print(f"\n【所有API配置】")
print("-" * 80)
for provider, api in api_key_library.apis.items():
    status_icon = "✅" if api.is_active() else "💤"
    pricing_icon = "🆓" if api.is_free() else "💰"
    print(f"{status_icon} {pricing_icon} {provider}")
    print(f"   {api.description}")

# 3. 模型统计
print(f"\n【AI模型统计】")
print("-" * 80)
free_models = ai_model_library.list_free_models()
paid_models = ai_model_library.list_paid_models()

print(f"总模型数: {len(ai_model_library.models)}")
print(f"  🆓 免费: {len(free_models)} 个")
print(f"  💰 付费: {len(paid_models)} 个")

# 4. 推荐模型
recommended = ai_model_library.get_recommended_free_model()
if recommended:
    print(f"\n【推荐免费模型】")
    print("-" * 80)
    print(f"✓ {recommended.display_name}")
    print(f"  模型ID: {recommended.model_id}")
    print(f"  上下文: {recommended.context_length:,} tokens")
    print(f"  描述: {recommended.description}")

print("\n" + "=" * 80 + "\n")
