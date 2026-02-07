"""
添加多样化研究种子到探索边界
"""

import sys
import requests

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000/api/v1"

# 2024-2025年热门研究主题（多样化）
fresh_research_topics = [
    # AI & Machine Learning (最新趋势)
    ("mamba state space models", 0.95),  # 2024年热门
    ("mixture of experts MoE", 0.95),  # GPT-4架构
    ("retrieval augmented generation RAG", 0.90),  # RAG系统
    ("low-rank adaptation LoRA fine-tuning", 0.90),  # 参数高效微调
    ("multimodal large language models", 0.90),  # 多模态LLM
    ("chain-of-thought prompting", 0.85),  # CoT推理
    ("instruction tuning", 0.85),  # 指令微调
    ("constitutional AI harmlessness", 0.85),  # AI对齐

    # Computer Vision
    ("vision transformers ViT", 0.90),  # 视觉Transformer
    ("diffusion models image generation", 0.90),  # 扩散模型
    ("neural radiance fields NeRF", 0.85),  # 3D场景重建
    ("CLIP contrastive language image pretraining", 0.85),  # 多模态学习

    # Natural Language Processing
    ("BERT masked language modeling", 0.80),  # 经典模型
    ("GPT autoregressive language modeling", 0.80),  # 自回归
    ("named entity recognition NER", 0.75),  # 信息抽取
    ("machine translation transformers", 0.75),  # 机器翻译

    # Deep Learning Theory
    ("double descent phenomenon", 0.90),  # 双下降现象
    ("grokking neural networks", 0.85),  # Grokking现象
    ("neural tangent kernel NTK", 0.80),  # NTK理论
    ("universal approximation theorem", 0.75),  # 通用逼近

    # Optimization & Training
    ("Adam optimizer convergence", 0.80),  # 优化器
    ("learning rate scheduling warmup", 0.75),  # 学习率调度
    ("gradient descent dynamics", 0.75),  # 梯度下降
    ("batch normalization internal covariate shift", 0.75),  # BN层

    # Reinforcement Learning
    ("proximal policy optimization PPO", 0.90),  # PPO算法
    ("deep Q-networks DQN", 0.85),  # DQN
    ("soft actor-critic SAC", 0.85),  # SAC算法
    ("model-based reinforcement learning", 0.80),  # 模型驱动RL
    ("multi-agent reinforcement learning", 0.80),  # 多智能体

    # Graph & Geometric Deep Learning
    ("graph convolutional networks GCN", 0.90),  # 图卷积
    ("graph attention networks GAT", 0.85),  # 图注意力
    ("geometric deep learning", 0.85),  # 几何深度学习
    ("knowledge graph embedding", 0.80),  # 知识图谱

    # Generative Models
    ("generative adversarial networks GAN", 0.85),  # GAN
    ("variational autoencoders VAE", 0.85),  # VAE
    ("normalizing flows density estimation", 0.80),  # 归一化流
    ("autoregressive models pixelCNN", 0.75),  # 自回归生成

    # Efficient Deep Learning
    ("neural architecture search NAS", 0.90),  # 神经架构搜索
    ("model compression pruning", 0.85),  # 模型压缩
    ("knowledge distillation", 0.85),  # 知识蒸馏
    ("quantization neural networks", 0.80),  # 量化
    ("efficient transformers", 0.80),  # 高效Transformer

    # Self-Supervised Learning
    ("contrastive learning SimCLR", 0.90),  # 对比学习
    ("masked image modeling MAE", 0.90),  # 掩码图像建模
    ("self-supervised video learning", 0.85),  # 自监督视频
    ("contrastive predictive coding CPC", 0.80),  # CPC

    # Robotics & Control
    ("model predictive control MPC", 0.85),  # MPC控制
    ("inverse reinforcement learning", 0.80),  # 逆RL
    ("imitation learning", 0.80),  # 模仿学习
    ("sim-to-real transfer robotics", 0.80),  # 仿真到现实

    # Healthcare & Biology
    ("protein structure prediction AlphaFold", 0.95),  # 蛋白质折叠
    ("drug discovery deep learning", 0.90),  # 药物发现
    ("medical image segmentation", 0.85),  # 医学图像
    ("electronic health records EHR", 0.80),  # 电子病历

    # Quantum Computing
    ("quantum machine learning", 0.95),  # 量子机器学习
    ("variational quantum algorithms", 0.90),  # 变分量子算法
    ("quantum error correction", 0.85),  # 量子纠错
    ("quantum supremacy", 0.85),  # 量子霸权

    # Security & Privacy
    ("adversarial attacks robustness", 0.90),  # 对抗攻击
    ("differential privacy deep learning", 0.85),  # 差分隐私
    ("federated learning privacy", 0.85),  # 联邦学习隐私
    ("homomorphic encryption", 0.80),  # 同态加密

    # Time Series & Forecasting
    ("transformers time series forecasting", 0.85),  # 时间序列
    ("temporal fusion transformers", 0.80),  # TFT
    ("long short-term memory LSTM", 0.75),  # LSTM

    # Causality & Interpretability
    ("causal inference machine learning", 0.90),  # 因果推断
    ("explainable AI SHAP LIME", 0.85),  # 可解释AI
    ("attention visualization interpretability", 0.80),  # 注意力可视化
    ("saliency maps deep learning", 0.75),  # 显著图

    # Meta Learning
    ("meta-learning few-shot learning", 0.90),  # 元学习
    ("model-agnostic meta-learning MAML", 0.85),  # MAML
    ("gradient-based meta-learning", 0.80),  # 基于梯度的元学习

    # Continual Learning
    ("continual learning catastrophic forgetting", 0.85),  # 持续学习
    ("elastic weight consolidation EWC", 0.80),  # EWC
    ("experience replay continual learning", 0.75),  # 经验回放

    # Graph & Network Science
    ("community detection networks", 0.80),  # 社区发现
    ("network embedding node2vec", 0.75),  # 网络嵌入
    ("graph neural networks explainability", 0.80),  # GNN可解释性

    # Audio & Speech
    ("wav2vec 2.0 self-supervised speech", 0.85),  # 语音预训练
    ("text-to-speech synthesis Tacotron", 0.80),  # TTS
    ("automatic speech recognition transformers", 0.80),  # ASR

    # Recommendation Systems
    ("collaborative filtering deep learning", 0.80),  # 协同过滤
    ("reinforcement learning recommender systems", 0.80),  # RL推荐
    ("session-based recommendation", 0.75),  # 会话推荐

    # Transfer Learning
    ("domain adaptation deep learning", 0.85),  # 域适应
    ("transfer learning fine-tuning", 0.80),  # 迁移学习
    ("unsupervised domain adaptation", 0.75),  # 无监督域适应
]

print("=" * 80)
print("添加多样化研究种子")
print("=" * 80)
print(f"准备添加 {len(fresh_research_topics)} 个研究主题...\n")

success_count = 0
duplicate_count = 0
failed_count = 0

for seed, priority in fresh_research_topics:
    try:
        response = requests.post(
            f"{API_BASE}/frontier/add",
            params={"seed": seed, "priority": priority},
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("message") == "Seed added":
                print(f"✅ 添加成功: {seed}")
                success_count += 1
            elif result.get("message") == "Seed already exists":
                print(f"📌 已存在: {seed}")
                duplicate_count += 1
        else:
            print(f"❌ 添加失败: {seed} (状态码: {response.status_code})")
            failed_count += 1

    except Exception as e:
        print(f"❌ 添加失败: {seed} (错误: {e})")
        failed_count += 1

print()
print("=" * 80)
print("添加完成")
print("=" * 80)
print(f"✅ 成功添加: {success_count}")
print(f"📌 已存在: {duplicate_count}")
print(f"❌ 添加失败: {failed_count}")
print(f"📊 总计: {len(fresh_research_topics)}")
print()
