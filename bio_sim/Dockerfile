FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    xvfb \
    libx11-6 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libxrandr2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest pytest-cov black isort flake8 pylint mypy

# 复制项目文件
COPY . .

# 设置环境变量（用于无头模式）
ENV DISPLAY=:99

# 暴露端口（如果需要Web界面）
EXPOSE 8000

# 默认命令
CMD ["python", "main.py"]
