#!/usr/bin/env python3
"""JSONL 日志分析工具"""
import os, sys, json
from collections import Counter

def analyze(filepath, top=10, level_filter=None):
    if not os.path.exists(filepath):
        print("错误: 文件不存在 - " + filepath)
        return
    total = 0; errors = 0
    levels = Counter(); sources = Counter(); recent = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            total += 1
            try:
                entry = json.loads(line)
                lvl = entry.get("level", entry.get("status", "INFO"))
                levels[lvl] += 1
                if lvl in ("ERROR", "CRITICAL", "FAIL"):
                    errors += 1
                src = entry.get("agent", entry.get("service", "unknown"))
                sources[src] += 1
                if level_filter is None or lvl == level_filter:
                    recent.append(entry)
            except json.JSONDecodeError:
                levels["_MALFORMED"] += 1
    print("  JSONL 日志分析报告")
    print("  " + "=" * 40)
    print("  文件: " + filepath)
    print("  总行数: " + str(total))
    print("  错误数: " + str(errors))
    print()
    for level, count in levels.most_common(top):
        pct = count / max(total, 1) * 100
        print("  {:10s} {:6d} ({:5.1f}%)".format(level, count, pct))
    print()
    for src, count in sources.most_common(top):
        print("  {:20s} {:6d}".format(src, count))
    if recent:
        for e in recent[:5]:
            msg = str(e.get("r", e.get("message", "")))[:80]
            print("  [{}] {}".format(e.get("level","?"), msg))
    print()

def export_csv(filepath, output):
    import csv
    with open(filepath, "r", encoding="utf-8") as fin, \
         open(output, "w", newline="", encoding="utf-8") as fout:
        writer = None
        for line in fin:
            try:
                entry = json.loads(line.strip())
                if writer is None:
                    writer = csv.DictWriter(fout, fieldnames=list(entry.keys()))
                    writer.writeheader()
                writer.writerow(entry)
            except:
                pass
    print("  CSV 已导出: " + output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 log_analyzer.py <file.jsonl> [--csv output.csv]")
        sys.exit(1)
    path = sys.argv[1]
    csv_out = None; level = None
    if "--csv" in sys.argv:
        idx = sys.argv.index("--csv")
        csv_out = sys.argv[idx+1] if idx+1 < len(sys.argv) else "output.csv"
    if "--level" in sys.argv:
        idx = sys.argv.index("--level")  
        level = sys.argv[idx+1] if idx+1 < len(sys.argv) else None
    analyze(path, level_filter=level)
    if csv_out:
        export_csv(path, csv_out)
