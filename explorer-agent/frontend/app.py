"""Explorer Agent Frontend - Streamlit Dashboard."""

import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(
    page_title="Explorer Agent",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# API helpers
@st.cache_data(ttl=60)
def fetch_stats():
    """Fetch exploration statistics."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/stats")
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch stats: {e}")
        return {}


@st.cache_data(ttl=60)
def fetch_nodes(limit=50, min_value=0.0):
    """Fetch recent nodes with optional score filtering."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/nodes?limit={limit}")
        nodes = response.json().get("nodes", [])
        # Filter by score if specified
        if min_value > 0:
            nodes = [n for n in nodes if n.get('value_score', 0) >= min_value]
        return nodes
    except Exception as e:
        st.error(f"Failed to fetch nodes: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_paths(limit=20, min_value=0.0):
    """Fetch recent exploration paths with optional value filtering."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/paths?limit={limit}")
        paths = response.json().get("paths", [])
        # Filter by total value if specified
        if min_value > 0:
            paths = [p for p in paths if p.get('total_value', 0) >= min_value]
        return paths
    except Exception as e:
        st.error(f"Failed to fetch paths: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_frontier():
    """Fetch frontier seeds."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/frontier")
        data = response.json()
        return data.get("seeds", [])
    except Exception as e:
        st.error(f"Failed to fetch frontier: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_insights(limit=50, insight_type=None):
    """Fetch insights from Thinker."""
    try:
        params = {"limit": limit}
        if insight_type:
            params["insight_type"] = insight_type
        response = requests.get(f"{BACKEND_URL}/api/v1/thinker/insights", params=params)
        return response.json().get("insights", [])
    except Exception as e:
        st.error(f"Failed to fetch insights: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_low_quality_pool(limit=50, unprocessed_only=False):
    """Fetch low quality pool."""
    try:
        params = {"limit": limit, "unprocessed_only": unprocessed_only}
        response = requests.get(f"{BACKEND_URL}/api/v1/thinker/low_quality_pool", params=params)
        data = response.json()
        return data.get("items", []), data.get("total", 0), data.get("unprocessed", 0)
    except Exception as e:
        st.error(f"Failed to fetch low quality pool: {e}")
        return [], 0, 0


@st.cache_data(ttl=60)
def fetch_thinking_processes(limit=20):
    """Fetch thinking process records."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/thinker/processes", params={"limit": limit})
        return response.json().get("processes", [])
    except Exception as e:
        st.error(f"Failed to fetch thinking processes: {e}")
        return []


def trigger_thinking(batch_size=10, mode="auto"):
    """Trigger thinking process."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/thinker/process",
            params={"batch_size": batch_size, "mode": mode}
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to trigger thinking: {e}")
        return None


def trigger_exploration(max_iterations=5, strategy="mixed"):
    """Trigger a new exploration round."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/explore/start",
            params={"max_iterations": max_iterations, "strategy": strategy}
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to trigger exploration: {e}")
        return None


def explore_from_path(path_id):
    """Trigger exploration from an existing path."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/explore/from_path/{path_id}"
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to explore from path: {e}")
        return None


def explore_from_seed(seed_id):
    """Trigger exploration from a specific seed."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/explore/from_seed/{seed_id}",
            params={"max_iterations": 3}
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to explore from seed: {e}")
        return None


def clear_frontier():
    """Clear all frontier seeds."""
    try:
        response = requests.delete(f"{BACKEND_URL}/api/v1/frontier/clear")
        return response.json()
    except Exception as e:
        st.error(f"Failed to clear frontier: {e}")
        return None


def add_frontier_seed(seed_text, priority=0.5):
    """Add a new seed to frontier."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/frontier/add",
            json={"seed": seed_text, "priority": priority}
        )
        return response.json()
    except Exception as e:
        st.error(f"Failed to add seed: {e}")
        return None


# Main UI
def main():
    st.title("🔭 Explorer Agent Dashboard")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("控制面板")

        # Exploration settings
        st.subheader("探索设置")
        strategy = st.selectbox(
            "探索策略",
            ["mixed", "random", "edge", "graph"],
            help="mixed: 混合策略 | random: 随机 | edge: 边缘探索 | graph: 图探索"
        )
        max_iterations = st.slider("迭代次数", 1, 10, 5)

        if st.button("🚀 立即探索", type="primary"):
            with st.spinner("探索中..."):
                result = trigger_exploration(max_iterations, strategy)
                if result:
                    st.success(f"已启动探索任务: {result.get('task_id', 'unknown')}")

        st.markdown("---")

        # Add custom seed
        st.subheader("添加探索种子")
        custom_seed = st.text_input("论文关键词/主题")
        seed_priority = st.slider("优先级", 0.0, 1.0, 0.5, 0.1)

        if st.button("➕ 添加种子") and custom_seed:
            result = add_frontier_seed(custom_seed, seed_priority)
            if result:
                st.success(f"已添加种子: {custom_seed}")
                st.cache_data.clear()  # Clear cache to refresh data

        st.markdown("---")

        # Stats display
        stats = fetch_stats()
        if stats:
            st.metric("总节点数", stats.get("total_nodes", 0))
            st.metric("总路径数", stats.get("total_paths", 0))
            st.metric("待探索种子", stats.get("frontier_count", 0))
            st.metric("平均价值分", f"{stats.get('avg_value_score', 0):.2f}")

        st.markdown("---")

        # Thinker stats
        if stats:
            st.subheader("🤔 思考者统计")
            st.metric("低质量池", f"{stats.get('low_quality_pool_size', 0)} ({stats.get('low_quality_unprocessed', 0)} 未处理)")
            st.metric("洞察数", stats.get("total_insights", 0))
            st.metric("思考会话", stats.get("thinking_sessions", 0))
            if stats.get("total_insights", 0) > 0:
                st.metric("洞察平均分", f"{stats.get('avg_insight_value', 0):.2f}")

        st.markdown("---")

        # Quality analysis
        st.subheader("质量分析")
        nodes_all = fetch_nodes(1000)
        if nodes_all:
            high_value = len([n for n in nodes_all if n.get('value_score', 0) >= 0.7])
            medium_value = len([n for n in nodes_all if 0.4 <= n.get('value_score', 0) < 0.7])
            low_value = len([n for n in nodes_all if n.get('value_score', 0) < 0.4])

            st.metric("🌟 高价值 (≥0.7)", high_value)
            st.metric("📊 中价值 (0.4-0.7)", medium_value)
            st.metric("📉 低价值 (<0.4)", low_value)

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🆕 最新发现", "🛤️ 探索路径", "🤔 思考者", "📊 质量分析", "🎯 探索管理"])

    with tab1:
        st.subheader("最新发现")
        min_score_filter = st.slider(
            "最低价值分过滤",
            0.0, 1.0, 0.0, 0.1,
            key="node_score_filter"
        )

        nodes = fetch_nodes(100, min_value=min_score_filter)

        if nodes:
            for i, node in enumerate(nodes):
                score = node.get('value_score', 0)
                emoji = '🌟' if score >= 0.8 else '⭐' if score >= 0.7 else '📌' if score >= 0.5 else '📄'

                with st.expander(
                    f"{emoji} [{score:.2f}] {node.get('title', node.get('content', '')[:80])}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**标题**: {node.get('title', 'N/A')}")
                        st.write(f"**来源**: {node.get('source', 'unknown')}")
                        st.write(f"**类型**: {node.get('type', 'unknown')}")
                    with col2:
                        st.write(f"**价值分**: {score:.3f}")
                        st.write(f"**发现时间**: {node.get('discovered_at', 'unknown')}")
                        if node.get('tags'):
                            st.write(f"**标签**: {', '.join(node['tags'])}")

                    st.markdown(f"**内容摘要**:\n{node.get('content', '')[:500]}...")
        else:
            st.info("暂无发现，点击左侧按钮开始探索")

    with tab2:
        st.subheader("探索路径")
        min_value_filter = st.slider(
            "路径总价值过滤",
            0.0, 5.0, 0.0, 0.5,
            key="path_value_filter"
        )

        paths = fetch_paths(50, min_value=min_value_filter)

        if paths:
            for path in paths:
                path_value = path.get('total_value', 0)
                nodes_list = path.get('nodes', [])

                with st.expander(
                    f"🛤️ 路径 #{path.get('id', '')} "
                    f"({'🌟' if path_value >= 2.0 else '⭐' if path_value >= 1.0 else '📊'} "
                    f"价值: {path_value:.2f}, 节点: {len(nodes_list)})"
                ):
                    # Show path nodes
                    for i, node in enumerate(nodes_list):
                        score = node.get('value_score', 0)
                        emoji = '🌟' if score >= 0.8 else '⭐' if score >= 0.7 else '📌'
                        st.write(f"{emoji} **步骤 {i+1}**: {node.get('title', node.get('content', '')[:80])} ({score:.2f})")

                    # Button to explore from this path
                    if st.button(f"🔄 沿此路径继续探索", key=f"explore_path_{path.get('id')}"):
                        with st.spinner(f"正在从路径 {path.get('id')} 探索..."):
                            result = explore_from_path(path.get('id'))
                            if result:
                                st.success(f"已启动探索任务!")
                                st.cache_data.clear()

                st.markdown("---")
        else:
            st.info("暂无探索路径")

    with tab3:
        st.subheader("🤔 思考者 - 深度挖掘系统")

        # Thinker controls
        col1, col2, col3 = st.columns(3)
        with col1:
            batch_size = st.slider("处理批次", 5, 50, 10, help="每次处理的低质量内容数量")
        with col2:
            mode = st.selectbox(
                "思考模式",
                ["auto", "mine_gems", "synthesize", "discover_connections"],
                help="auto: 自动选择 | mine_gems: 挖掘宝石 | synthesize: 综合洞察 | discover_connections: 发现关联"
            )
        with col3:
            if st.button("🧠 启动思考", type="primary"):
                with st.spinner("思考中..."):
                    result = trigger_thinking(batch_size, mode)
                    if result:
                        st.success(f"已启动思考任务: {result.get('task_id', 'unknown')}")
                        st.cache_data.clear()

        st.markdown("---")

        # Sub-tabs for Thinker views
        think_tab1, think_tab2, think_tab3 = st.tabs(["💎 洞察", "📦 低质量池", "📝 思考记录"])

        with think_tab1:
            st.write("**Thinker提取的高价值洞察**")

            insight_type_filter = st.selectbox(
                "洞察类型",
                ["全部", "hidden_gem", "synthesis", "connection"],
                help="hidden_gem: 隐藏宝石 | synthesis: 综合洞察 | connection: 关联发现"
            )

            insights = fetch_insights(
                limit=100,
                insight_type=insight_type_filter if insight_type_filter != "全部" else None
            )

            if insights:
                for insight in insights:
                    insight_type = insight.get('insight_type', 'unknown')
                    emoji_map = {
                        'hidden_gem': '💎',
                        'synthesis': '🔮',
                        'connection': '🔗'
                    }
                    emoji = emoji_map.get(insight_type, '💡')
                    score = insight.get('value_score', 0)

                    with st.expander(
                        f"{emoji} [{insight_type}] {insight.get('title', insight.get('insight_content', '')[:60])} "
                        f"({score:.2f})"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**类型**: {insight_type}")
                            st.write(f"**价值分**: {score:.3f}")
                            st.write(f"**来源数量**: {len(insight.get('source_node_ids', []))}")
                        with col2:
                            st.write(f"**创建时间**: {insight.get('created_at', 'unknown')[:19]}")

                        st.markdown(f"**洞察内容**:\n{insight.get('insight_content', '')}")

                        if insight.get('reasoning'):
                            with st.expander("🧠 查看推理过程"):
                                st.write(insight.get('reasoning'))
            else:
                st.info("暂无洞察，运行思考任务开始提取")

        with think_tab2:
            st.write("**低质量内容池 - 等待Thinker处理**")

            show_unprocessed = st.checkbox("只显示未处理", value=True)

            pool_items, total_count, unprocessed_count = fetch_low_quality_pool(
                limit=100,
                unprocessed_only=show_unprocessed
            )

            st.info(f"总计: {total_count} 项 | 未处理: {unprocessed_count} 项 | 已处理: {total_count - unprocessed_count} 项")

            if pool_items:
                for item in pool_items:
                    score = item.get('original_score', 0)
                    processed = item.get('processed', False)
                    status = "✅ 已处理" if processed else "⏳ 待处理"

                    with st.expander(
                        f"{status} [{score:.2f}] {item.get('title', item.get('content', '')[:60])}"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**原始评分**: {score:.3f}")
                            st.write(f"**来源**: {item.get('source', 'unknown')[:80]}")
                        with col2:
                            st.write(f"**类型**: {item.get('type', 'unknown')}")
                            st.write(f"**发现时间**: {item.get('discovered_at', 'unknown')[:19]}")
                        if item.get('tags'):
                            st.write(f"**标签**: {', '.join(item.get('tags', []))}")

                        st.markdown(f"**内容摘要**:\n{item.get('content', '')[:400]}...")
            else:
                st.info("低质量池为空")

        with think_tab3:
            st.write("**思考过程记录**")

            processes = fetch_thinking_processes(limit=50)

            if processes:
                for process in processes:
                    session_type = process.get('session_type', 'unknown')
                    status = process.get('status', 'unknown')
                    status_emoji = "✅" if status == "completed" else "⚠️" if status == "partial" else "❌"

                    with st.expander(
                        f"{status_emoji} {session_type} - {process.get('created_at', '')[:19]} "
                        f"({process.get('processing_time', 0):.1f}s)"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**类型**: {session_type}")
                            st.write(f"**AI模型**: {process.get('ai_model_used', 'unknown')}")
                        with col2:
                            st.write(f"**状态**: {status}")
                            st.write(f"**处理数量**: {len(process.get('input_low_quality_ids', []))}")

                        if process.get('extracted_insights'):
                            st.write(f"**生成洞察**: {len(process.get('extracted_insights', []))} 个")
                        if process.get('new_frontier_seeds'):
                            st.write(f"**新种子**: {len(process.get('new_frontier_seeds', []))} 个")

                        if process.get('error_message'):
                            st.error(f"错误: {process.get('error_message')}")
            else:
                st.info("暂无思考记录")

    with tab4:
        st.subheader("质量评测系统分析")

        # Get all nodes for analysis
        all_nodes = fetch_nodes(1000)

        if all_nodes:
            col1, col2 = st.columns(2)

            with col1:
                st.write("**价值分数分布**")
                scores = [n.get('value_score', 0) for n in all_nodes]

                fig = go.Figure(data=[go.Histogram(
                    x=scores,
                    nbinsx=20,
                    marker_color='lightblue',
                    name='价值分数'
                )])
                fig.update_layout(
                    xaxis_title="价值分数",
                    yaxis_title="节点数量",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.write("**评分统计**")
                if scores:
                    st.metric("平均分", f"{sum(scores)/len(scores):.3f}")
                    st.metric("最高分", f"{max(scores):.3f}")
                    st.metric("最低分", f"{min(scores):.3f}")
                    st.metric("中位数", f"{sorted(scores)[len(scores)//2]:.3f}")

            st.markdown("---")

            # Show evaluation system info
            st.subheader("质量评测系统说明")

            st.write("""
            **当前AI评估器**: 智谱AI GLM-4-Flash

            **评估标准** (0.0-1.0分):
            1. **新颖性** (0-1): 是否提供了新的信息或视角？
            2. **质量** (0-1): 信息是否可信、有深度？
            3. **潜力** (0-1): 是否能启发新的思考或发现？

            **评分等级**:
            - 🌟 **高价值** (≥0.7): 优秀内容，值得深入探索
            - ⭐ **中高价值** (0.5-0.7): 良好内容，有一定价值
            - 📌 **中等价值** (0.3-0.5): 普通内容，可保留
            - 📉 **低价值** (<0.3): 低质量内容，会被过滤

            **当前阈值设置**: MIN_VALUE_SCORE = 0.1
            (低于此分数的内容不会被保存到数据库)
            """)

            st.markdown("---")

            # Show low value examples
            st.subheader("低价值内容示例")
            low_value_nodes = [n for n in all_nodes if n.get('value_score', 0) < 0.3]

            if low_value_nodes:
                for node in low_value_nodes[:5]:
                    score = node.get('value_score', 0)
                    title = node.get('title', '') or node.get('content', '')[:60]
                    with st.expander(f"[{score:.2f}] {title}"):
                        st.write(f"**内容**: {node.get('content', '')[:300]}...")
                        st.write(f"**原因**: 可能与已有内容重复、信息量不足或相关性低")
            else:
                st.info("暂无低价值节点（已被系统过滤）")

    with tab5:
        st.subheader("探索管理与种子池")

        # Show current frontier
        frontier = fetch_frontier()

        if frontier:
            st.write(f"**当前种子池**: {len(frontier)} 个待探索种子")

            col1, col2 = st.columns([3, 1])

            with col1:
                # Display seeds in a table with actions
                for seed in frontier:
                    s_id, s_text, s_priority, s_attempts = (
                        seed.get('id'),
                        seed.get('seed'),
                        seed.get('priority'),
                        seed.get('attempts', 0)
                    )

                    cols = st.columns([4, 2, 2, 2])
                    with cols[0]:
                        st.text_input("种子", s_text, key=f"seed_text_{s_id}", disabled=True)
                    with cols[1]:
                        st.metric("优先级", f"{s_priority:.2f}", help=f"种子优先级")
                    with cols[2]:
                        st.metric("尝试", s_attempts, help="已尝试探索次数")
                    with cols[3]:
                        if st.button("🔍 探索", key=f"explore_seed_{s_id}"):
                            with st.spinner(f"正在从 '{s_text}' 探索..."):
                                result = explore_from_seed(s_id)
                                if result:
                                    st.success(f"已启动探索!")
                                    st.cache_data.clear()
                                    st.rerun()

                    st.markdown("---")

            with col2:
                st.write("**批量操作**")
                if st.button("🗑️ 清空所有种子"):
                    if st.confirm("确定要清空所有种子吗？"):
                        result = clear_frontier()
                        if result:
                            st.success(f"已删除 {result.get('deleted_count', 0)} 个种子")
                            st.cache_data.clear()
                            st.rerun()

            st.markdown("---")

            # Add multiple seeds at once
            st.subheader("批量添加种子")

            default_seeds = """
quantum machine learning
transformer architecture optimization
graph neural networks
federated learning privacy
multi-agent reinforcement learning
neural architecture search
self-supervised learning
generative adversarial networks
attention mechanisms
transfer learning
deep learning theory
natural language understanding
computer vision
reinforcement learning applications
            """.strip()

            batch_seeds = st.text_area(
                "每行一个种子（推荐论文主题/关键词）",
                value=default_seeds,
                height=200
            )

            batch_priority = st.slider("批量优先级", 0.0, 1.0, 0.8, 0.1)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📥 批量添加"):
                    seeds_list = [s.strip() for s in batch_seeds.split('\n') if s.strip()]
                    success_count = 0

                    with st.spinner(f"正在添加 {len(seeds_list)} 个种子..."):
                        for seed in seeds_list:
                            result = add_frontier_seed(seed, batch_priority)
                            if result:
                                success_count += 1

                    st.success(f"成功添加 {success_count}/{len(seeds_list)} 个种子")
                    st.cache_data.clear()
                    st.rerun()

            with col_b:
                if st.button("🎲 随机添加10个"):
                    import random
                    research_topics = [
                        "machine learning interpretability",
                        "causal inference",
                        "adversarial robustness",
                        "meta learning",
                        "contrastive learning",
                        "graph representation learning",
                        "transformer efficiency",
                        "continual learning",
                        "unsupervised alignment",
                        "multi-modal learning"
                    ]
                    success_count = 0
                    for seed in random.sample(research_topics, 10):
                        result = add_frontier_seed(seed, 0.7)
                        if result:
                            success_count += 1

                    st.success(f"成功添加 {success_count}/10 个随机种子")
                    st.cache_data.clear()
                    st.rerun()

        else:
            st.info("种子池为空，请添加种子或使用默认种子集")

            # Quick add default seeds
            if st.button("📋 添加默认种子集", type="primary"):
                default_seeds_list = [
                    "quantum machine learning",
                    "transformer architecture",
                    "graph neural networks",
                    "federated learning",
                    "reinforcement learning",
                    "neural architecture search",
                    "self-supervised learning",
                    "generative models",
                    "attention mechanisms",
                    "transfer learning"
                ]
                success_count = 0
                for seed in default_seeds_list:
                    result = add_frontier_seed(seed, 0.8)
                    if result:
                        success_count += 1

                st.success(f"成功添加 {success_count}/{len(default_seeds_list)} 个默认种子")
                st.cache_data.clear()
                st.rerun()


if __name__ == "__main__":
    main()
