# 📅 每日自动化探索系统 - 用户指南

## 🎯 明天你能得到什么？

### 1. 📊 自动生成的每日报告

每天早上你会得到一份详细报告，包含：

#### **JSON格式报告** (机器可读)
- 位置: `reports/daily_report_YYYYMMDD_HHMMSS.json`
- 包含: 所有探索数据、节点信息、统计数据

#### **Markdown格式报告** (人类可读)
- 位置: `reports/daily_report_YYYYMMDD_HHMMSS.md`
- 包含:
  - 📈 今日总结 (新节点数、总节点数、平均评分等)
  - 🎯 质量分布 (高/中/低价值节点占比)
  - 🔬 今日新发现的论文列表
    - 论文标题
    - 评分 (0-1.0)
    - 来源链接
    - 自动提取的标签
    - 内容摘要
  - ⚠️ 错误日志 (如果有)

### 2. 🔬 自动探索的新论文

**预期成果**:
- 每天约 **5-15篇** 新发现的Arxiv论文
- 全部经过AI质量评估 (智谱AI GLM-4-Flash)
- 自动提取关键词标签
- 按价值评分排序

**论文覆盖领域**:
- 机器学习 (Transformer, GAN, Diffusion Models)
- 计算机视觉 (Vision Transformer, NeRF)
- 自然语言处理 (LLM, RAG, Fine-tuning)
- 强化学习 (PPO, SAC, Multi-agent)
- 图神经网络 (GCN, GAT)
- 量子计算
- 生物信息学
- 等等...

### 3. 📈 数据增长趋势

系统会自动跟踪：
- 总节点数增长
- 种子池大小变化
- 平均质量分趋势
- 探索路径数量

---

## ✅ 你需要做什么 (只需3步)

### 第1步: 设置定时任务 (1分钟)

运行设置脚本:
```bash
python setup_scheduled_task.py
```

按照提示选择:
- **Windows**: 自动创建定时任务 (每天凌晨2点运行)
- **Linux**: 自动添加cron任务

**或者手动运行** (不设置定时任务):
```bash
python automated_exploration.py
```

### 第2步: 确保系统运行 (自动化)

**系统需要保持运行**:
- Docker容器必须运行 (`docker-compose up -d`)
- 计算机不能关机 (或设置开机自动启动)

**验证系统状态**:
```bash
# 检查后端
curl http://localhost:8000/api/v1/health

# 查看统计
curl http://localhost:8000/api/v1/stats
```

### 第3步: 每天查看报告 (自动化完成)

**报告位置**: `reports/` 文件夹

**查看方式**:
1. 打开 `reports/` 文件夹
2. 找到最新的 `.md` 文件
3. 用任何文本编辑器/Markdown查看器打开

**示例报告内容**:
```markdown
# 📊 每日探索报告

**日期**: 2025-12-28T02:00:00

## 📈 今日总结

- **新发现节点**: 8 个
- **总节点数**: 13 个
- **总路径数**: 15 条
- **种子池大小**: 135 个
- **平均评分**: 0.79
- **探索轮数**: 3
- **总耗时**: 285.3 秒

## 🔬 今日新发现

### 1. [0.85] Mamba: State-Space Models for Sequence Modeling

- **来源**: http://arxiv.org/abs/2312.00752
- **标签**: State Space Models, Sequence Modeling, Long Sequences
- **摘要**: Mamba is a new class of sequence modeling layers that combines the
  scalability of transformers with the efficiency of recurrent models...

### 2. [0.82] Grokking: Generalization Beyond Overfitting

...
```

---

## ⚙️ 配置说明

### 修改探索参数

编辑 `automated_exploration.py` 中的配置:

```python
EXPLORATION_CONFIG = {
    "max_iterations": 20,      # 每次探索迭代次数 (默认20)
    "strategy": "mixed",        # 探索策略: random/edge/graph/mixed
    "daily_rounds": 3,          # 每天探索轮数 (默认3轮)
    "min_new_nodes_target": 5,  # 目标新节点数 (默认5)
}
```

### 修改运行时间

**Windows**:
1. 打开 "任务计划程序"
2. 找到 "ExplorerAgent_DailyExploration"
3. 右键 → 属性 → 触发器 → 修改时间

**Linux**:
```bash
crontab -e
# 修改时间 (格式: 分 时 日 月 周)
0 2 * * *  # 改成你想要的时间，比如 0 9 * * * (早上9点)
```

---

## 📊 预期数据增长

### 第1天
- 节点数: 2 → ~10
- 新发现: ~8篇论文

### 第7天
- 节点数: ~50-70
- 新发现: ~40-60篇论文/周

### 第30天
- 节点数: ~200-300
- 新发现: ~200-300篇论文/月
- 种子池: ~200+ 个多样化主题

**质量保证**:
- 所有节点评分 ≥ 0.1 (低于此分不保存)
- 平均评分 ~0.7-0.8 (高质量)
- 70%+ 高价值节点 (≥0.7)

---

## 🔍 监控与调试

### 查看运行日志

**Docker容器日志**:
```bash
docker-compose logs -f celery_worker
docker-compose logs -f backend
```

**手动测试运行**:
```bash
python automated_exploration.py
```

### 常见问题

**Q: 没有生成新节点?**
- 检查日志是否有 "Node already exists"
- 正常现象，系统会跳过重复论文
- 尝试增加 `max_iterations` 或 `daily_rounds`

**Q: 系统报错?**
- 检查Docker容器是否运行
- 检查后端健康状态: `curl http://localhost:8000/api/v1/health`
- 查看 `reports/` 目录中的错误日志

**Q: 想临时停止?**
```bash
docker-compose stop celery_worker  # 停止探索
docker-compose stop backend         # 停止后端
```

---

## 📈 数据使用

### 查看所有节点
```bash
curl http://localhost:8000/api/v1/nodes?limit=100
```

### 按评分过滤
```bash
# 只看高价值节点 (≥0.7)
curl http://localhost:8000/api/v1/nodes?limit=100&min_value=0.7
```

### 查看探索路径
```bash
curl http://localhost:8000/api/v1/paths?limit=50
```

### Web界面查看
- 打开浏览器: http://localhost:8501
- 实时查看所有节点、路径、统计

---

## 🎓 高级用法

### 分析报告数据

```python
import json

# 读取报告
with open('reports/daily_report_20251228_020000.json') as f:
    report = json.load(f)

# 统计分析
new_nodes = report['summary']['new_nodes_today']
avg_score = report['summary']['avg_value_score']

# 找出高价值论文
high_value = [n for n in report['new_nodes'] if n['value_score'] >= 0.8]
```

### 导出到Excel

```python
import pandas as pd

# 读取所有报告
reports = list(Path('reports').glob('*.json'))
df = pd.DataFrame([json.load(open(r)) for r in reports])

# 导出
df.to_excel('exploration_summary.xlsx')
```

---

## 📞 支持

**文件位置**:
- `explorer-agent/automated_exploration.py` - 主程序
- `explorer-agent/setup_scheduled_task.py` - 定时任务设置
- `explorer-agent/reports/` - 报告输出目录

**文档**:
- `specs/exploration-engine/` - 探索引擎规格
- `specs/ai-evaluator/` - AI评估器规格
- `PROJECT_SPEC.md` - 项目总规范

---

**最后更新**: 2025-12-27
**版本**: 1.0
**下次运行**: 明天凌晨 2:00 (自动)
