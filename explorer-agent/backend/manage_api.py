"""
API和AI模型管理脚本
用于查看、添加、切换API配置
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_models.library import ai_model_library, PricingType
from app.ai_models.api_library import api_key_library, APIStatus


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 80)
    print("API & AI 模型管理系统")
    print("=" * 80)
    print("1. 查看API配置目录")
    print("2. 查看AI模型目录")
    print("3. 切换到免费API")
    print("4. 切换到付费API")
    print("5. 测试当前API")
    print("6. 查看API使用统计")
    print("0. 退出")
    print("=" * 80)


def show_api_catalog():
    """显示API目录"""
    api_key_library.print_api_catalog()


def show_model_catalog():
    """显示模型目录"""
    ai_model_library.print_catalog()


def switch_to_free():
    """切换到免费API"""
    success = api_key_library.switch_to_free()
    if success:
        api = api_key_library.get_active_api()
        print(f"\n✓ 已切换到免费API: {api.provider}")
        print(f"  描述: {api.description}")
        print(f"  模型数: {len(api.models)}")
    else:
        print("\n✗ 切换失败，没有可用的免费API")


def switch_to_paid():
    """切换到付费API"""
    success = api_key_library.switch_to_paid()
    if success:
        api = api_key_library.get_active_api()
        print(f"\n✓ 已切换到付费API: {api.provider}")
        print(f"  描述: {api.description}")
        print(f"  模型数: {len(api.models)}")
    else:
        print("\n✗ 切换失败，没有可用的付费API")


def test_current_api():
    """测试当前API"""
    print("\n测试当前活跃API...")
    api = api_key_library.get_active_api()

    if not api:
        print("✗ 没有活跃的API配置")
        return

    print(f"\n提供商: {api.provider}")
    print(f"API URL: {api.base_url}")
    print(f"状态: {api.status.value}")
    print(f"定价: {api.pricing}")
    print(f"密钥: {api.api_key[:20]}...{api.api_key[-10:]}")
    print(f"\n可用模型 ({len(api.models)}):")
    for i, model in enumerate(api.models[:5], 1):
        print(f"  {i}. {model}")
    if len(api.models) > 5:
        print(f"  ... 等共 {len(api.models)} 个模型")

    # 测试评估器
    print(f"\n测试AI评估...")
    try:
        from app.services.evaluator import ValueEvaluator
        evaluator = ValueEvaluator()
        print(f"✓ 评估器初始化成功")
        print(f"  使用提供商: {evaluator.provider}")
        print(f"  使用模型: {evaluator.model}")

        # 简单测试
        test_content = "Test content for evaluation."
        import time
        start = time.time()
        score = evaluator.evaluate(test_content, [])
        elapsed = time.time() - start

        print(f"\n✓ API测试成功!")
        print(f"  评分: {score}")
        print(f"  响应时间: {elapsed:.1f}秒")

    except Exception as e:
        print(f"✗ API测试失败: {e}")


def show_statistics():
    """显示使用统计"""
    print("\n" + "=" * 80)
    print("API配置统计")
    print("=" * 80)

    all_apis = api_key_library.apis
    free_apis = api_key_library.list_free_apis()
    paid_apis = api_key_library.list_paid_apis()

    print(f"\n总API数: {len(all_apis)}")
    print(f"  免费Freemium: {len(free_apis)} 个")
    print(f"  付费: {len(paid_apis)} 个")

    all_models = ai_model_library.models
    free_models = ai_model_library.list_free_models()
    paid_models = ai_model_library.list_paid_models()

    print(f"\n总模型数: {len(all_models)}")
    print(f"  免费: {len(free_models)} 个")
    print(f"  Freemium: {len(ai_model_library.list_models(pricing=PricingType.FREEMIUM))} 个")
    print(f"  付费: {len(paid_models)} 个")

    # 当前活跃
    active_api = api_key_library.get_active_api()
    if active_api:
        print(f"\n当前活跃API: {active_api.provider}")
        print(f"  类型: {'免费' if active_api.is_free() else '付费'}")
        print(f"  状态: {active_api.status.value}")

    print("\n" + "=" * 80)


def main():
    """主函数"""
    while True:
        print_menu()
        choice = input("\n请选择操作 (0-6): ").strip()

        if choice == "0":
            print("\n退出系统")
            break
        elif choice == "1":
            show_api_catalog()
        elif choice == "2":
            show_model_catalog()
        elif choice == "3":
            switch_to_free()
        elif choice == "4":
            switch_to_paid()
        elif choice == "5":
            test_current_api()
        elif choice == "6":
            show_statistics()
        else:
            print("\n无效选择，请重试")

        input("\n按Enter继续...")


if __name__ == "__main__":
    main()
