#!/usr/bin/env python3
"""自动备份脚本 — 压缩目录并保留最近 N 天备份"""
import os
import sys
import time
import shutil
import tarfile
from datetime import datetime, timedelta

BACKUP_DIR = os.path.expanduser("~/Backups")
RETENTION_DAYS = 7

def backup(source, dest_dir=BACKUP_DIR):
    if not os.path.isdir(source):
        print(f"错误: 源目录不存在 - {source}")
        return False
    
    os.makedirs(dest_dir, exist_ok=True)
    basename = os.path.basename(os.path.abspath(source))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{basename}_{ts}.tar.gz"
    dest = os.path.join(dest_dir, filename)
    
    print(f"  📦 备份: {source}")
    print(f"  → {dest}")
    
    with tarfile.open(dest, "w:gz") as tar:
        tar.add(source, arcname=basename)
    
    size_mb = os.path.getsize(dest) / 1048576
    print(f"  ✅ 完成: {size_mb:.1f} MB")
    return True

def clean_old_backups(dest_dir=BACKUP_DIR, days=RETENTION_DAYS):
    if not os.path.isdir(dest_dir):
        return
    cutoff = datetime.now() - timedelta(days=days)
    count = 0
    for f in os.listdir(dest_dir):
        path = os.path.join(dest_dir, f)
        if os.path.isfile(path) and f.endswith(".tar.gz"):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
                count += 1
    if count:
        print(f"  🗑️  清理了 {count} 个旧备份 (>={days}天)")

def list_backups(dest_dir=BACKUP_DIR):
    if not os.path.isdir(dest_dir):
        print("  暂无备份")
        return
    files = [f for f in os.listdir(dest_dir) if f.endswith(".tar.gz")]
    if not files:
        print("  暂无备份")
        return
    print(f"  备份列表 ({len(files)} 个):")
    total = 0
    for f in sorted(files, reverse=True):
        path = os.path.join(dest_dir, f)
        size = os.path.getsize(path) / 1048576
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        total += size
        print(f"    {mtime.strftime('%m-%d %H:%M')}  {size:6.1f}MB  {f}")
    print(f"  总计: {total:.1f} MB")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 auto_backup.py <目录>     # 备份指定目录")
        print("  python3 auto_backup.py --list     # 查看备份列表")
        print("  python3 auto_backup.py --clean    # 清理旧备份")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "--list":
        list_backups()
    elif cmd == "--clean":
        clean_old_backups()
    else:
        backup(os.path.abspath(cmd))
