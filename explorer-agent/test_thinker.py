"""
测试脚本：手动添加低质量内容并触发Thinker
"""

import requests
import time

API_BASE = "http://localhost:8000/api/v1"

# 模拟低质量内容
LOW_QUALITY_ITEMS = [
    {
        "title": "Very brief paper with minimal content",
        "content": "This is a very short paper with almost no substance. It lacks detailed methodology, experimental results, or meaningful contributions to the field.",
        "source": "http://test.example/low1",
        "type": "paper",
        "original_score": 0.05,
        "tags": ["incomplete", "minimal"]
    },
    {
        "title": "Poorly written research notes",
        "content": "Some random thoughts about AI. Not really a paper. Just notes. Maybe useful later? Contains some keywords: machine learning, neural networks, data science. But no actual research.",
        "source": "http://test.example/low2",
        "type": "paper",
        "original_score": 0.08,
        "tags": ["notes", "informal"]
    },
    {
        "title": "Duplicate ideas paper",
        "content": "This paper discusses standard backpropagation algorithms. It's a basic explanation of gradient descent that has been covered thousands of times before. Nothing new here.",
        "source": "http://test.example/low3",
        "type": "paper",
        "original_score": 0.12,
        "tags": ["basic", "introductory"]
    },
    {
        "title": "Preliminary thoughts on quantum computing",
        "content": "I think quantum computing might be useful for optimization problems. Need to research more. Some key concepts: qubits, superposition, entanglement. Could be interesting for machine learning applications.",
        "source": "http://test.example/low4",
        "type": "paper",
        "original_score": 0.15,
        "tags": ["preliminary", "quantum"]
    },
    {
        "title": "Incomplete experimental results",
        "content": "We ran some experiments. The results were mixed. More analysis needed. Some observations about model performance. Contains keywords: deep learning, optimization, hyperparameters.",
        "source": "http://test.example/low5",
        "type": "paper",
        "original_score": 0.18,
        "tags": ["experimental", "incomplete"]
    },
]

def add_low_quality_content():
    """直接向数据库添加低质量内容"""
    print("正在添加低质量测试内容...")

    # 需要通过后端API或直接数据库操作
    # 这里我们通过触发一个特殊的探索来生成低质量内容
    # 或者直接插入到数据库

    # 由于没有直接API，我们通过检查现有功能来测试
    print("注意：当前系统会将评分 < 0.1 的内容放入低质量池")
    print("由于Arxiv论文质量普遍较高，实际运行中可能不会生成低质量内容")
    print("\n要测试Thinker，可以：")
    print("1. 降低 min_value_score 阈值")
    print("2. 或手动向数据库插入测试数据")

    # 触发探索
    print("\n触发一次探索...")
    response = requests.post(f"{API_BASE}/explore/start", params={"max_iterations": 3, "strategy": "mixed"})
    print(f"探索任务已启动: {response.json()['task_id']}")

    # 等待
    time.sleep(30)

    # 检查统计
    stats = requests.get(f"{API_BASE}/stats").json()
    print(f"\n当前统计:")
    print(f"  总节点: {stats['total_nodes']}")
    print(f"  低质量池: {stats['low_quality_pool_size']}")
    print(f"  未处理: {stats['low_quality_unprocessed']}")

    return stats['low_quality_pool_size'] > 0

def test_thinker_api():
    """测试Thinker API端点"""
    print("\n" + "="*60)
    print("测试Thinker API端点")
    print("="*60)

    # 1. 测试低质量池
    print("\n[1] 测试低质量池API")
    response = requests.get(f"{API_BASE}/thinker/low_quality_pool")
    data = response.json()
    print(f"  低质量池大小: {data['total']}")
    print(f"  未处理: {data['unprocessed']}")

    # 2. 测试洞察API
    print("\n[2] 测试洞察API")
    response = requests.get(f"{API_BASE}/thinker/insights")
    data = response.json()
    print(f"  洞察总数: {data['total']}")

    # 3. 测试思考过程API
    print("\n[3] 测试思考过程API")
    response = requests.get(f"{API_BASE}/thinker/processes")
    data = response.json()
    print(f"  思考会话: {data['total']}")

    # 4. 如果有未处理内容，触发思考
    stats = requests.get(f"{API_BASE}/stats").json()
    if stats['low_quality_unprocessed'] > 0:
        print("\n[4] 触发思考任务")
        response = requests.post(
            f"{API_BASE}/thinker/process",
            params={"batch_size": min(5, stats['low_quality_unprocessed']), "mode": "auto"}
        )
        print(f"  思考任务已启动: {response.json()}")

        # 等待
        print("  等待思考完成...")
        time.sleep(60)

        # 检查结果
        new_stats = requests.get(f"{API_BASE}/stats").json()
        print(f"\n  思考后统计:")
        print(f"    总洞察: {new_stats['total_insights']}")
        print(f"    思考会话: {new_stats['thinking_sessions']}")
    else:
        print("\n[4] 暂无低质量内容，跳过思考测试")

def main():
    print("[TEST] Thinker System Test")
    print("="*60)

    # 测试API
    test_thinker_api()

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n[TIP] To fully test Thinker, you need low-quality content in the pool")
    print("   Since Arxiv papers are generally high-quality, you may need to:")
    print("   1. Lower MIN_VALUE_SCORE in backend/.env")
    print("   2. Or manually insert test data into low_quality_pool table")

if __name__ == "__main__":
    main()
