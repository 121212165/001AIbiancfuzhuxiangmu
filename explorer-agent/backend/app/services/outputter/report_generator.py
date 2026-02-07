"""
Report Generator for Outputter Agent
"""
from typing import Dict, List, Any
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Report generator

    Generates daily reports, weekly digests, and insight briefs
    """

    def __init__(self):
        pass

    def generate_daily_report(self, data: Dict[str, Any]) -> str:
        """
        Generate daily report

        Args:
            data: Organizer output data

        Returns:
            str: Daily report in markdown format
        """
        metrics = data.get("knowledge_graph", {}).get("metrics", {})
        topics = data.get("topics", {}).get("clusters", [])
        trends = data.get("trends", {})
        questions = data.get("questions", {}).get("questions", [])

        report_lines = [
            f"# 知识探索日报 - {date.today().strftime('%Y-%m-%d')}",
            "",
            "## 📈 今日数据",
            f"- 新节点: {metrics.get('nodes_processed', 0)} 个",
            f"- 知识图谱节点: {metrics.get('graph_nodes', 0)} 个",
            f"- 知识图谱边: {metrics.get('graph_edges', 0)} 条",
            f"- 主题聚类: {metrics.get('topics_found', 0)} 个",
            f"- 时间线事件: {metrics.get('timeline_events', 0)} 个",
            f"- 趋势识别: {metrics.get('trends_identified', 0)} 个",
            f"- 研究问题: {metrics.get('questions_found', 0)} 个",
            "",
            "## 🔥 今日主题聚类",
        ]

        # Add top clusters
        for i, cluster in enumerate(topics[:5], 1):
            report_lines.extend([
                f"### {i}. {cluster.get('name', 'Unnamed')}",
                f"- 包含项目: {cluster.get('item_count', 0)} 个",
                f"- 置信度: {cluster.get('confidence', 0):.2f}",
                ""
            ])

        # Add trends
        report_lines.extend([
            "## 📊 趋势分析",
        ])

        if trends.get("rising"):
            report_lines.append("### 🔼 上升趋势")
            for keyword in trends["rising"][:5]:
                report_lines.append(f"- {keyword}")
            report_lines.append("")

        if trends.get("stable"):
            report_lines.append("### ➡️ 稳定趋势")
            for keyword in trends["stable"][:5]:
                report_lines.append(f"- {keyword}")
            report_lines.append("")

        # Add questions
        report_lines.extend([
            "## 💡 研究问题",
        ])

        for i, question in enumerate(questions[:3], 1):
            report_lines.extend([
                f"### {i}. {question.get('question', 'N/A')}",
                f"- 类型: {question.get('type', 'N/A')}",
                f"- 重要性: {question.get('importance', 'N/A')}",
                ""
            ])

        report_lines.extend([
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        return "\n".join(report_lines)

    def generate_weekly_digest(self, data: Dict[str, Any]) -> str:
        """
        Generate weekly digest

        Args:
            data: Organizer output data

        Returns:
            str: Weekly digest in markdown format
        """
        # For MVP, weekly digest is similar to daily report
        # In full implementation, would aggregate data over a week
        week_num = date.today().isocalendar()[1]

        report_lines = [
            f"# 本周知识总结 - Week {week_num}",
            "",
            "## 📊 本周概览",
            "",
            "本周的探索发现已经整合到知识图谱中。",
            "详细内容请查看每日报告。",
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ]

        return "\n".join(report_lines)

    def generate_insight_briefs(self, data: Dict[str, Any]) -> List[str]:
        """
        Generate insight briefs

        Args:
            data: Organizer output data

        Returns:
            List[str]: List of insight briefs
        """
        questions = data.get("questions", {}).get("questions", [])
        briefs = []

        for i, question in enumerate(questions[:5], 1):
            brief = f"""# 洞察简报 #{i}

## 问题
{question.get('question', 'N/A')}

## 类型
{question.get('type', 'N/A')}

## 重要性
{question.get('importance', 'N/A')}

## 建议探索方向
{question.get('suggested_exploration', 'N/A')}

---
*生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            briefs.append(brief)

        return briefs
