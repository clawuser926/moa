#!/usr/bin/env python3
"""MoA Service - 用户套餐管理与计费"""
import os, sys, json, time
from pathlib import Path

BASE = Path.home() / ".openclaw" / "workspace" / "moa"
UF = BASE / "service_users.json"
PF = BASE / "service_plans.json"
UGF = BASE / "service_usage.jsonl"

PLANS = {
    "free":      {"name": "免费体验", "price": 0,   "daily_limit": 20,   "vision": False, "skills": False},
    "monthly":   {"name": "月付会员", "price": 30,  "daily_limit": 200,  "vision": True,  "skills": True},
    "quarterly": {"name": "季度会员", "price": 79,  "daily_limit": 500,  "vision": True,  "skills": True},
    "yearly":    {"name": "年付会员", "price": 299, "daily_limit": -1,   "vision": True,  "skills": True},
}
UPGRADE_DAYS = {"monthly": 30, "quarterly": 90, "yearly": 365}


def init():
    UF.parent.mkdir(parents=True, exist_ok=True)
    if not UF.exists():
        d = {"users": {}, "total_queries": 0, "total_users": 0, "revenue": 0}
        UF.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    if not PF.exists():
        PF.write_text(json.dumps(PLANS, indent=2, ensure_ascii=False))


def load():
    init()
    return json.loads(UF.read_text())


def save(d):
    UF.write_text(json.dumps(d, indent=2, ensure_ascii=False))


def register(wx_id, nick="", plan="free"):
    d = load()
    if wx_id in d.get("users", {}):
        return {"ok": False, "msg": "already exists"}
    u = {"wx": wx_id, "nick": nick, "plan": plan, "created": time.time(),
         "expires": None if plan == "free" else time.time() + 30*86400,
         "today": 0, "last_date": "", "total": 0, "paid": False}
    d["users"][wx_id] = u
    d["total_users"] = len(d["users"])
    save(d)
    return {"ok": True, "msg": "registered: " + PLANS[plan]["name"]}


def upgrade(wx_id, plan, amount, method="wechat"):
    d = load()
    if wx_id not in d["users"]:
        register(wx_id)
        d = load()
    d["users"][wx_id]["plan"] = plan
    d["users"][wx_id]["paid"] = True
    days = UPGRADE_DAYS.get(plan, 30)
    d["users"][wx_id]["expires"] = time.time() + days * 86400
    d["users"][wx_id]["pay_method"] = method
    d["users"][wx_id]["pay_time"] = time.time()
    d["revenue"] = d.get("revenue", 0) + amount
    save(d)
    return {"ok": True, "msg": "upgraded to " + PLANS[plan]["name"]}


def check(wx_id):
    d = load()
    if wx_id not in d["users"]:
        return {"ok": True, "plan": "free", "remaining": PLANS["free"]["daily_limit"]}
    u = d["users"][wx_id]
    pn = u["plan"]
    pi = PLANS.get(pn, PLANS["free"])
    if u.get("expires") and time.time() > u["expires"] and pn != "free":
        u["plan"] = "free"
        save(d)
        pi = PLANS["free"]
    today = time.strftime("%Y-%m-%d")
    if u["last_date"] != today:
        u["today"] = 0
        u["last_date"] = today
        save(d)
    if pi["daily_limit"] > 0 and u["today"] >= pi["daily_limit"]:
        return {"ok": False, "reason": "daily limit reached", "plan": pn}
    rem = pi["daily_limit"] - u["today"] if pi["daily_limit"] > 0 else -1
    return {"ok": True, "plan": pn, "remaining": rem}


def record(wx_id):
    d = load()
    if wx_id not in d["users"]:
        return
    u = d["users"][wx_id]
    today = time.strftime("%Y-%m-%d")
    if u["last_date"] != today:
        u["today"] = 0
        u["last_date"] = today
    u["today"] += 1
    u["total"] += 1
    d["total_queries"] += 1
    save(d)


def stats():
    d = load()
    users = d.get("users", {})
    active = sum(1 for u in users.values() if (u.get("expires") or 0) > time.time() or u.get("plan") != "free")
    paid = sum(1 for u in users.values() if u.get("paid"))
    by_plan = {}
    for u in users.values():
        p = u.get("plan", "free")
        by_plan[p] = by_plan.get(p, 0) + 1
    return {"users": d["total_users"], "active": active, "paid": paid,
            "revenue": d.get("revenue", 0), "queries": d["total_queries"], "by_plan": by_plan}


def plans_msg():
    lines = []
    lines.append("")
    lines.append("  MoA AI 助手 - 套餐介绍")
    lines.append("  " + "=" * 40)
    for k, p in PLANS.items():
        limit = "不限量" if p["daily_limit"] == -1 else "每日 " + str(p["daily_limit"]) + " 次"
        features = []
        if p["vision"]: features.append("图片识别")
        if p["skills"]: features.append("技能库(149个)")
        lines.append("")
        lines.append("  【" + p["name"] + "】¥" + str(p["price"]) + "/月")
        lines.append("    " + limit)
        for f in features:
            lines.append("    " + f)
    lines.append("")
    lines.append("  " + "=" * 40)
    lines.append("  付款：微信/支付宝扫码")
    lines.append("  截图发我秒开通")
    lines.append("")
    lines.append("  回复关键词：")
    lines.append("    【套餐】看介绍")
    lines.append("    【开通】我要付费")
    lines.append("    【状态】使用情况")
    lines.append("    【免费】先体验")
    return chr(10).join(lines)


def my_status(wx_id):
    d = load()
    if wx_id not in d["users"]:
        return "还没注册，发【免费】开试用"
    u = d["users"][wx_id]
    pi = PLANS.get(u["plan"], PLANS["free"])
    limit = pi["daily_limit"]
    remaining = "不限" if limit == -1 else str(limit - u["today"])
    lines = []
    lines.append("  套餐: " + pi["name"])
    lines.append("  今日: " + str(u["today"]) + "次 / 剩余: " + remaining)
    lines.append("  总计: " + str(u["total"]) + "次")
    if u.get("expires"):
        dl = int((u["expires"] - time.time()) / 86400)
        if dl > 0:
            lines.append("  剩余 " + str(dl) + " 天")
        else:
            lines.append("  已过期")
    return chr(10).join(lines)


if __name__ == "__main__":
    init()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "stats":
            s = stats()
            print(json.dumps(s, indent=2, ensure_ascii=False))
        elif cmd == "plans":
            print(plans_msg())
        else:
            print("cmds: stats, plans")
    else:
        print(plans_msg())
