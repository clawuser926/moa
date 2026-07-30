#!/usr/bin/env python3
"""Mac 系统健康检查 — CPU/内存/磁盘/网络"""
import os
import json
import time
import subprocess
from datetime import datetime

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except:
        return "N/A"

def check_cpu():
    out = run("top -l 1 -n 0 | grep 'CPU usage'")
    load = run("sysctl -n vm.loadavg")
    return {"usage": out, "load": load}

def check_memory():
    out = run("vm_stat | head -10")
    mem = run("sysctl hw.memsize | awk '{print $2/1073741824 \" GB\"}'")
    page_size = run("sysctl hw.pagesize | awk '{print $2}'")
    return {"total": mem, "vm_stat": out[:200], "page_size": page_size}

def check_disk():
    out = run("df -h /")
    lines = out.split("\n")
    if len(lines) >= 2:
        parts = lines[1].split()
        return {"total": parts[1], "used": parts[2], "avail": parts[3], "usage": parts[4]}
    return {"raw": out}

def check_network():
    ping = run("ping -c 2 -t 3 223.5.5.5 2>&1 | tail -1")
    iface = run("ifconfig en0 2>/dev/null | grep 'inet '")
    return {"ping": ping[:80], "ip": iface.strip()}

def report():
    print("=" * 50)
    print(f"  Mac 系统健康检查报告")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    cpu = check_cpu()
    print(f"\n  CPU:  {cpu['usage']}")
    print(f"  负载:  {cpu['load']}")
    
    mem = check_memory()
    print(f"\n  内存: {mem['total']}")
    
    disk = check_disk()
    print(f"\n  磁盘: 总量 {disk.get('total','?')} / 已用 {disk.get('used','?')} / 可用 {disk.get('avail','?')}")
    print(f"  使用率: {disk.get('usage','?')}")
    
    net = check_network()
    print(f"\n  网络: {net['ip']}")
    print(f"  Ping: {net['ping']}")
    print()
    print("=" * 50)

if __name__ == "__main__":
    report()
