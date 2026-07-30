# AI 开源免费模型知识摘要

> 学习日期：2026-07-30
> 来源：GitHub/GitHub Pages 官方仓库 & Hugging Face
> 说明：聚焦 2024-2026 免费、开源、可本地部署的主流 AI 模型

---

## 一、主流免费开源 LLM 系列

### 1. Meta LLaMA 系列

| 模型 | 参数量 | 上下文长度 | 发布日 | 特点 |
|------|--------|-----------|--------|------|
| Llama 2 | 7B / 13B / 70B | 4K | 2023-07 | 基础开源大模型，商用友好 |
| Llama 3 | 8B / 70B | 8K | 2024-04 | 改用 TikToken 分词器 |
| Llama 3.1 | 8B / 70B / **405B** | **128K** | 2024-07 | 超长上下文，405B 最强开源密集模型 |
| Llama 3.2 | **1B / 3B** / 11B-V / 90B-V | 128K | 2024-09 | 小模型适合端侧，Vision 多模态 |
| Llama 3.3 | 70B | 128K | 2024-12 | 3.1 70B 的改进版 |
| **Llama 4** | Scout-17B-16E / Maverick-17B-128E | 10M / 1M | 2025-04 | MoE 架构，超长上下文，多模态 |

**能力特点：**
- Llama 2 适合轻度对话/文本生成
- Llama 3/3.1 综合能力强，405B 接近 GPT-4 水平
- Llama 3.2 1B/3B 极小，手机/笔记本可跑
- Llama 4 Scout 支持 10M token（百万级），MoE 架构推理高效
- Llama 4 Maverick 128 expert MoE，适合大规模部署

**下载方式：** `pip install llama-models` → `llama-model download --source meta --model-id <ID>`
**Hugging Face 访问：** https://huggingface.co/meta-llama （需申请授权）
**许可证：** Llama 2/3/4 Community License（研究+商用免费）

---

### 2. Qwen3（阿里通义千问）

| 模型 | 参数量 | 上下文 | 发布日 |
|------|--------|--------|--------|
| Qwen3 (密集) | 0.6B / 1.7B / 4B / 8B / 14B / 32B | 256K（可扩展到 **1M**）| 2025-04 |
| Qwen3 (MoE) | 30B-A3B / **235B-A22B** | 256K（可扩展到 1M）| 2025-04 |
| Qwen3-2507 更新版 | 4B / 30B-A3B / 235B-A22B | 256K-1M | 2025-07 |

**能力特点：**
- 支持**思考模式（Thinking）和非思考模式（Instruct）无缝切换**
- 一个模型同时覆盖复杂推理（数学/代码）和快速闲聊
- 235B-A22B MoE 每次推理仅激活 22B 参数，效率高
- 支持 100+ 语言，中文能力最强开源模型
- Agent/tool use 能力领先
- Qwen3-2507 版本大幅提升知识覆盖和指令遵循

**下载：** https://huggingface.co/Qwen
**部署：** `pip install transformers>=4.51.0` → 使用 AutoModelForCausalLM
**许可证：** Apache 2.0（完全商用自由）

---

### 3. DeepSeek 系列

| 模型 | 参数量 | 激活量 | 上下文 | 特点 |
|------|--------|--------|--------|------|
| **DeepSeek-V3** | 671B (MoE) | 37B | 128K | 最强开源基础模型，类 GPT-4o |
| DeepSeek-R1 | 671B (MoE) | 37B | 128K | 推理专用，类似 o1 |
| DeepSeek-R1-Distill | 1.5B ~ 70B (密集) | 全部 | 128K | 知识蒸馏版，小模型高性能 |

**能力特点：**
- V3：MMLU 87.1，HumanEval 65.2，GSM8K 89.3 — 开源 SOTA
- R1：首创纯 RL 训练推理能力（无需 SFT），媲美 OpenAI o1
- R1-Distill-Qwen-32B 超越 o1-mini
- 训练仅用 2.788M H800 GPU-hours（极低成本）
- MLA 注意力 + DeepSeekMoE 架构，推理效率高
- 支持多 token 预测（MTP），可用于推测解码加速

