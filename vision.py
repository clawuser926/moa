#!/usr/bin/env python3
"""
MoA Vision — 给微信小弟加上识图能力
基于 mlx-vlm + Qwen2-VL-2B，M1 上跑得飞快
"""

import os, sys, time, json
from pathlib import Path

MODEL_PATH = os.path.expanduser("~/.openclaw/workspace/moa/models/Qwen2-VL-2B")

_loaded_model = None
_loaded_processor = None


def load_vision_model():
    global _loaded_model, _loaded_processor
    if _loaded_model is not None:
        return _loaded_model, _loaded_processor

    print(f"[Vision] Loading Qwen2-VL-2B from {MODEL_PATH}...", end=" ", flush=True)
    t0 = time.time()
    from mlx_vlm import load

    model, processor = load(MODEL_PATH)
    load_time = time.time() - t0
    print(f"done in {load_time:.1f}s")

    _loaded_model = model
    _loaded_processor = processor
    return model, processor


def describe_image(image_path: str, prompt: str = "请详细描述这张图片中的内容") -> str:
    """给一张图片，返回 AI 描述文字（适合微信场景）"""
    if not os.path.exists(image_path):
        return f"[Error] Image not found: {image_path}"

    model, processor = load_vision_model()

    print(f"[Vision] Processing {os.path.basename(image_path)}...", end=" ", flush=True)
    t0 = time.time()

    from mlx_vlm import generate
    from mlx_vlm.utils import prepare_inputs

    # Prepare inputs
    inputs = prepare_inputs(processor, image_path, prompt, model)

    # Generate
    output = generate(model, processor, inputs, max_tokens=512, temperature=0.7)
    elapsed = time.time() - t0

    result = output.strip() if output else "(no description generated)"
    print(f"done in {elapsed:.1f}s, {len(result)} chars")
    return result


def check_model_ready() -> bool:
    """检查视觉模型是否已下载就绪"""
    p = Path(MODEL_PATH)
    if not p.exists():
        return False
    safetensors = list(p.glob("*.safetensors"))
    return len(safetensors) > 0


def model_status() -> dict:
    """返回模型状态信息"""
    p = Path(MODEL_PATH)
    if not p.exists():
        return {"status": "not_downloaded", "path": MODEL_PATH}
    safetensors = list(p.glob("*.safetensors"))
    if len(safetensors) == 0:
        return {"status": "downloading", "path": MODEL_PATH}
    total_mb = sum(f.stat().st_size for f in safetensors) / (1024 * 1024)
    return {"status": "ready", "path": MODEL_PATH, "size_mb": f"{total_mb:.0f}"}


def main():
    if not check_model_ready():
        print(f"[Vision] Model not ready at: {MODEL_PATH}")
        print("[Vision] Download with: cd ~/.openclaw/workspace/moa/models/Qwen2-VL-2B &&")
        print("  curl -L -C - -o model.safetensors \\")
        print("    \"https://hf-mirror.com/mlx-community/Qwen2-VL-2B-Instruct-4bit/resolve/main/model.safetensors\"")
        return

    # Test mode
    print("[Vision] MoA Vision Module Ready")
    print(f"[Vision] Model: Qwen2-VL-2B-Instruct-4bit")
    print(f"[Vision] Status: {json.dumps(model_status(), ensure_ascii=False)}")

    if len(sys.argv) > 1:
        image_file = sys.argv[1]
        custom_prompt = sys.argv[2] if len(sys.argv) > 2 else "请详细描述这张图片中的内容"
        print(f"\n[Vision] Analyzing: {image_file}")
        print(f"[Vision] Prompt: {custom_prompt}")
        print()
        result = describe_image(image_file, custom_prompt)
        print()
        print("=" * 60)
        print(result)
        print("=" * 60)


if __name__ == "__main__":
    main()
