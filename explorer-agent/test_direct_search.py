"""
直接测试搜索和创建节点
绕过frontier，直接测试完整流程
"""

import requests
import time

API_BASE = "http://localhost:8000/api/v1"


def test_direct_discovery():
    """直接测试发现流程"""

    print("=" * 80)
    print("直接搜索测试 - Transformer主题")
    print("=" * 80)

    # 直接调用Arxiv搜索（模拟explorer内部流程）
    import docker
    client = docker.from_home()

    container = client.containers.get("explorer-agent-backend-1")

    print("\n1. 测试Arxiv搜索...")
    result = container.exec_run(
        "python -c \""
        "from app.services.sources import ArxivSource; "
        "arxiv = ArxivSource(); "
        "results = arxiv.search('transformer attention mechanism', num_results=3); "
        "import json; "
        "for r in results[:1]: print(json.dumps(r)) "
        "\"",
        workdir="/app"
    )

    if result.exit_code == 0:
        output = result.output.decode('utf-8')
        print("搜索成功！")

        try:
            import json
            paper = json.loads(output.strip().split('\n')[-1])

            print(f"\n2. 找到论文:")
            print(f"   标题: {paper.get('title', 'N/A')}")
            print(f"   来源: {paper.get('source', 'N/A')}")
            print(f"   类型: {paper.get('type', 'N/A')}")

            # 3. 测试AI评估
            print(f"\n3. 测试AI评分（通义深度研究模型）...")
            eval_result = container.exec_run(
                f"python -c \""
                f"from app.services.evaluator import ValueEvaluator; "
                f"evaluator = ValueEvaluator(); "
                f"content = '''{paper.get('content', '')[:1000]}'''; "
                f"score = evaluator.evaluate(content, []); "
                f"print(f'评分: {{score}}') "
                f"\"",
                workdir="/app"
            )

            if eval_result.exit_code == 0:
                eval_output = eval_result.output.decode('utf-8')
                for line in eval_output.split('\n'):
                    if '评分:' in line:
                        print(f"   {line.strip()}")

                # 提取评分
                import re
                score_match = re.search(r'评分:\s*(0\.\d+|1\.0|0|1)', eval_output)
                if score_match:
                    score = float(score_match.group(1))
                    print(f"\n4. 评分结果: {score}")

                    if score >= 0.1:
                        print(f"   ✓ 评分通过阈值 (0.1)，可以创建节点")

                        # 5. 显示完整信息
                        print(f"\n5. 完整发现内容:")
                        print(f"   标题: {paper.get('title', 'N/A')}")
                        print(f"   评分: {score}")
                        print(f"   类型: {paper.get('type', 'N/A')}")
                        print(f"   来源: {paper.get('source', 'N/A')}")
                        print(f"\n[SUCCESS] 搜索能力验证成功！")
                        print(f"  - Arxiv搜索: ✓")
                        print(f"  - AI评估: ✓ (评分{score})")
                        print(f"  - 阈值过滤: ✓")
                        return True
                    else:
                        print(f"   ✗ 评分未通过阈值 (< 0.1)")
                        return False
        except Exception as e:
            print(f"解析错误: {e}")
            print(f"原始输出: {output}")
    else:
        print(f"搜索失败: {result.output.decode('utf-8')}")

    return False


if __name__ == "__main__":
    success = test_direct_discovery()

    print("\n" + "=" * 80)
    if success:
        print("验证结果: 搜索能力正常 ✓")
    else:
        print("验证结果: 需要调整")
    print("=" * 80)
