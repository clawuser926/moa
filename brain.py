#!/usr/bin/env python3
"""MoA 知识大脑 — 小弟们的大脑，自动参考知识库"""
import os, sys, json
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))
import moa

BASE = Path.home() / ".openclaw" / "workspace" / "moa"
KNOW_DIR = BASE / "knowledge"
NL = chr(10)

class Brain:
    def __init__(self):
        self.knowledge = {}
        self._load_all()

    def _load_all(self):
        for f in sorted(KNOW_DIR.glob("*.md")):
            if f.name == "README.md":
                continue
            try:
                self.knowledge[f.stem] = f.read_text(encoding="utf-8")
                print("  [Brain] loaded: " + f.name)
            except Exception as e:
                print("  [Brain] skip: " + f.name + " - " + str(e))

    def query(self, question, max_kb=3):
        kw_map = {
            "self_media": ["自媒体","小红书","抖音","知乎","公众号","b站","起号","涨粉","内容","博主","爆款","流量"],
            "ecommerce": ["电商","淘宝","拼多多","京东","选品","运营","卖货","店铺","转化率","直播"],
            "cross_border": ["跨境","亚马逊","shopee","temu","出海","fba","物流","tiktok"],
            "ai_models": ["模型","llama","qwen","deepseek","mistral","mlx","部署","训练","量化","vllm","ollama"],
        }
        ql = question.lower()
        scores = []
        for stem, kws in kw_map.items():
            if stem not in self.knowledge:
                continue
            s = sum(1 for kw in kws if kw.lower() in ql)
            if s > 0:
                scores.append((s, stem))
        scores.sort(reverse=True)
        if not scores and self.knowledge:
            scores = [(1, k) for k in self.knowledge.keys()]
        results = []
        for _, stem in scores[:max_kb]:
            results.append({"domain": stem, "content": self.knowledge[stem][:2000]})
        return results

    def generate(self, niche, platform):
        relevant = self.query(niche + " " + platform)
        ctx = ""
        for item in relevant:
            ctx = ctx + "[知识:" + item["domain"] + "]" + NL + item["content"][:800] + NL
        sm = {
            "xiaohongshu": "小红书风格：标题抓眼球，多换行，多emoji，分段短，末尾话题标签",
            "zhihu": "知乎风格：开头抛观点，正文有深度有依据，结构清晰",
            "wechat_oa": "公众号风格：开篇引人入胜，正文有干货有案例",
            "douyin": "抖音脚本：前3秒抓眼球，中间干货，结尾引导关注",
            "bilibili": "B站脚本：开场自我介绍+主题，中间技术细节，结尾总结预告",
        }
        style = sm.get(platform, "")
        prompt = "你是" + platform + "博主，专注" + niche + NL + style + NL + ctx + NL + "写一篇300-500字的内容，直接输出正文。"
        raw = moa.rr(prompt)
        lines = raw.split(NL)
        clean = [l for l in lines if not l.startswith("==") and not l.startswith("  Loading") and not ("loaded in" in l)]
        return NL.join(clean).strip()

if __name__ == "__main__":
    print("  Brain starting...")
    b = Brain()
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        niche = sys.argv[2] if len(sys.argv) > 2 else "Mac效率工具"
        plat = sys.argv[3] if len(sys.argv) > 3 else "xiaohongshu"
        print(b.generate(niche, plat))
    else:
        for q in ["自媒体怎么赚钱", "M1 Mac跑什么模型", "跨境电商避坑"]:
            r = b.query(q)
            print("Q: " + q)
            for item in r:
                print("  -> " + item["domain"])
            print()
