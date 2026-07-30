#!/usr/bin/env python3
"""微信服务机器人"""
import os, sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))
import service
import moa

CMD_MAP = {
    "套餐": "plans", "会员": "plans", "价格": "plans",
    "开通": "sub", "订阅": "sub", "付费": "sub",
    "状态": "st", "我的": "st",
    "免费": "free", "试用": "free",
    "帮助": "help", "help": "help",
}

NL = chr(10)

def handle_text(from_user, text):
    text = text.strip()
    for kw, cmd in CMD_MAP.items():
        if kw in text:
            return run_cmd(cmd, from_user)
    return chat(from_user, text)

def run_cmd(cmd, wx):
    if cmd == "plans":
        return service.plans_msg()
    elif cmd == "sub":
        return NL.join(["MoA AI 会员", "", "30元/月 每日200次+识图", "79元/季 每日500次", "299元/年 不限量", "", "付款后截图发我秒开通"])
    elif cmd == "st":
        return service.my_status(wx)
    elif cmd == "free":
        service.register(wx, plan="free")
        return NL.join(["免费体验已开通", "每日20次", "回复【套餐】升级"])
    elif cmd == "help":
        return NL.join(["MoA AI", "【套餐】查看价格", "【状态】用量", "【免费】试用", "发图片可识别内容"])
    return ""

def chat(wx_id, text):
    ac = service.check(wx_id)
    if not ac["ok"]:
        return NL.join(["今日次数用完", "回复【套餐】升级"])
    try:
        r = moa.rr(text)
        if not r:
            return "（思考中...）"
        service.record(wx_id)
        return r
    except:
        return "系统繁忙，稍后再试"

def handle_image(from_user, img_path, prompt=""):
    ac = service.check(from_user)
    if not ac["ok"] or ac["plan"] == "free":
        return NL.join(["图片识别仅限会员", "回复【套餐】升级"])
    try:
        from vision_agent import handle_image as vi
        r = vi(img_path, prompt)
        service.record(from_user)
        return r or "没认出"
    except:
        return "识别失败"

if __name__ == "__main__":
    print("WeChat service bot loaded")
