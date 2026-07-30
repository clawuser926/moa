#!/usr/bin/env python3
"""
MoA Router v2 - K3-Inspired Smart Routing
模仿 Kimi K3 的 MoE 路由思想，用轻量分类器替代关键词匹配
"""

import json, os, re, sys
from pathlib import Path

# 用 K3 的 MoE 思想：多个"专家"分类器投票
# K3 是 896 选 16，我们简化成 6 选 1

EXPERTS = {
    "code": {
        "keywords": ["写", "实现", "编", "修复", "bug", "debug", "代码", "code",
                     "python", "javascript", "rust", "go", "java", "cpp", "sql",
                     "api", "git", "docker", "shell", "bash", "terminal",
                     "refactor", "test", "函数", "class", "算法", "leetcode"],
        "weight": 1.0,
        "target": "general",
    },
    "math": {
        "keywords": ["数学", "证明", "推导", "计算", "solve", "equation",
                     "概率", "统计", "逻辑", "推理", "reason", "题目", "答案"],
        "weight": 0.9,
        "target": "general",
    },
    "knowledge": {
        "keywords": ["是什么", "定义", "解释", "概念", "原理", "历史", "科学",
                     "物理", "化学", "生物", "地理", "经济", "文化", "知识"],
        "weight": 0.7,
        "target": "general",
    },
    "language": {
        "keywords": ["翻译", "英文", "中文", "英语", "日文", "法语", "语言",
                     "写作", "作文", "润色", "改写", "总结", "摘要"],
        "weight": 0.7,
        "target": "general",
    },
    "chat": {
        "keywords": ["你好", "嗨", "hi", "hello", "hey", "在吗", "谢谢",
                     "bye", "哈哈", "嗯", "好的", "ok"],
        "weight": 0.8,
        "target": "tiny",
    },
    "k3_knowledge": {
        "keywords": ["Kimi", "K3", "KDA", "MoE", "Attention", "专家",
                     "2.8T", "104B", "架构", "参数量", "delta", "residual",
                     "意识", "思维", "感知", "原生", "视觉", "token"],
        "weight": 1.0,
        "target": "general",
    },
}

# K3 风格的 Activation Residuals：如果多个专家都激活，加权融合
ACTIVATION_THRESHOLD = 0.3


def smart_route(query):
    """K3 启发式路由：多专家投票 + 置信度排序"""
    votes = {}
    for expert_name, expert in EXPERTS.items():
        match_count = 0
        for kw in expert["keywords"]:
            if re.search(kw, query, re.IGNORECASE):
                match_count += 1

        if match_count > 0:
            confidence = min(expert["weight"] * (match_count / len(expert["keywords"]) * 10), 1.0)
            target = expert["target"]
            if target not in votes or confidence > votes[target][0]:
                votes[target] = (confidence, expert_name)

    if not votes:
        return "general", 0.3, "fallback"

    best_target = max(votes, key=lambda t: votes[t][0])
    best_conf, best_expert = votes[best_target]

    # K3 风格的 Attention Residuals：保留路由路径信息
    route_path = [best_expert]
    for t, (c, e) in sorted(votes.items(), key=lambda x: -x[1][0]):
        if c > ACTIVATION_THRESHOLD and e != best_expert:
            route_path.append(e)

    return best_target, best_conf, "+".join(route_path)


def test():
    test_cases = [
        ("用Python写一个快速排序", "编程"),
        ("你好呀", "闲聊"),
        ("Kimi K3 有多少参数", "K3知识"),
        ("1+1等于几", "数学"),
        ("翻译hello to Chinese", "翻译"),
        ("地球是什么形状", "知识"),
        ("今天天气怎么样", "通用"),
    ]

    print("=" * 70)
    print("  K3-Inspired MoA Router Test")
    print("=" * 70)
    for query, category in test_cases:
        target, conf, path = smart_route(query)
        print(f"  [{category:8s}] \"{query:30s}\" → [{target:7s}] ({conf:.2f}) 专家路径: {path}")
    print("=" * 70)


if __name__ == "__main__":
    test()
