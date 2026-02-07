"""
Test Qwen API Integration
测试 Qwen API 是否正确配置和运行
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.evaluator import ValueEvaluator
from app.core.config import get_settings

print("=" * 60)
print("Qwen API Integration Test")
print("=" * 60)

# 1. Check settings
settings = get_settings()
print("\n[1] Environment Settings:")
print(f"  QWEN_API_KEY: {'***' + settings.qwen_api_key[-4:] if settings.qwen_api_key else 'NOT SET'}")
print(f"  QWEN_BASE_URL: {settings.qwen_base_url}")
print(f"  QWEN_MODEL: {settings.qwen_model}")

# 2. Initialize evaluator
evaluator = ValueEvaluator()
print("\n[2] Evaluator Status:")
print(f"  Active Provider: {evaluator.provider}")
print(f"  Model: {evaluator.model if hasattr(evaluator, 'model') else 'N/A'}")

# Check if Qwen is selected
if evaluator.provider == "qwen":
    print("  Status: [OK] Qwen API is active!")
elif evaluator.provider == "siliconflow":
    print("  Status: [INFO] SiliconFlow has higher priority than Qwen")
elif evaluator.provider == "volcengine":
    print("  Status: [INFO] VolcEngine has higher priority than Qwen")
else:
    print(f"  Status: [INFO] Using {evaluator.provider} instead")

# 3. Test evaluation
test_content = """
Transformer architecture revolutionized natural language processing by enabling
parallel processing of sequences through self-attention mechanisms. This allows
models to capture long-range dependencies more effectively than RNNs.
"""

print("\n[3] Testing Content Evaluation:")
print(f"  Test content length: {len(test_content)} characters")
print("  Calling AI API...")

try:
    score = evaluator.evaluate(test_content, existing_nodes=[])
    print(f"  Evaluation Score: {score}")
    if 0.0 <= score <= 1.0:
        print("  Status: [OK] Score in valid range!")
    else:
        print(f"  Status: [WARN] Score out of range [0.0, 1.0]")
except Exception as e:
    print(f"  Status: [FAIL] Error: {e}")

# 4. Test tag extraction
print("\n[4] Testing Tag Extraction:")
try:
    tags = evaluator.extract_tags(test_content)
    print(f"  Tags: {tags}")
    if tags:
        print(f"  Status: [OK] Extracted {len(tags)} tags")
    else:
        print("  Status: [WARN] No tags extracted")
except Exception as e:
    print(f"  Status: [FAIL] Error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