**下载：** https://huggingface.co/deepseek-ai
**部署：** vLLM / SGLang / llama.cpp 均支持；需大显存（671B 建议 8×A100/H100）
**许可证：** MIT（完全商用自由）

---

### 4. Mistral 系列

| 模型 | 参数量 | 特点 |
|------|--------|------|
| Mistral 7B | 7B | 轻量高效，当年最强 7B |
| Mixtral 8x7B | 46.7B (MoE) | 12.9B 激活，对标 Llama 2 70B |
| Mixtral 8x22B | 141B (MoE) | 39B 激活 |
| Mistral Nemo 12B | 12B | 与 NVIDIA 合作，128K 上下文 |
| Mistral Large 2 | 123B | 接近 GPT-4 级别 |
| **Mistral Small 3.1** | **24B** | 2025 最新，对标 Llama 3 8B 但大 3 倍 |
| Pixtral 12B | 12B | 多模态（图文理解）|
| Codestral 22B | 22B | 代码专用 |
| Codestral Mamba 7B | 7B | Mamba 架构，线性复杂度 |

**能力特点：**
- 全部开源，Apache 2.0（部分模型为 MNPL/MRL 非商用）
- Mixtral 系列 MoE 效率极高
- Mistral Small 3.1 适合中等部署
- Pixtral 多模态能力突出

**下载：** https://huggingface.co/mistralai
**部署：** `pip install mistral-inference` → `mistral-chat`

---

### 5. Gemma（Google）

| 模型 | 参数量 | 特点 |
|------|--------|------|
| Gemma 2 | 2B / 9B / 27B | Google 开源，轻量高效 |
| **Gemma 3** | 2B / 9B / 27B | 2025 更新版，改进架构 |
| PaliGemma 2 | 多模态 | VLM 视觉语言模型 |

**能力特点：**
- gemma.cpp 提供纯 C++ 推理引擎，仅 ~2K LoC
- CPU-only 推理友好，SIMD 优化
- 研究友好，易于修改和嵌入
- 支持 fp8/bf16/fp32 混合精度

**下载：** https://www.kaggle.com/models/google/gemma-2
**许可证：** Gemma License（商用免费，需同意条款）

---

### 6. Phi（Microsoft）

| 模型 | 参数量 | 特点 |
|------|--------|------|
| Phi-3 | 3.8B / 7B / 14B | 小模型之王，参数效率极高 |
| **Phi-4** | 14B | 2025 最新，最强 SLM |
| Phi-Vision | 多模态 | 视觉理解 |

**能力特点：**
- SLM（小语言模型）定位，成本极低
- Phi-3 3.8B 在手机/树莓派上可运行
- 推理、编码、数学在同尺寸中领先
- 适合边缘设备/离线部署

**下载：** https://huggingface.co/microsoft
**许可证：** MIT

---

## 二、MLX 框架（Apple Silicon 专属）

- **定位：** Apple 机器学习研究团队推出的数组框架，类似 NumPy + PyTorch + Jax
- **核心特性：**
  - Python API 近似 NumPy，神经网络 API 近似 PyTorch
  - **统一内存**：CPU/GPU 共享内存，无需数据搬移
  - 惰性计算 + 动态图构建
  - 支持自动微分、自动向量化、计算图优化
  - 支持多设备（CPU + GPU 任意组合）
- **支持的模型（mlx-examples）：**
  - LLaMA 推理 + LoRA 微调
  - Stable Diffusion 文生图
  - OpenAI Whisper 语音识别
  - Transformer 语言模型训练
- **安装：** macOS → `pip install mlx`；Linux → `pip install mlx[cuda]`
- **许可证：** MIT

---

## 三、Hugging Face 热门模型生态

Hugging Face 托管数万个开源模型，以下是最热门/下载量最高的模型类型：

