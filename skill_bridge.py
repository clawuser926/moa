#!/usr/bin/env python3
"""MoA Skill Bridge — 把 OpenClaw/Codex 150个技能变成小弟的能力"""
import os, sys, json
from pathlib import Path

SKILL_ROOTS = [
    Path.home() / ".npm-global" / "lib" / "node_modules" / "openclaw" / "skills",
    Path.home() / ".codex" / "skills",
]

def list_all_skills():
    """扫描所有可用 skills，返回分类列表"""
    categories = {}
    for root in SKILL_ROOTS:
        if not root.exists():
            continue
        for item in sorted(root.iterdir()):
            if item.is_dir():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    cat = "general"
                    content = skill_file.read_text(encoding="utf-8", errors="replace")
                    for kw in ["browser", "web", "search", "firecrawl"]:
                        if kw in item.name.lower():
                            cat = "search"
                    for kw in ["github", "git", "code", "review"]:
                        if kw in item.name.lower():
                            cat = "dev"
                    for kw in ["notion", "obsidian", "note", "task", "trello"]:
                        if kw in item.name.lower():
                            cat = "productivity"
                    for kw in ["earnings", "finance", "invest", "portfolio", "income"]:
                        if kw in item.name.lower():
                            cat = "finance"
                    for kw in ["image", "video", "meme", "music", "audio"]:
                        if kw in item.name.lower():
                            cat = "media"
                    for kw in ["weather", "spotify", "sonos", "order"]:
                        if kw in item.name.lower():
                            cat = "lifestyle"
                    for kw in ["whisper", "tts", "sag", "voice"]:
                        if kw in item.name.lower():
                            cat = "voice"
                    categories.setdefault(cat, []).append(item.name)
    return categories

def get_skill_info(name):
    """获取单个 skill 的简介"""
    for root in SKILL_ROOTS:
        sp = root / name / "SKILL.md"
        if sp.exists():
            content = sp.read_text(encoding="utf-8", errors="replace")
            lines = content.split("\n")
            desc = ""
            for line in lines:
                if line.startswith("# ") and len(line) > 3:
                    desc = line[2:].strip()
                    break
            if not desc:
                desc = name.replace("-", " ").title()
            return {"name": name, "desc": desc, "path": str(sp)}
    return None

def main():
    cats = list_all_skills()
    total = sum(len(v) for v in cats.values())
    print("=" * 66)
    print("  MoA Skill Bridge — {:>3d} Skills Available".format(total))
    print("=" * 66)
    for cat, skills in sorted(cats.items()):
        print("\n  {}:".format(cat.capitalize()))
        for s in skills:
            info = get_skill_info(s)
            if info:
                print("    {:<35s} {}".format(s, info["desc"][:50]))
    print("\n  Total: {} skills across {} categories".format(
        total, len(cats)))
    print("  All available to WeChat agents via knowledge_hub")
    print()

if __name__ == "__main__":
    main()
