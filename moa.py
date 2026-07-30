#!/usr/bin/env python3
"""MoA - Mixture of Agents for M1 Mac"""
import time, json, sys, os, re
from pathlib import Path

WS = Path.home() / ".openclaw" / "workspace" / "moa"
MD = WS / "models"
CF = WS / "models_config.json"

DM = {
  "general": {"name":"Qwen2.5-1.5B-Instruct-4bit","model_id":"mlx-community/Qwen2.5-1.5B-Instruct-4bit","path":str(MD/"Qwen2.5-1.5B-Instruct-4bit"),"enabled":True},
  "tiny": {"name":"Qwen2.5-0.5B-4bit","model_id":"mlx-community/Qwen2.5-0.5B-4bit","path":str(MD/"Qwen2.5-0.5B-4bit"),"enabled":True}
}

RR = [
  (r"(bug|代码|code|python|javascript|写|实现|api|git|docker|shell|sql|rust|go|java|cpp|typescript|算法|leetcode)","general",0.8),
]

SP = {"general":"You are Qwen, created by Alibaba Cloud. You are a helpful assistant. Answer in Chinese.","tiny":"You are Qwen. Answer briefly in Chinese."}

def gc():
  CF.parent.mkdir(parents=True, exist_ok=True)
  if CF.exists():
    try:
      with open(CF) as f:
        return json.load(f)
    except:
      pass
  sc(DM)
  return DM

def sc(c):
  with open(CF, "w") as f:
    f.write(json.dumps(c, indent=2, ensure_ascii=False))

def ci(q):
  s = {}
  for p, t, w in RR:
    if re.search(p, q, re.IGNORECASE):
      s[t] = s.get(t, 0) + w
  if s:
    b = max(s, key=s.get)
    return b, s[b]
  return "general", 0.3

def me(k):
  c = gc()
  if k not in c:
    return False
  p = Path(c[k]["path"])
  if not p.exists():
    return False
  return len(list(p.glob("*.safetensors"))) > 0

def lm():
  c = gc()
  print()
  print("=" * 60)
  print("  MoA Model Status")
  print("=" * 60)
  for k, m in c.items():
    p = Path(m["path"])
    if p.exists():
      sf = list(p.glob("*.safetensors"))
      hs = len(sf) > 0
    else:
      hs = False
    if hs:
      mb = sum(f.stat().st_size for f in sf) / 1048576
      st = "OK {:.0f}MB".format(mb)
    elif p.exists():
      st = "PARTIAL"
    else:
      st = "NOT_DOWNLOADED"
    print("  [{}] {}: {}".format(k, m["name"], st))
  print()

loaded_models = {}

def rm(k, prompt, sps=None, mt=2048):
  global loaded_models
  c = gc()
  if k not in c:
    return "[ERROR] Unknown: {}".format(k)
  m = c[k]
  if not me(k):
    return "[WARNING] {} not downloaded".format(m["name"])
  sys.stdout.write("  Loading {}... ".format(m["name"]))
  sys.stdout.flush()
  t0 = time.time()
  try:
    if k not in loaded_models:
      from mlx_lm import load
      from mlx_lm.sample_utils import make_sampler
      loaded_models["_sampler_fn"] = make_sampler
      loaded_models["_gen_fn"] = __import__("mlx_lm").generate
      mo, tk = load(m["path"])
      loaded_models[k] = (mo, tk)
    else:
      mo, tk = loaded_models[k]
    sys.stdout.write("loaded in {:.1f}s\n".format(time.time() - t0))
    sys.stdout.flush()
    msgs = []
    if sps:
      msgs.append({"role": "system", "content": sps})
    msgs.append({"role": "user", "content": prompt})
    fp = tk.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    sampler = loaded_models["_sampler_fn"](temp=0.7)
    t1 = time.time()
    r = loaded_models["_gen_fn"](mo, tk, prompt=fp, max_tokens=mt, sampler=sampler, verbose=False)
    r = r.replace("<|im_end|>", "").strip()
    sys.stdout.write("  {} chars in {:.1f}s\n".format(len(r), time.time() - t1))
    sys.stdout.flush()
    return r
  except Exception as e:
    return "[ERROR] ({:.1f}s): {}".format(time.time() - t0, e)

def rr(q):
  t, co = ci(q)
  qd = q[:80] + "..." if len(q) > 80 else q
  print()
  print("=" * 60)
  print("  Q: " + qd)
  print("  Route: [" + t + "] (" + "{:.1f}".format(co) + ")")
  print("=" * 60)
  if not me(t):
    av = [k for k in gc() if me(k)]
    if not av:
      return "[ERROR] No models."
    print("  Using {} instead".format(av[0]))
    t = av[0]
  return rm(t, q, sps=SP.get(t, SP["general"]))

def ia():
  print()
  print("=" * 60)
  print("  MoA Interactive")
  print("  /exit /list /download")
  print("=" * 60)
  while True:
    try:
      raw = input(">> ").strip()
    except (EOFError, KeyboardInterrupt):
      print()
      print("Bye!")
      break
    if not raw:
      continue
    if raw == "/exit":
      break
    if raw == "/list":
      lm()
      continue
    if raw == "/download":
      da()
      continue
    if raw.startswith("/"):
      print("  Unknown:", raw)
      continue
    r = rr(raw)
    if r:
      print()
      print("-" * 60)
      print(r)
      print("-" * 60)

def da():
  c = gc()
  for k, m in c.items():
    if not m.get("enabled", True):
      continue
    if me(k):
      print("  OK {} ready".format(m["name"]))
      continue
    print()
    print("  DL {} ({})...".format(m["name"], m["model_id"]))
    Path(m["path"]).mkdir(parents=True, exist_ok=True)
    ok = False
    for ep in ["https://hf-mirror.com", "https://huggingface.co"]:
      try:
        os.environ["HF_ENDPOINT"] = ep
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=m["model_id"], local_dir=m["path"], resume_download=True, max_workers=2)
        if me(k):
          print("  OK done ({})".format(ep))
          ok = True
          break
      except Exception as e:
        print("  Fail: {}: {}".format(ep, e))
    if not ok:
      print("  FAILED {}".format(m["name"]))
  print("  Final:")
  lm()

if __name__ == "__main__":
  import argparse
  ap = argparse.ArgumentParser(description="MoA")
  ap.add_argument("query", nargs="?")
  ap.add_argument("-i", "--interactive", action="store_true")
  ap.add_argument("-l", "--list", action="store_true")
  ap.add_argument("-d", "--download", action="store_true")
  a = ap.parse_args()
  if a.list:
    lm()
  elif a.download:
    da()
  elif a.interactive or not a.query:
    ia()
  else:
    r = rr(a.query)
    if r:
      print(r)