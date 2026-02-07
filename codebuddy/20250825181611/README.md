# PDF 转 Markdown 工具

这是一个用于将PDF文件转换为Markdown格式的命令行工具，支持大文件和多文件处理。

## 功能特点

- 支持单个PDF文件转换
- 支持批量处理目录中的所有PDF文件
- 自动识别标题、列表等结构
- 处理大型PDF文件
- 文本向量化功能，提取关键词、命名实体和摘要
- 友好的命令行界面和进度显示

## 安装

```bash
# 克隆仓库
git clone [仓库URL]
cd pdf-to-markdown-converter

# 安装依赖
npm install

# 全局安装（可选）
npm install -g .
```

## 使用方法

### 基本用法

```bash
# 转换单个PDF文件
node src/index.js --input example.pdf --output example.md

# 转换目录中的所有PDF文件
node src/index.js --input ./pdf-folder --output ./markdown-folder
```

### 命令行选项

```
选项:
  -V, --version          显示版本号
  -i, --input <path>     输入PDF文件或包含PDF文件的目录路径
  -o, --output <path>    输出Markdown文件或目录路径
  -r, --recursive        递归处理子目录中的PDF文件 (默认: false)
  -v, --vectorize        生成文本向量表示 (默认: false)
  --vector-output <path> 向量化数据输出路径（可选）
  -h, --help             显示帮助信息
```

## 示例

### 转换单个文件

```bash
node src/index.js --input ./documents/report.pdf --output ./markdown/report.md
```

### 转换目录中的所有PDF文件

```bash
node src/index.js --input ./documents --output ./markdown
```

### 递归处理子目录

```bash
node src/index.js --input ./documents --output ./markdown --recursive
```

## 处理大型PDF文件

本工具针对大型PDF文件进行了优化，采用分块处理的方式，可以有效处理大型PDF文件而不会导致内存溢出。

## 注意事项

- PDF文件的复杂格式（如表格、图表等）可能无法完美转换为Markdown
- 某些特殊字符或格式可能需要手动调整
- 对于非常大的PDF文件（超过100MB），转换过程可能需要较长时间

## 许可证

MIT