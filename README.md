# MoA - Mixture of Agents on Apple Silicon

**在 Mac M1/M2/M3 上运行多模型路由系统的轻量方案**

## 简介

MoA（Mixture of Agents）是一个在 Apple Silicon（M 系列芯片）上运行多模型智能路由的工具。它利用 MLX 框架的 Apple Metal 加速，按问题类型自动调度最优本地模型，无需 GPU 或云服务。

## 特性

- **多模型路由** — 根据问题自动选择模型（闲聊→轻量模型，编程/推理→强模型）
- **纯本地推理** — 所有数据在本地，无需联网（模型下载除外）
- **Apple Silicon 原生加速** — 基于 MLX 框架，使用 Metal GPU 和统一内存
- **模型热插拔** — 任意 MLX 格式的模型即拷即用
- **交互式 + 命令行** — 支持 CLI 单次查询和交互式聊天
- **国内镜像优先** — 自动从 hf-mirror.com 下载模型

## 快速开始

```bash
# 1. 安装依赖
pip install mlx mlx-lm mlx-metal huggingface_hub

# 2. 进入项目目录
cd moa

# 3. 查看模型状态
python3 moa.py -l

# 4. 下载模型（自动从国内镜像 hf-mirror.com）
python3 moa.py -d
# 或逐个下载：python3 moa.py -d tiny

# 5. 开始使用
python3 moa.py "你好"                # 单次问答
python3 moa.py -i                     # 交互式聊天
```

## 模型配置

当前内置模型：

| Key | 模型 | 大小 | 用途 |
|-----|------|------|------|
| `tiny` | Qwen2.5-0.5B-4bit | 265 MB | 闲聊、简短问答 |
| `general` | Qwen2.5-1.5B-Instruct-4bit | 828 MB | 知识、编程、推理 |

所有模型均使用 **4-bit 量化**（MLX 格式），在 M1 16GB 上流畅运行。

## 路由规则

系统通过关键词匹配自动路由：

- 编程/技术类 → `general`（1.5B）
- 数学/推理 → `general`
- 知识类 → `general`
- 简短问候/闲聊 → `tiny`（0.5B，快速响应）
- 其他 → `general`

## 硬件要求

- **M 系列 Mac**（M1/M2/M3/M4）
- **最低 8GB 统一内存**（推荐 16GB）
- **macOS 13+**

## 项目结构

```
moa/
├── moa.py              # 主程序（路由 + 推理）
├── models/             # 模型存储目录（自动创建）
│   ├── Qwen2.5-0.5B-4bit/
│   └── Qwen2.5-1.5B-Instruct-4bit/
├── models_config.json  # 模型配置（自动生成）
└── README.md
```

## 技术栈

- [MLX](https://github.com/ml-explore/mlx) — Apple 官方机器学习框架
- [mlx-lm](https://github.com/ml-explore/mlx-examples/tree/main/llms) — MLX 上的 LLM 推理库
- [Qwen2.5](https://github.com/QwenLM/Qwen2.5) — 阿里通义千问开源模型
- [Hugging Face](https://huggingface.co) / [hf-mirror.com](https://hf-mirror.com) — 模型分发

## License

MIT
