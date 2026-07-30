# K3 Knowledge Base — 被 MoA 吸收的开源模型知识

> 来源: MoonshotAI/Kimi-K3 (GitHub)
> 吸收者: MoA (Qwen2.5-1.5B-Instruct-4bit)

## 核心架构参数

| 参数 | 值 |
|------|-----|
| 总参数 | 2.8T |
| 激活参数 | 104B |
| 架构 | MoE (896 专家, 16激活/token) |
| 层数 | 93 (69 KDA + 24 Gated MLA + 1 Dense) |
| 上下文 | 1,048,576 tokens |
| 量化 | MXFP4 权重 / MXFP8 激活 |
| 视觉编码器 | MoonViT-V2 (401M) |

## 技术启发 → MoA 升级

1. **多专家投票路由** → 代替关键词匹配
2. **残差注意力** → 深层推理避免信息丢失
3. **共享专家机制** → tiny 模型处理通用查询
4. **负载均衡** → 防止单模型过热
5. **Fallback 链路** → 本地→云端
