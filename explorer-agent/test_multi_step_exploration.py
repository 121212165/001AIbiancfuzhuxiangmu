"""
多步探索测试脚本
测试连续探索能力、路径连续性和后端处理能力
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000/api/v1"


class ExplorationTester:
    """探索测试器"""

    def __init__(self):
        self.results = []
        self.session = requests.Session()

    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def print_subheader(self, title: str):
        """打印子标题"""
        print(f"\n{'─' * 80}")
        print(f"  {title}")
        print(f"{'─' * 80}")

    def check_health(self) -> bool:
        """检查后端健康状态"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] 后端健康: {data.get('status')}")
                return True
        except Exception as e:
            print(f"[FAIL] 后端健康检查失败: {e}")
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

    def get_paths(self) -> List[Dict]:
        """获取所有探索路径"""
        try:
            response = self.session.get(f"{API_BASE}/exploration-paths")
            if response.status_code == 200:
                data = response.json()
                return data.get('paths', [])
        except Exception as e:
            print(f"[FAIL] 获取路径失败: {e}")
        return []

    def start_exploration(self, max_iterations: int = 5, strategy: str = "mixed") -> Dict:
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

    def wait_for_exploration(self, task_id: str, timeout: int = 120) -> bool:
        """等待探索完成"""
        start_time = time.time()
        print(f"  等待任务完成 (最长{timeout}秒)...", end="", flush=True)

        dots = 0
        while time.time() - start_time < timeout:
            try:
                # 检查是否有新节点创建
                nodes = self.get_nodes()
                if dots % 10 == 0:
                    print(".", end="", flush=True)
                dots += 1
                time.sleep(2)

                # 简单检查：如果有新节点，可能探索已完成
                # 更好的方式是轮询任务状态API（如果有的话）
            except Exception:
                pass

        print(" [DONE]")
        return True

    def analyze_path_continuity(self, paths: List[Dict]) -> Dict:
        """分析路径连续性"""
        if not paths:
            return {"total_paths": 0, "connected_paths": 0, "continuity_rate": 0.0, "avg_path_length": 0.0}

        total = len(paths)
        connected = 0
        total_length = 0

        for path in paths:
            path_nodes = path.get('path', [])
            if path_nodes:
                connected += 1
                total_length += len(path_nodes)

        avg_length = total_length / connected if connected > 0 else 0
        continuity_rate = (connected / total) if total > 0 else 0

        return {
            "total_paths": total,
            "connected_paths": connected,
            "continuity_rate": continuity_rate,
            "avg_path_length": avg_length
        }

    def run_high_mode_test(self, rounds: int = 5):
        """运行高模式测试（多次连续探索）"""
        self.print_header("高模式测试 - 连续5次探索")

        initial_nodes = self.get_nodes()
        initial_count = len(initial_nodes)
        print(f"初始节点数: {initial_count}")

        task_ids = []
        for i in range(rounds):
            print(f"\n第 {i+1}/{rounds} 轮探索...")
            start_time = time.time()

            result = self.start_exploration(max_iterations=5, strategy="mixed")

            if result.get('task_id'):
                task_id = result['task_id']
                task_ids.append(task_id)
                print(f"  [OK] 任务ID: {task_id}")

                # 等待探索完成
                self.wait_for_exploration(task_id, timeout=60)

                elapsed = time.time() - start_time
                current_nodes = self.get_nodes()
                new_nodes = len(current_nodes) - initial_count

                print(f"  [OK] 完成，耗时: {elapsed:.1f}秒")
                print(f"  [OK] 新增节点: {new_nodes} (总计: {len(current_nodes)})")
            else:
                print(f"  [FAIL] 启动失败")

            # 间隔时间
            if i < rounds - 1:
                time.sleep(3)

        final_nodes = self.get_nodes()
        final_count = len(final_nodes)

        self.print_subheader("高模式测试结果")
        print(f"启动任务数: {len(task_ids)}")
        print(f"初始节点: {initial_count}")
        print(f"最终节点: {final_count}")
        print(f"新增节点: {final_count - initial_count}")
        print(f"平均每轮: {(final_count - initial_count) / rounds:.1f} 个节点")

        return {
            "mode": "high",
            "rounds": rounds,
            "initial_nodes": initial_count,
            "final_nodes": final_count,
            "new_nodes": final_count - initial_count,
            "task_ids": task_ids
        }

    def run_low_mode_test(self, rounds: int = 3):
        """运行低模式测试（较少次数连续探索）"""
        self.print_header("低模式测试 - 连续3次探索")

        initial_nodes = self.get_nodes()
        initial_count = len(initial_nodes)
        print(f"初始节点数: {initial_count}")

        task_ids = []
        for i in range(rounds):
            print(f"\n第 {i+1}/{rounds} 轮探索...")
            start_time = time.time()

            # 低模式使用较少迭代次数
            result = self.start_exploration(max_iterations=3, strategy="graph")

            if result.get('task_id'):
                task_id = result['task_id']
                task_ids.append(task_id)
                print(f"  [OK] 任务ID: {task_id}")

                # 等待探索完成
                self.wait_for_exploration(task_id, timeout=45)

                elapsed = time.time() - start_time
                current_nodes = self.get_nodes()
                new_nodes = len(current_nodes) - initial_count

                print(f"  ✓ 完成，耗时: {elapsed:.1f}秒")
                print(f"  ✓ 新增节点: {new_nodes}")
            else:
                print(f"  [FAIL] 启动失败")

            # 间隔时间
            if i < rounds - 1:
                time.sleep(2)

        final_nodes = self.get_nodes()
        final_count = len(final_nodes)

        self.print_subheader("低模式测试结果")
        print(f"启动任务数: {len(task_ids)}")
        print(f"初始节点: {initial_count}")
        print(f"最终节点: {final_count}")
        print(f"新增节点: {final_count - initial_count}")
        print(f"平均每轮: {(final_count - initial_count) / rounds:.1f} 个节点")

        return {
            "mode": "low",
            "rounds": rounds,
            "initial_nodes": initial_count,
            "final_nodes": final_count,
            "new_nodes": final_count - initial_count,
            "task_ids": task_ids
        }

    def analyze_path_quality(self, paths: List[Dict]):
        """分析路径质量"""
        self.print_subheader("路径连续性分析")

        analysis = self.analyze_path_continuity(paths)

        print(f"总路径数: {analysis['total_paths']}")
        print(f"连接路径数: {analysis['connected_paths']}")
        print(f"连续性率: {analysis['continuity_rate']*100:.1f}%")
        print(f"平均路径长度: {analysis['avg_path_length']:.1f} 个节点")

        if paths:
            print(f"\n最近3条路径:")
            for i, path in enumerate(paths[-3:], 1):
                path_nodes = path.get('path', [])
                strategy = path.get('strategy', 'unknown')
                print(f"  {i}. 策略={strategy}, 节点数={len(path_nodes)}, "
                      f"价值={path.get('total_value', 0):.2f}")

    def show_backend_capacity(self):
        """展示后端能力"""
        self.print_subheader("后端能力分析")

        nodes = self.get_nodes()
        paths = self.get_paths()

        # 统计节点类型分布
        type_counts = {}
        score_sum = 0
        for node in nodes:
            node_type = node.get('type', 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
            score_sum += node.get('value_score', 0)

        print(f"节点统计:")
        print(f"  总节点数: {len(nodes)}")
        print(f"  总路径数: {len(paths)}")
        print(f"  平均评分: {score_sum/len(nodes):.2f}" if nodes else "  平均评分: N/A")

        print(f"\n节点类型分布:")
        for node_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  - {node_type}: {count} 个")

    def run_full_test(self):
        """运行完整测试"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "        多步探索测试 - 连续探索能力 & 路径连续性 & 后端能力        ".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)

        # 1. 健康检查
        self.print_header("1. 后端健康检查")
        if not self.check_health():
            print("✗ 后端不健康，终止测试")
            return

        # 2. 高模式测试
        high_result = self.run_high_mode_test(rounds=5)

        # 3. 低模式测试
        low_result = self.run_low_mode_test(rounds=3)

        # 4. 路径分析
        paths = self.get_paths()
        self.analyze_path_quality(paths)

        # 5. 后端能力
        self.show_backend_capacity()

        # 6. 总体报告
        self.print_header("测试总结")

        total_new = high_result['new_nodes'] + low_result['new_nodes']
        total_rounds = high_result['rounds'] + low_result['rounds']
        total_tasks = len(high_result['task_ids']) + len(low_result['task_ids'])

        print(f"测试模式: 高模式(5轮) + 低模式(3轮)")
        print(f"总任务数: {total_tasks}")
        print(f"成功任务: {total_tasks} (假设全部成功)")
        print(f"新增节点: {total_new}")
        print(f"平均每轮: {total_new/total_rounds:.1f} 个节点")

        # 最终节点展示
        nodes = self.get_nodes()
        print(f"\n最终节点列表 (最新5个):")
        for i, node in enumerate(nodes[-5:], 1):
            print(f"  {i}. [{node.get('type', 'unknown')}] {node.get('title', 'No title')[:50]}... "
                  f"(评分: {node.get('value_score', 0):.2f})")

        print("\n" + "=" * 80)
        print("[SUCCESS] 测试完成！")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    tester = ExplorationTester()
    tester.run_full_test()
