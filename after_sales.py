#!/usr/bin/env python3
"""
MoA Auto-Service — 自动售后客服系统
买家付款后：自动交付 → 自动答疑 → 自动退款处理
"""
import os, sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))
import moa

NL = chr(10)
ORDERS_FILE = Path.home() / ".openclaw" / "workspace" / "moa" / "orders.json"


def init():
    if not ORDERS_FILE.exists():
        ORDERS_FILE.write_text(json.dumps({"orders": [], "total_revenue": 0}, indent=2))


def load():
    init()
    return json.loads(ORDERS_FILE.read_text())


def save(d):
    ORDERS_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False))


def new_order(buyer, product, amount, platform="xianyu"):
    """创建订单并自动交付"""
    d = load()
    order = {
        "id": "MOA" + str(int(time.time()))[-6:],
        "buyer": buyer,
        "product": product,
        "amount": amount,
        "platform": platform,
        "time": time.time(),
        "status": "paid",
        "delivered": False,
        "after_sales": [],
    }
    d["orders"].append(order)
    d["total_revenue"] = d.get("total_revenue", 0) + amount
    save(d)
    return order


def deliver(order_id):
    """自动交付数字商品"""
    d = load()
    for o in d["orders"]:
        if o["id"] == order_id:
            o["delivered"] = True
            o["deliver_time"] = time.time()
            save(d)
            return True
    return False


def after_sale(order_id, issue, auto_reply=True):
    """售后处理"""
    d = load()
    order = None
    for o in d["orders"]:
        if o["id"] == order_id:
            order = o
            break
    if not order:
        return {"ok": False, "msg": "订单不存在"}

    # 自动回复
    if auto_reply:
        prompt = f"用户售后问题：{issue}。请给出友好、耐心的回复，承诺解决问题"
        reply = moa.rr(prompt) or "您好，收到您的问题，我们马上处理！"
    else:
        reply = ""

    record = {"time": time.time(), "issue": issue, "reply": reply, "resolved": False}
    order.setdefault("after_sales", []).append(record)
    save(d)
    return {"ok": True, "reply": reply, "order_id": order_id}


def refund(order_id, reason=""):
    """退款处理（诚信第一）"""
    d = load()
    for o in d["orders"]:
        if o["id"] == order_id:
            o["status"] = "refunded"
            o["refund_reason"] = reason
            o["refund_time"] = time.time()
            d["total_revenue"] -= o["amount"]
            save(d)
            return {"ok": True, "msg": "退款成功", "amount": o["amount"]}
    return {"ok": False, "msg": "订单不存在"}


def order_status(order_id):
    """查询订单"""
    d = load()
    for o in d["orders"]:
        if o["id"] == order_id:
            return o
    return None


def stats():
    """收入统计"""
    d = load()
    orders = d.get("orders", [])
    paid = sum(1 for o in orders if o["status"] == "paid")
    refunded = sum(1 for o in orders if o["status"] == "refunded")
    no_issues = sum(1 for o in orders if len(o.get("after_sales", [])) == 0)
    return {
        "total_orders": len(orders),
        "paid": paid,
        "refunded": refunded,
        "revenue": d.get("total_revenue", 0),
        "satisfaction": f"{no_issues}/{len(orders)} 无售后" if orders else "N/A",
    }


def list_products():
    """可卖的商品清单"""
    products = []
    base = "https://github.com/clawuser926"

    products.append({
        "id": "moa-deploy",
        "name": "MoA AI 本地部署包",
        "price": 29,
        "desc": "一键部署多模型AI助手到M1/M2/M3 Mac，含4个模型+API接口",
        "delivery": f"{base}/moa/releases",
        "type": "digital",
    })
    products.append({
        "id": "python-tools-01",
        "name": "Python 效率工具合集 vol.1",
        "price": 15,
        "desc": "10个实用Python脚本：文件监控/日志分析/系统检测/自动备份",
        "delivery": f"{base}/python-tools/releases",
        "type": "digital",
    })
    products.append({
        "id": "ai-tutorial-01",
        "name": "M1 Mac AI 部署从零到一教程",
        "price": 10,
        "desc": "万字教程+视频，手把手教你本地跑大模型",
        "delivery": f"{base}/ai-tutorials/releases",
        "type": "digital",
    })
    products.append({
        "id": "custom-script",
        "name": "Python 脚本定制服务",
        "price": "面议",
        "desc": "你想要什么脚本，小弟们给你写",
        "delivery": "直接交付",
        "type": "service",
    })
    return products


def product_msg():
    """商品介绍"""
    lines = []
    lines.append("  MoA 数字商品")
    lines.append("  " + "=" * 40)
    for p in list_products():
        lines.append("")
        lines.append(f"  【{p['name']}】¥{p['price']}")
        lines.append(f"    {p['desc'][:60]}")
        lines.append(f"    交付: GitHub releases 自动下载")
    lines.append("")
    lines.append("  购买流程:")
    lines.append("    闲鱼下单 → 自动获得下载链接 → 售后找机器人")
    lines.append("  所有商品不满意包退")
    return NL.join(lines)


if __name__ == "__main__":
    init()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "products":
            print(product_msg())
        elif cmd == "stats":
            s = stats()
            print(json.dumps(s, indent=2, ensure_ascii=False))
        elif cmd == "new-order" and len(sys.argv) > 4:
            o = new_order(sys.argv[2], sys.argv[3], float(sys.argv[4]))
            print(json.dumps(o, ensure_ascii=False))
        elif cmd == "after-sale" and len(sys.argv) > 3:
            r = after_sale(sys.argv[2], sys.argv[3])
            print(json.dumps(r, ensure_ascii=False))
        elif cmd == "orders":
            d = load()
            for o in d["orders"]:
                print(f"  #{o['id']} {o['product']} ¥{o['amount']} [{o['status']}]")
        else:
            print("cmds: products, stats, new-order, after-sale, orders")
    else:
        print(product_msg())
