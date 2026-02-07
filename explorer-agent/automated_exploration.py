"""
自动化探索系统 - 每日自动运行
每天自动探索Arxiv论文，生成报告并保存
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ 配置部分 ============
API_BASE = "http://localhost:8000/api/v1"

# 探索配置
EXPLORATION_CONFIG = {
    "max_iterations": 20,          # 每次探索迭代次数
    "strategy": "mixed",            # 探索策略
    "daily_rounds": 3,              # 每天探索轮数
    "min_new_nodes_target": 5,      # 目标新节点数
}

# 思考者配置
THINKER_CONFIG = {
    "enable_thinking": True,        # 是否启用思考者
    "batch_size": 10,               # 每次处理数量
    "mode": "auto",                 # 思考模式
    "run_after_exploration": True,  # 探索后自动运行
}

# 报告配置
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# ============ 核心功能 ============

class DailyExplorationSystem:
    """每日自动探索系统"""

    def __init__(self):
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "rounds_completed": 0,
            "nodes_before": 0,
            "nodes_after": 0,
            "new_nodes": [],
            "exploration_time": 0,
            "thinking_time": 0,
            "insights_created": 0,
            "errors": [],
        }

    def check_system_health(self):
        """检查系统健康状态"""
        print("\n[1] 检查系统健康状态...")

        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务正常")
                return True
            else:
                print(f"❌ 后端服务异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到后端: {e}")
            return False

    def get_initial_stats(self):
        """获取初始统计"""
        print("\n[2] 获取初始状态...")

        try:
            response = requests.get(f"{API_BASE}/stats")
            stats = response.json()

            self.stats["nodes_before"] = stats.get("total_nodes", 0)

            print(f"📊 当前节点数: {self.stats['nodes_before']}")
            print(f"📊 当前路径数: {stats.get('total_paths', 0)}")
            print(f"📊 种子池大小: {stats.get('frontier_count', 0)}")
            print(f"📊 平均评分: {stats.get('avg_value_score', 0):.2f}")

            return True
        except Exception as e:
            print(f"❌ 获取统计失败: {e}")
            return False

    def run_exploration_round(self, round_num):
        """运行一轮探索"""
        print(f"\n[3.{round_num}] 启动第{round_num}轮探索...")

        try:
            start_time = time.time()

            response = requests.post(
                f"{API_BASE}/explore/start",
                params={
                    "max_iterations": EXPLORATION_CONFIG["max_iterations"],
                    "strategy": EXPLORATION_CONFIG["strategy"]
                }
            )

            if response.status_code != 200:
                raise Exception(f"探索启动失败: {response.status_code}")

            task_info = response.json()
            task_id = task_info.get("task_id")
            print(f"✅ 任务已启动: {task_id}")

            # 等待任务完成
            max_wait = 300  # 最多等待5分钟
            elapsed = 0
            interval = 5

            while elapsed < max_wait:
                time.sleep(interval)
                elapsed += interval

                # 检查是否有新节点
                stats = requests.get(f"{API_BASE}/stats").json()
                current_nodes = stats.get("total_nodes", 0)

                if current_nodes > self.stats["nodes_before"] + len(self.stats["new_nodes"]):
                    new_count = current_nodes - self.stats["nodes_before"] - len(self.stats["new_nodes"])
                    print(f"   进度: 已发现 {new_count} 个新节点...")

                # 尝试检查任务状态
                try:
                    status_response = requests.get(f"{API_BASE}/explore/status/{task_id}")
                    if status_response.status_code == 404:
                        # 任务已完成
                        break
                except:
                    pass

            exploration_time = time.time() - start_time
            self.stats["exploration_time"] += exploration_time
            self.stats["rounds_completed"] += 1

            print(f"✅ 第{round_num}轮探索完成 (耗时: {exploration_time:.1f}秒)")
            return True

        except Exception as e:
            error_msg = f"第{round_num}轮探索失败: {e}"
            print(f"❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return False

    def collect_new_nodes(self):
        """收集新发现的节点"""
        print("\n[4] 收集新发现的节点...")

        try:
            response = requests.get(f"{API_BASE}/nodes?limit=100")
            data = response.json()
            all_nodes = data.get("nodes", [])

            # 只获取比初始数量多的节点
            if len(all_nodes) > self.stats["nodes_before"]:
                new_nodes = all_nodes[:(len(all_nodes) - self.stats["nodes_before"])]
                self.stats["new_nodes"] = new_nodes
                self.stats["nodes_after"] = len(all_nodes)

                print(f"✅ 收集到 {len(new_nodes)} 个新节点:")
                for i, node in enumerate(new_nodes, 1):
                    score = node.get('value_score', 0)
                    title = node.get('title', '')[:70]
                    print(f"   {i}. [{score:.2f}] {title}...")
            else:
                print("⚠️  未发现新节点")

            return True
        except Exception as e:
            print(f"❌ 收集节点失败: {e}")
            return False

    def run_thinking(self):
        """运行思考者处理低质量内容"""
        if not THINKER_CONFIG["enable_thinking"]:
            print("\n[4.5] 思考者未启用，跳过")
            return True

        print("\n[4.5] 运行思考者...")

        try:
            # 检查是否有未处理的低质量内容
            stats_response = requests.get(f"{API_BASE}/stats")
            stats = stats_response.json()
            unprocessed = stats.get("low_quality_unprocessed", 0)

            if unprocessed == 0:
                print("   暂无未处理的低质量内容")
                return True

            print(f"   发现 {unprocessed} 个未处理项目，启动思考...")

            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/thinker/process",
                params={
                    "batch_size": min(THINKER_CONFIG["batch_size"], unprocessed),
                    "mode": THINKER_CONFIG["mode"]
                }
            )

            if response.status_code != 200:
                raise Exception(f"思考启动失败: {response.status_code}")

            task_info = response.json()
            task_id = task_info.get("task_id")
            print(f"   ✅ 思考任务已启动: {task_id}")

            # 等待任务完成
            max_wait = 600  # 最多等待10分钟
            elapsed = 0
            interval = 10

            while elapsed < max_wait:
                time.sleep(interval)
                elapsed += interval

                # 检查任务状态
                try:
                    status_response = requests.get(f"{API_BASE}/thinker/status/{task_id}")
                    if status_response.status_code == 404:
                        break
                    status_data = status_response.json()
                    if status_data.get("state") == "SUCCESS":
                        break
                except:
                    pass

            thinking_time = time.time() - start_time
            self.stats["thinking_time"] = thinking_time

            # 获取新洞察数
            new_stats = requests.get(f"{API_BASE}/stats").json()
            self.stats["insights_created"] = new_stats.get("total_insights", 0)

            print(f"   ✅ 思考完成 (耗时: {thinking_time:.1f}秒)")
            print(f"   总洞察数: {self.stats['insights_created']}")
            return True

        except Exception as e:
            error_msg = f"思考处理失败: {e}"
            print(f"   ❌ {error_msg}")
            self.stats["errors"].append(error_msg)
            return False

    def generate_quality_report(self):
        """生成质量评估报告"""
        print("\n[5] 生成质量评估报告...")

        try:
            # 获取最新统计
            stats = requests.get(f"{API_BASE}/stats").json()
            nodes_response = requests.get(f"{API_BASE}/nodes?limit=1000")
            all_nodes = nodes_response.json().get("nodes", [])

            # 质量分析
            high_value = len([n for n in all_nodes if n.get('value_score', 0) >= 0.7])
            medium_value = len([n for n in all_nodes if 0.5 <= n.get('value_score', 0) < 0.7])
            low_value = len([n for n in all_nodes if n.get('value_score', 0) < 0.5])

            # 来源分布
            sources = {}
            for node in all_nodes:
                source = node.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1

            # 生成报告
            report = {
                "report_date": datetime.now().isoformat(),
                "summary": {
                    "total_nodes": stats.get("total_nodes", 0),
                    "new_nodes_today": len(self.stats["new_nodes"]),
                    "total_paths": stats.get("total_paths", 0),
                    "frontier_seeds": stats.get("frontier_count", 0),
                    "avg_value_score": stats.get("avg_value_score", 0),
                },
                "quality_distribution": {
                    "high_value (≥0.7)": high_value,
                    "medium_value (0.5-0.7)": medium_value,
                    "low_value (<0.5)": low_value,
                },
                "source_distribution": sources,
                "new_nodes": self.stats["new_nodes"],
                "exploration_stats": {
                    "rounds_completed": self.stats["rounds_completed"],
                    "total_time": self.stats["exploration_time"],
                    "errors": self.stats["errors"],
                },
                # Thinker stats
                "thinker_stats": {
                    "low_quality_pool_size": stats.get("low_quality_pool_size", 0),
                    "low_quality_unprocessed": stats.get("low_quality_unprocessed", 0),
                    "total_insights": stats.get("total_insights", 0),
                    "thinking_sessions": stats.get("thinking_sessions", 0),
                    "avg_insight_value": stats.get("avg_insight_value", 0),
                    "thinking_time": self.stats.get("thinking_time", 0),
                    "insights_created_today": self.stats.get("insights_created", 0),
                }
            }

            # 保存报告
            report_file = REPORT_DIR / f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"✅ 报告已保存: {report_file}")
            print(f"\n   📊 今日总结:")
            print(f"   - 新节点: {len(self.stats['new_nodes'])} 个")
            print(f"   - 总节点: {stats.get('total_nodes', 0)} 个")
            print(f"   - 平均分: {stats.get('avg_value_score', 0):.2f}")
            print(f"   - 探索轮数: {self.stats['rounds_completed']}")
            print(f"   - 探索耗时: {self.stats['exploration_time']:.1f}秒")

            # Thinker summary
            if THINKER_CONFIG["enable_thinking"]:
                print(f"   🤔 思考者:")
                print(f"   - 低质量池: {stats.get('low_quality_pool_size', 0)} (未处理: {stats.get('low_quality_unprocessed', 0)})")
                print(f"   - 总洞察: {stats.get('total_insights', 0)} 个")
                print(f"   - 思考耗时: {self.stats.get('thinking_time', 0):.1f}秒")

            # 生成Markdown报告
            self._generate_markdown_report(report, report_file)

            return report_file

        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return None

    def _generate_markdown_report(self, report, json_file):
        """生成Markdown格式的报告"""
        md_file = json_file.with_suffix('.md')

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 每日探索报告\n\n")
            f.write(f"**日期**: {report['report_date']}\n\n")

            f.write(f"## 📈 今日总结\n\n")
            f.write(f"- **新发现节点**: {report['summary']['new_nodes_today']} 个\n")
            f.write(f"- **总节点数**: {report['summary']['total_nodes']} 个\n")
            f.write(f"- **总路径数**: {report['summary']['total_paths']} 条\n")
            f.write(f"- **种子池大小**: {report['summary']['frontier_seeds']} 个\n")
            f.write(f"- **平均评分**: {report['summary']['avg_value_score']:.2f}\n")
            f.write(f"- **探索轮数**: {report['exploration_stats']['rounds_completed']}\n")
            f.write(f"- **总耗时**: {report['exploration_stats']['total_time']:.1f} 秒\n\n")

            # Thinker section
            if 'thinker_stats' in report and report['thinker_stats'].get('total_insights', 0) > 0:
                f.write(f"## 🤔 思考者统计\n\n")
                f.write(f"- **低质量池大小**: {report['thinker_stats']['low_quality_pool_size']} 个\n")
                f.write(f"- **未处理**: {report['thinker_stats']['low_quality_unprocessed']} 个\n")
                f.write(f"- **总洞察数**: {report['thinker_stats']['total_insights']} 个\n")
                f.write(f"- **思考会话**: {report['thinker_stats']['thinking_sessions']} 次\n")
                f.write(f"- **洞察平均分**: {report['thinker_stats']['avg_insight_value']:.2f}\n")
                f.write(f"- **思考耗时**: {report['thinker_stats']['thinking_time']:.1f} 秒\n\n")

            f.write(f"## 🎯 质量分布\n\n")
            for level, count in report['quality_distribution'].items():
                percentage = count / report['summary']['total_nodes'] * 100 if report['summary']['total_nodes'] > 0 else 0
                f.write(f"- **{level}**: {count} 个 ({percentage:.1f}%)\n")

            f.write(f"\n## 🔬 今日新发现\n\n")
            if report['new_nodes']:
                for i, node in enumerate(report['new_nodes'], 1):
                    score = node.get('value_score', 0)
                    title = node.get('title', 'N/A')
                    source = node.get('source', 'N/A')
                    tags = node.get('tags', [])
                    content = node.get('content', '')[:200]

                    f.write(f"### {i}. [{score:.2f}] {title}\n\n")
                    f.write(f"- **来源**: {source}\n")
                    f.write(f"- **标签**: {', '.join(tags)}\n")
                    f.write(f"- **摘要**: {content}...\n\n")
            else:
                f.write(f"⚠️ 今日未发现新节点\n\n")

            if report['exploration_stats']['errors']:
                f.write(f"## ⚠️ 错误日志\n\n")
                for error in report['exploration_stats']['errors']:
                    f.write(f"- {error}\n")

        print(f"✅ Markdown报告已保存: {md_file}")


# ============ 主程序 ============

def main():
    """主程序"""
    print("=" * 80)
    print("🚀 每日自动探索系统")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"配置: {EXPLORATION_CONFIG['daily_rounds']}轮探索, 每轮{EXPLORATION_CONFIG['max_iterations']}次迭代")
    if THINKER_CONFIG['enable_thinking']:
        print(f"思考者: 启用 (批次: {THINKER_CONFIG['batch_size']}, 模式: {THINKER_CONFIG['mode']})")
    print()

    system = DailyExplorationSystem()

    # 1. 健康检查
    if not system.check_system_health():
        print("\n❌ 系统不健康，退出")
        return

    # 2. 获取初始状态
    if not system.get_initial_stats():
        return

    # 3. 运行探索
    for round_num in range(1, EXPLORATION_CONFIG["daily_rounds"] + 1):
        if not system.run_exploration_round(round_num):
            print(f"⚠️ 第{round_num}轮探索失败，继续下一轮...")

        # 轮次之间休息
        if round_num < EXPLORATION_CONFIG["daily_rounds"]:
            print("   休息10秒...")
            time.sleep(10)

    # 4. 收集新节点
    system.collect_new_nodes()

    # 4.5. 运行思考者
    system.run_thinking()

    # 5. 生成报告
    report_file = system.generate_quality_report()

    print()
    print("=" * 80)
    print("✅ 每日探索完成!")
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"新节点: {len(system.stats['new_nodes'])} 个")
    print(f"报告位置: {report_file}")
    print()


if __name__ == "__main__":
    main()
