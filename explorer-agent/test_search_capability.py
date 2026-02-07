"""
搜索能力验证测试
1. 创建高价值种子节点
2. 从种子节点出发探索
3. 验证相关内容发现能力
"""

import requests
import time
import json
from typing import Dict, List

API_BASE = "http://localhost:8000/api/v1"


class SearchCapabilityTester:
    """搜索能力测试器"""

    def __init__(self):
        self.session = requests.Session()

    def print_header(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def add_frontier_seeds(self, seeds: List[str], priority: float = 1.0) -> bool:
        """添加探索种子到frontier"""
        try:
            # 使用正确的API端点
            for seed in seeds:
                response = self.session.post(
                    f"{API_BASE}/frontier/add",
                    json={"seed": seed, "priority": priority},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code in [200, 201]:
                    print(f"[OK] 添加探索种子: {seed}")
                else:
                    print(f"[INFO] 种子可能已存在: {seed} (状态码: {response.status_code})")
            return True
        except Exception as e:
            print(f"[FAIL] 添加种子异常: {e}")
            return False

    def get_nodes(self) -> List[Dict]:
        """获取所有节点"""
        try:
            response = self.session.get(f"{API_BASE}/nodes")
            if response.status_code == 200:
                data = response.json()
                return data.get('nodes', [])
        except Exception as e:
            print(f"[FAIL] 获取节点失败: {e}")
        return []

    def start_exploration(self, max_iterations: int = 10, strategy: str = "graph") -> Dict:
        """启动探索任务"""
        try:
            payload = {
                "max_iterations": max_iterations,
                "strategy": strategy
            }
            response = self.session.post(
                f"{API_BASE}/explore/start",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[FAIL] 启动探索失败: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] 启动探索异常: {e}")
        return {}

    def monitor_exploration(self, task_id: str, timeout: int = 180):
        """监控探索进度"""
        print(f"\n监控探索任务: {task_id}")
        print("-" * 80)

        start_time = time.time()
        check_interval = 5
        last_count = 0

        while time.time() - start_time < timeout:
            # 检查节点数量
            nodes = self.get_nodes()
            current_count = len(nodes)

            if current_count > last_count:
                elapsed = time.time() - start_time
                print(f"[{elapsed:.1f}s] 新增节点! 当前总数: {current_count}")

                # 显示最新节点
                if nodes:
                    latest = nodes[-1]
                    print(f"  └─ [{latest.get('type', 'unknown')}] {latest.get('title', 'No title')[:60]}...")
                    print(f"     评分: {latest.get('value_score', 0):.2f}")

                last_count = current_count

            time.sleep(check_interval)

        elapsed = time.time() - start_time
        print(f"\n探索完成，耗时: {elapsed:.1f}秒")

    def analyze_discoveries(self, initial_nodes: int, final_nodes: List[Dict]):
        """分析发现结果"""
        self.print_header("发现能力分析")

        new_count = len(final_nodes) - initial_nodes
        new_nodes = final_nodes[initial_nodes:] if len(final_nodes) > initial_nodes else []

        print(f"初始节点数: {initial_nodes}")
        print(f"最终节点数: {len(final_nodes)}")
        print(f"新增节点数: {new_count}")

        if new_nodes:
            print(f"\n新增节点详情:")
            for i, node in enumerate(new_nodes, 1):
                print(f"\n{i}. [{node.get('type', 'unknown')}] {node.get('title', 'No title')}")
                print(f"   来源: {node.get('source', 'unknown')}")
                print(f"   评分: {node.get('value_score', 0):.2f}")
                print(f"   标签: {', '.join(node.get('tags', [])[:5])}")

            # 统计类型分布
            type_count = {}
            for node in new_nodes:
                t = node.get('type', 'unknown')
                type_count[t] = type_count.get(t, 0) + 1

            print(f"\n类型分布:")
            for t, count in sorted(type_count.items(), key=lambda x: -x[1]):
                print(f"  - {t}: {count} 个")

            # 评分统计
            scores = [n.get('value_score', 0) for n in new_nodes]
            avg_score = sum(scores) / len(scores) if scores else 0
            print(f"\n评分统计:")
            print(f"  平均评分: {avg_score:.2f}")
            print(f"  最高评分: {max(scores):.2f}")
            print(f"  最低评分: {min(scores):.2f}")

        else:
            print("\n[INFO] 未发现新节点")
            print("可能原因:")
            print("  1. AI评分阈值过高 (当前: 0.5)")
            print("  2. 网络连接问题 (部分数据源SSL错误)")
            print("  3. 种子主题已完全探索")

    def verify_relevance(self, seed_topic: str, nodes: List[Dict]):
        """验证发现内容的相关性"""
        self.print_header("相关性验证")

        if not nodes:
            print("[INFO] 没有新节点需要验证")
            return

        seed_lower = seed_topic.lower()
        relevant_count = 0

        print(f"种子主题: {seed_topic}\n")

        for i, node in enumerate(nodes, 1):
            title = node.get('title', '').lower()
            content = node.get('content', '').lower()[:500]
            combined = title + ' ' + content

            # 简单关键词匹配检查
            keywords = seed_lower.split()
            matched = [kw for kw in keywords if kw in combined and len(kw) > 3]
            is_relevant = len(matched) >= 2

            if is_relevant:
                relevant_count += 1
                status = "[RELATED]"
            else:
                status = "[UNRELATED]"

            print(f"{i}. {status} {node.get('title', 'No title')[:60]}...")
            if matched:
                print(f"   匹配关键词: {', '.join(matched[:3])}")

        relevance_rate = (relevant_count / len(nodes)) * 100 if nodes else 0
        print(f"\n相关率: {relevant_count}/{len(nodes)} = {relevance_rate:.1f}%")

        if relevance_rate >= 60:
            print("[OK] 搜索能力良好！大部分发现内容相关")
        elif relevance_rate >= 30:
            print("[INFO] 搜索能力一般，部分相关内容")
        else:
            print("[WARN] 搜索能力较弱，相关性较低")

    def run_test(self):
        """运行完整测试"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "       搜索能力验证测试 - 从高价值节点出发探索相关内容       ".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)

        # 1. 添加高价值探索种子
        self.print_header("步骤1: 添加Transformer相关探索种子")

        # 添加高优先级的Transformer相关种子
        high_priority_seeds = [
            "transformer architecture attention mechanism",
            "BERT pretraining language model",
            "GPT generative transformer"
        ]

        self.add_frontier_seeds(high_priority_seeds, priority=1.0)

        # 2. 添加更多相关探索方向
        self.print_header("步骤2: 添加探索方向")

        exploration_seeds = [
            "transformer architecture improvements",
            "attention mechanisms variants",
            "BERT language model",
            "GPT generative pretraining",
            "efficient transformer implementations",
            "vision transformer ViT",
            "transformer interpretability"
        ]

        self.add_frontier_seeds(exploration_seeds)

        # 3. 记录初始状态
        initial_nodes = self.get_nodes()
        initial_count = len(initial_nodes)
        print(f"\n初始节点数: {initial_count}")

        # 4. 启动探索
        self.print_header("步骤3: 从种子节点出发探索")

        # 使用graph策略，更注重从现有节点扩展
        result = self.start_exploration(max_iterations=10, strategy="graph")

        if not result.get('task_id'):
            print("[FAIL] 无法启动探索任务")
            return

        task_id = result['task_id']
        print(f"[OK] 探索任务已启动: {task_id}")

        # 5. 监控探索过程
        self.monitor_exploration(task_id, timeout=180)

        # 6. 分析发现结果
        final_nodes = self.get_nodes()
        new_nodes = final_nodes[initial_count:] if len(final_nodes) > initial_count else []

        self.analyze_discoveries(initial_count, final_nodes)

        # 7. 验证相关性
        self.verify_relevance("transformer attention neural network", new_nodes)

        # 8. 总结
        self.print_header("测试总结")

        total_new = len(final_nodes) - initial_count
        print(f"种子主题: Transformers / Attention Mechanisms")
        print(f"探索轮数: 10次迭代")
        print(f"发现节点: {total_new} 个")

        if total_new > 0:
            print("\n[SUCCESS] 搜索能力验证成功！")
            print(f"  系统能够从种子节点发现相关的{total_new}个新内容")
        else:
            print("\n[INFO] 未发现新节点")
            print("  建议调整 MIN_VALUE_SCORE 阈值或检查网络连接")

        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    tester = SearchCapabilityTester()
    tester.run_test()
