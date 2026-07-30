#!/usr/bin/env python3
"""MoA Knowledge Hub — 知识吞噬中枢"""
import os, sys, json
from pathlib import Path

BASE = Path.home() / ".openclaw" / "workspace" / "moa"
KDIR = BASE / "knowledge"
MDIR = BASE / "models"
CF = BASE / "hub_config.json"

def load_config():
    """
    Load config from hub_config.json. This function handles
    loading the configuration for the knowledge hub.
    """
    CF.parent.mkdir(parents=True, exist_ok=True)
    if CF.exists():
        try:
            return json.loads(CF.read_text())
        except:
            pass
    cfg = {"absorbed": [], "api_keys": {}}
    CF.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    return cfg

def scan_models():
    """Scan all downloaded models in the models directory."""
    result = []
    if not MDIR.exists():
        return result
    for d in sorted(MDIR.iterdir()):
        if d.is_dir():
            safetensors = list(d.glob("*.safetensors"))
            if safetensors:
                total_mb = sum(f.stat().st_size for f in safetensors) / 1048576
                result.append({"name": d.name, "mb": int(total_mb), "status": "ready"})
            elif any(d.iterdir()):
                result.append({"name": d.name, "mb": 0, "status": "partial"})
            else:
                result.append({"name": d.name, "mb": 0, "status": "empty"})
    return result

def scan_skills():
    """Scan available skills from OpenClaw and Codex."""
    skills = []
    for base in [
        Path.home() / ".npm-global" / "lib" / "node_modules" / "openclaw" / "skills",
        Path.home() / ".codex" / "skills",
    ]:
        if base.exists():
            for item in sorted(base.iterdir()):
                if item.is_dir():
                    skills.append(item.name)
    return skills

def scan_apis():
    """Scan configured API keys from environment."""
    detected = []
    for var in [
        "OPENAI_API_KEY", "OPENROUTER_API_KEY", "MOONSHOT_API_KEY",
        "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "DEEPSEEK_API_KEY",
    ]:
        if os.environ.get(var):
            detected.append(var.replace("_API_KEY", ""))
    return detected

def vision_ready():
    """Check if vision model is fully downloaded."""
    vp = MDIR / "Qwen2-VL-2B"
    if vp.exists():
        safetensors = list(vp.glob("*.safetensors"))
        return len(safetensors) > 0
    return False

def status():
    """Print comprehensive status report."""
    models = scan_models()
    skills = scan_skills()
    apis = scan_apis()
    vision_ok = vision_ready()

    print()
    print("=" * 66)
    print("  MoA Knowledge Hub")
    print("=" * 66)
    print()
    print("Models [{}]:".format(len(models)))
    for m in models:
        icon = {"ready": "OK", "partial": "..", "empty": "--"}.get(m["status"], "??")
        name = m["name"]
        mb = m["mb"]
        print("  [{}] {:<35s} {:>5}MB".format(icon, name, mb))
    print()
    print("Skills: {} available".format(len(skills)))
    print("APIs: {} configured".format(len(apis)))
    print("Vision: {}".format("OK" if vision_ok else "Downloading..."))
    print()
    knowledge_files = list(KDIR.rglob("*.md"))
    if knowledge_files:
        print("Absorbed: {} knowledge files".format(len(knowledge_files)))
    else:
        print("Absorbed: 0 knowledge files (run absorb commands)")
    print()

if __name__ == "__main__":
    status()
