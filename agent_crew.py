#!/usr/bin/env python3
"""MoA Agent Crew - 小弟打工系统"""
import os, sys, json, time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))
import moa
import service

NL = chr(10)

class AgentCrew:
    def __init__(self):
        self.log_file = Path.home() / ".openclaw" / "workspace" / "moa" / "crew_log.jsonl"
        self.ef = Path.home() / ".openclaw" / "workspace" / "moa" / "crew_earnings.json"
        self._load()

    def _load(self):
        if self.ef.exists():
            self.d = json.loads(self.ef.read_text())
        else:
            self.d = {"total": 0.0, "jobs": 0, "by_type": {}}

    def _save(self):
        self.ef.write_text(json.dumps(self.d, indent=2, ensure_ascii=False))

    def log(self, agent, action, result, value=0.0):
        e = {"t": time.time(), "ts": datetime.now().strftime("%H:%M"),
             "agent": agent, "action": action,
             "r": str(result)[:80], "v": value}
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(str(self.log_file), "a") as f:
            f.write(json.dumps(e, ensure_ascii=False) + NL)

    def earn(self, jt, amt):
        self.d["total"] = self.d.get("total", 0) + amt
        self.d["jobs"] = self.d.get("jobs", 0) + 1
        if jt not in self.d["by_type"]:
            self.d["by_type"][jt] = 0
        self.d["by_type"][jt] += amt
        self._save()

    def chat(self, task):
        try:
            return moa.rr(task) or ""
        except Exception as e:
            return str(e)

    def job_knowledge(self):
        repos = [
            "openai/openai-cookbook",
            "microsoft/autogen",
            "langchain-ai/langchain",
            "ml-explore/mlx-examples",
        ]
        count = 0
        for r in repos:
            prompt = f"用一句话总结 {r} 项目的核心功能"
            res = self.chat(prompt)
            self.log("knowledge", r, res[:50], 0.5)
            count += 1
        return count

    def job_content(self):
        topics = ["本地AI部署指南", "M1 Mac MLX性能优化", "开源模型选择指南"]
        count = 0
        for t in topics:
            prompt = f"写一句关于【{t}】的核心观点"
            res = self.chat(prompt)
            self.log("content", t, res[:50], 2)
            count += 1
        return count

    def job_code(self):
        tasks = ["用Python写个文件监控脚本", "写个JSONL日志分析工具"]
        count = 0
        for t in tasks:
            res = self.chat(t)
            self.log("code", t, str(len(res.split())) + " words", 3)
            count += 1
        return count

    def shift(self):
        print()
        print("  [轮班] " + datetime.now().strftime("%H:%M") + " 小弟们开工")
        nk = self.job_knowledge()
        print("  📚 知识吸收: " + str(nk) + " 个")
        nc = self.job_content()
        print("  ✍️  内容生成: " + str(nc) + " 篇")
        nc2 = self.job_code()
        print("  💻 代码生成: " + str(nc2) + " 段")
        val = nk * 0.5 + nc * 2 + nc2 * 3
        self.earn("auto", val)
        print("  💰 产出价值: ¥" + str(round(val, 1)) + " | 累计: ¥" + str(round(self.d["total"], 1)))
        print()

    def status(self):
        print()
        print("  🤖 Agent Crew")
        print("  " + "=" * 40)
        print("  累计价值: ¥" + str(round(self.d.get("total", 0), 2)))
        print("  工作数: " + str(self.d.get("jobs", 0)))
        if self.log_file.exists():
            lns = self.log_file.read_text().strip().split(NL)
            print("  日志: " + str(len(lns)) + " 条")
        print()


if __name__ == "__main__":
    c = AgentCrew()
    if len(sys.argv) > 1 and sys.argv[1] == "shift":
        c.shift()
    elif len(sys.argv) > 1 and sys.argv[1] == "loop":
        iv = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        print("  小弟们每" + str(iv) + "分钟轮班")
        while True:
            c.shift()
            time.sleep(iv * 60)
    else:
        c.status()