| 类别 | 代表模型 | HF 地址 |
|------|---------|---------|
| 通用对话 | Llama 3/4, Qwen3, Mistral, DeepSeek | huggingface.co/meta-llama, /Qwen, /mistralai, /deepseek-ai |
| 推理/数学 | DeepSeek-R1, Qwen3-Thinking | 同上 / 各系列下 |
| 代码 | CodeLlama, DeepSeek-Coder, Qwen2.5-Coder | /codellama, /deepseek-ai |
| 多模态 | Llama 4, Qwen-VL, Pixtral, PaliGemma | 各组织下 |
| 嵌入 | BGE, E5, GTE | /BAAI, /intfloat |
| 语音 | Whisper, Bark, MMS | /openai (Whisper), /suno (Bark) |
| 图像生成 | Stable Diffusion 3, Flux | /stabilityai, /black-forest-labs |

---

## 四、部署要点

### 硬件要求

| 模型规模 | 最小显存 | 推荐部署方式 |
|----------|---------|-------------|
| 1B-3B（Phi-3, Llama 3.2 1B/3B） | 2-4 GB | 手机 / 笔记本 / CPU |
| 7B-8B | 8-16 GB | 消费级 GPU（RTX 3090/4090） |
| 14B-24B | 16-24 GB | RTX 4090 / A10 / A100 |
| 32B-70B | 24-48 GB | 多卡 RTX 4090 / A100 |
| 235B-671B（MoE 激活 22-37B）| 48-80 GB（+量化）| 多卡 A100/H100 |
| 405B+ | 80 GB+ | 多节点集群 |

### 推理框架推荐

| 框架 | 适用场景 | 安装 |
|------|---------|------|
| **llama.cpp / Ollama** | 本地轻量部署，CPU/边缘设备 | `ollama pull llama3.2` |
| **MLX** | Apple Silicon (M系列芯片) | `pip install mlx` |
| **vLLM** | 高吞吐生产部署 | `pip install vllm` |
| **SGLang** | 大规模推理，多模态 | `pip install sglang` |
| **Transformers** | 灵活研究/实验 | `pip install transformers` |
| **TGI** (HuggingFace) | 生产级文本生成推理 | Docker 部署 |

### 量化方案

| 量化类型 | 显存节省 | 精度损失 |
|----------|---------|---------|
| FP8 | 约 50% | 极小 |
| INT4 (AWQ/GPTQ) | 约 75% | 可接受 |
| INT4 (GGUF Q4_K_M) | 约 75% | 可接受 |
| INT4 (Llama 原生 int4_mixed) | 约 75% | 极小，1 卡跑 Scout-17B |

### 快速部署示例

```bash
# Ollama（最简单）
ollama pull llama3.2:3b    # 3B 模型
ollama pull qwen3:8b       # Qwen3 8B
ollama pull deepseek-r1:7b # DeepSeek R1 蒸馏版

# Transformers（Python）
pip install transformers accelerate
python -c "from transformers import AutoModelForCausalLM; m=AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-8B', device_map='auto')"

# MLX（Apple Silicon）
pip install mlx-lm
mlx_lm.generate --model mlx-community/Llama-3.2-3B-Instruct-4bit --prompt "你好"

# vLLM（生产）
pip install vllm
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen3-8B-Instruct
```

---

## 五、趋势总结

1. **MoE 成为主流**：DeepSeek-V3、Qwen3-MoE、Llama 4、Mixtral 全部采用 MoE，以极低激活参数实现大模型效果
2. **超长上下文**：Llama 4 支持 10M tokens，Qwen3 支持 1M tokens
3. **推理模型崛起**：DeepSeek-R1、Qwen3-Thinking 带 Chain-of-Thought 推理能力
4. **小模型性能爆炸**：Phi-3/4、Llama 3.2 1B/3B、Qwen3 0.6B 等小模型在特定任务上接近大模型
5. **多模态融合**：Llama 4、Qwen-VL、Pixtral、PaliGemma 等视觉语言模型普及
6. **Apple Silicon 生态**：MLX 框架专为 Mac 优化，统一内存设计降低门槛
7. **开源许可证成熟**：Apache 2.0 / MIT / Llama License 均支持商用

---

*此文档由 MoA 学习特攻队生成，基于 GitHub 官方仓库和 Hugging Face 实际数据。*
