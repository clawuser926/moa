#!/usr/bin/env python3
"""文件监控脚本 — 监控目录变化并记录日志"""
import os
import sys
import time
import logging
from datetime import datetime

def setup_logger(log_file="monitor.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_files_snapshot(directory):
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            try:
                snapshot[path] = os.path.getmtime(path)
            except OSError:
                pass
    return snapshot

def monitor(directory, interval=2):
    if not os.path.isdir(directory):
        print(f"错误: 目录不存在 - {directory}")
        sys.exit(1)
    
    logger = setup_logger()
    logger.info(f"开始监控目录: {directory}")
    logger.info(f"扫描间隔: {interval}秒")
    
    prev = get_files_snapshot(directory)
    logger.info(f"初始文件数: {len(prev)}")
    
    try:
        while True:
            time.sleep(interval)
            curr = get_files_snapshot(directory)
            
            new_files = set(curr.keys()) - set(prev.keys())
            deleted = set(prev.keys()) - set(curr.keys())
            modified = {f for f in curr if f in prev and curr[f] != prev[f]}
            
            for f in sorted(new_files):
                logger.info(f"[新增] {f}")
            for f in sorted(deleted):
                logger.info(f"[删除] {f}")
            for f in sorted(modified):
                logger.info(f"[修改] {f}")
            
            prev = curr
    except KeyboardInterrupt:
        logger.info("监控已停止")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    monitor(target)
