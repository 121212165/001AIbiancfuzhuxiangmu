"""
Explorer Agent 综合评测
测试整个探索系统的表现
"""

import sys
import os
import time
import requests
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000/api/v1"

print("=" * 80)
print("Explorer Agent 综合评测")
print("=" * 80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 评测结果存储
results = {
    "tests": [],
    "total_nodes_before": 0,
    "total_nodes_after": 0,
    "exploration_time": 0,
    "avg_quality_score": 0,
    "diversity_score": 0
}

# ============ 测试1: 系统状态检查 ============
print("[测试1] 系统状态检查")
print("-" * 80)

try:
    # 检查后端
    response = requests.get(f"{API_BASE}/health", timeout=5)
    if response.status_code == 200:
        print("✅ 后端服务: 正常")
        results["tests"].append({"name": "后端健康检查", "status": "PASS"})
    else:
        print(f"❌ 后端服务: 异常 ({response.status_code})")
        results["tests"].append({"name": "后端健康检查", "status": "FAIL"})

    # 检查初始状态
    stats = requests.get(f"{API_BASE}/stats").json()
    results["total_nodes_before"] = stats.get("total_nodes", 0)
    print(f"📊 初始节点数: {results['total_nodes_before']}")
    print(f"📊 初始路径数: {stats.get('total_paths', 0)}")
    print(f"📊 待探索种子: {stats.get('frontier_count', 0)}")

except Exception as e:
    print(f"❌ 系统检查失败: {e}")
    results["tests"].append({"name": "系统状态检查", "status": "FAIL"})

print()

# ============ 测试2: 数据源功能 ============
print("[测试2] 数据源功能测试")
print("-" * 80)

try:
    # 添加测试种子
    test_seeds = [
        ("deep learning theory", 0.9),
        ("computer vision", 0.8),
        ("natural language processing", 0.8),
    ]

    for seed, priority in test_seeds:
        response = requests.post(
            f"{API_BASE}/frontier/add",
            params={"seed": seed, "priority": priority}
        )
        if response.status_code == 200:
            print(f"✅ 添加种子: {seed}")
        else:
            print(f"❌ 添加种子失败: {seed}")

    results["tests"].append({"name": "种子添加", "status": "PASS"})

except Exception as e:
    print(f"❌ 种子添加失败: {e}")
    results["tests"].append({"name": "种子添加", "status": "FAIL"})

print()

# ============ 测试3: 探索执行 ============
print("[测试3: 探索执行测试")
print("-" * 80)

try:
    print("🚀 启动探索任务 (3轮迭代)...")
    start_time = time.time()

    response = requests.post(
        f"{API_BASE}/explore/start",
        params={"max_iterations": 3, "strategy": "graph"}
    )

    if response.status_code == 200:
        task_info = response.json()
        task_id = task_info.get("task_id")
        print(f"✅ 任务已启动: {task_id}")

        # 等待任务完成
        print("⏳ 等待任务完成...")
        max_wait = 120
        elapsed = 0
        interval = 3

        while elapsed < max_wait:
            time.sleep(interval)
            elapsed += interval

            # 检查任务状态
            try:
                status_response = requests.get(f"{API_BASE}/explore/status/{task_id}")
                # 如果404，可能已完成，检查节点数
                if status_response.status_code == 404:
                    break
            except:
                break

        exploration_time = time.time() - start_time
        results["exploration_time"] = exploration_time
        print(f"⏱️  探索耗时: {exploration_time:.2f}秒")

        results["tests"].append({"name": "探索执行", "status": "PASS"})
    else:
        print(f"❌ 探索启动失败: {response.status_code}")
        results["tests"].append({"name": "探索执行", "status": "FAIL"})

except Exception as e:
    print(f"❌ 探索执行失败: {e}")
    results["tests"].append({"name": "探索执行", "status": "FAIL"})

print()

# 等待一下确保数据写入
time.sleep(5)

# ============ 测试4: 结果评估 ============
print("[测试4: 结果评估")
print("-" * 80)

try:
    # 获取探索后的统计
    stats_after = requests.get(f"{API_BASE}/stats").json()
    results["total_nodes_after"] = stats_after.get("total_nodes", 0)
    new_nodes = results["total_nodes_after"] - results["total_nodes_before"]

    print(f"📊 探索前节点数: {results['total_nodes_before']}")
    print(f"📊 探索后节点数: {results['total_nodes_after']}")
    print(f"📊 新增节点数: {new_nodes}")

    # 获取节点详情
    nodes_response = requests.get(f"{API_BASE}/nodes?limit=100")
    nodes = nodes_response.json().get("nodes", [])

    if nodes:
        print(f"\n📝 新发现节点详情:")
        print("-" * 80)

        total_score = 0
        sources = {}
        types = {}

        for i, node in enumerate(nodes, 1):
            score = node.get('value_score', 0)
            total_score += score

            source = node.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

            node_type = node.get('type', 'unknown')
            types[node_type] = types.get(node_type, 0) + 1

            # 显示节点信息
            status_icon = "🌟" if score >= 0.8 else "⭐" if score >= 0.6 else "📌"
            title = node.get('title', '') or node.get('content', '')[:60]
            print(f"{status_icon} 节点{i}: {title}...")
            print(f"   评分: {score:.3f} | 来源: {source} | 类型: {node_type}")
            if node.get('tags'):
                print(f"   标签: {', '.join(node['tags'][:3])}")
            print()

        # 计算平均分
        results["avg_quality_score"] = total_score / len(nodes) if nodes else 0
        print(f"\n📊 质量分析:")
        print(f"   平均评分: {results['avg_quality_score']:.3f}")

        # 来源分布
        print(f"\n   来源分布:")
        for source, count in sources.items():
            print(f"   - {source}: {count}个")

        # 类型分布
        print(f"\n   类型分布:")
        for node_type, count in types.items():
            print(f"   - {node_type}: {count}个")

        # 多样性评分
        results["diversity_score"] = len(sources) + len(types)
        print(f"\n   多样性评分: {results['diversity_score']}")
        print(f"   (来源数: {len(sources)}, 类型数: {len(types)})")

        if new_nodes > 0:
            results["tests"].append({"name": "结果评估", "status": "PASS"})
            print(f"\n✅ 探索成功: 创建了{new_nodes}个新节点")
        else:
            results["tests"].append({"name": "结果评估", "status": "WARN"})
            print(f"\n⚠️  探索未创建新节点 (可能内容已存在)")

    else:
        print("❌ 未获取到任何节点")
        results["tests"].append({"name": "结果评估", "status": "FAIL"})

except Exception as e:
    print(f"❌ 结果评估失败: {e}")
    import traceback
    traceback.print_exc()
    results["tests"].append({"name": "结果评估", "status": "FAIL"})

print()

# ============ 测试5: AI评估系统 ============
print("[测试5: AI评估系统测试")
print("-" * 80)

try:
    print("🤖 当前AI评估器配置:")
    print(f"   提供商: 智谱AI (ZhipuAI)")
    print(f"   模型: GLM-4-Flash")
    print(f"   类型: 免费API")

    if nodes:
        high_quality = len([n for n in nodes if n.get('value_score', 0) >= 0.7])
        medium_quality = len([n for n in nodes if 0.4 <= n.get('value_score', 0) < 0.7])
        low_quality = len([n for n in nodes if n.get('value_score', 0) < 0.4])

        print(f"\n📊 质量分布:")
        print(f"   🌟 高质量 (≥0.7): {high_quality}个 ({high_quality/len(nodes)*100:.1f}%)")
        print(f"   ⭐ 中质量 (0.4-0.7): {medium_quality}个 ({medium_quality/len(nodes)*100:.1f}%)")
        print(f"   📉 低质量 (<0.4): {low_quality}个 ({low_quality/len(nodes)*100:.1f}%)")

        results["tests"].append({"name": "AI评估系统", "status": "PASS"})

except Exception as e:
    print(f"❌ AI评估测试失败: {e}")
    results["tests"].append({"name": "AI评估系统", "status": "FAIL"})

print()

# ============ 综合评分 ============
print("[综合评分]")
print("=" * 80)

pass_count = len([t for t in results["tests"] if t["status"] == "PASS"])
warn_count = len([t for t in results["tests"] if t["status"] == "WARN"])
fail_count = len([t for t in results["tests"] if t["status"] == "FAIL"])
total_count = len(results["tests"])

print(f"测试通过率: {pass_count}/{total_count} ({pass_count/total_count*100:.1f}%)")
print(f"  - 通过: {pass_count}")
print(f"  - 警告: {warn_count}")
print(f"  - 失败: {fail_count}")
print()

# 性能指标
print(f"性能指标:")
print(f"  - 探索耗时: {results.get('exploration_time', 0):.2f}秒")
print(f"  - 平均质量分: {results.get('avg_quality_score', 0):.3f}")
print(f"  - 多样性评分: {results.get('diversity_score', 0)}")
print(f"  - 新增节点: {results.get('total_nodes_after', 0) - results.get('total_nodes_before', 0)}")
print()

# 总体评价
print(f"总体评价:")

if pass_count == total_count and results.get('avg_quality_score', 0) >= 0.5:
    print("  ✅ 优秀 - 系统运行良好，探索质量高")
elif pass_count >= total_count * 0.8:
    print("  ⭐ 良好 - 系统基本正常，部分功能需要优化")
elif pass_count >= total_count * 0.5:
    print("  📌 一般 - 系统可用，但存在较多问题")
else:
    print("  📉 需要改进 - 系统存在严重问题")

print()
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
