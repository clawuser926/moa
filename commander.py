#!/usr/bin/env python3
"""MoA 指挥官 — 我带队小弟全自动运作"""
import os, sys, json, time, random, subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "moa"))
import moa

BASE = Path.home() / ".openclaw" / "workspace" / "moa"
NL = chr(10)

class Commander:
    def __init__(self):
        self.log_file = BASE / "commander_log.jsonl"
        self.state_file = BASE / "commander_state.json"
        self.content_dir = BASE / "self_media" / "content"
        self.images_dir = BASE / "self_media" / "images"
        os.makedirs(self.content_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        self._load()

    def _load(self):
        if self.state_file.exists():
            self.state = json.loads(self.state_file.read_text())
        else:
            self.state = {"total_rounds":0,"total_content":0,"total_images":0,"total_revenue":0,"last_round":0,"published":[]}
            self._save()

    def _save(self):
        self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False))

    def log(self, action, detail, value=0):
        e = {"t": time.time(), "ts": datetime.now().strftime("%H:%M"), "action": action, "detail": str(detail)[:100], "value": value}
        with open(str(self.log_file), "a") as f:
            f.write(json.dumps(e, ensure_ascii=False) + NL)

    def order_produce(self, niche, platform, style_extra=""):
        """命令: 小弟生产内容"""
        style_map = {
            "xiaohongshu": "小红书风格：标题抓眼球，多换行多emoji，分段短，结尾加话题标签",
            "zhihu": "知乎风格：开头抛观点，正文有深度有依据，结构清晰",
            "wechat_oa": "公众号风格：开篇引入，正文有干货，段落分明，像行业前辈分享经验",
            "douyin": "抖音脚本：前3秒抓眼球，中间干货，结尾引导点赞关注，口语化带画面描述",
            "bilibili": "B站脚本：开场自我介绍加主题，中间技术细节，结尾总结预告带时间轴",
        }
        style = style_map.get(platform, "")
        prompt = "你是" + platform + "博主，专注" + niche + "。" + style + style_extra + NL + "写一篇300-500字的内容。直接输出正文。"
        raw = moa.rr(prompt)
        lines = raw.split(NL)
        clean = [l for l in lines if not l.startswith("==") and not l.startswith("  Loading") and not ("loaded in" in l)]
        content = NL.join(clean).strip()
        filename = niche + "_" + platform + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".md"
        path = self.content_dir / filename
        path.write_text("# " + niche + NL + NL + content, encoding="utf-8")
        self.state["total_content"] += 1
        self._save()
        self.log("produce", filename, 1)
        return filename, content

    def order_image(self, title, platform="xiaohongshu"):
        """命令: 设计小弟配图"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random as rnd
            colors = [(255,107,107),(255,159,67),(78,205,196),(85,180,255),(156,136,255)]
            bg = rnd.choice(colors)
            light = tuple(min(c+60,255) for c in bg)
            sizes = {"xiaohongshu":(800,1000),"zhihu":(800,400),"wechat_oa":(800,400),"douyin":(720,720),"bilibili":(1280,720)}
            w,h = sizes.get(platform, (800,400))
            img = Image.new("RGB", (w,h), bg)
            draw = ImageDraw.Draw(img)
            for y in range(h):
                ratio = y/h
                r = int(bg[0]*(1-ratio)+light[0]*ratio)
                g = int(bg[1]*(1-ratio)+light[1]*ratio)
                b = int(bg[2]*(1-ratio)+light[2]*ratio)
                draw.line([(0,y),(w,y)], fill=(r,g,b))
            try:
                font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
            except:
                font = ImageFont.load_default()
            draw.text((w//6, h//3), title[:20], fill="white", font=font)
            draw.text((w//6, h//2+20), "MoA AI | " + datetime.now().strftime("%Y-%m-%d"), fill="white", font=font)
            filename = "cover_" + platform + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
            path = self.images_dir / filename
            img.save(path)
            self.state["total_images"] += 1
            self._save()
            self.log("image", filename, 0.5)
            return str(path)
        except Exception as e:
            self.log("image_fail", str(e), 0)
            return None

    def order_publish(self, platform, content_file, image_file=None, product_price=None):
        """命令: 发布小弟打包"""
        content = Path(content_file).read_text(encoding="utf-8") if os.path.exists(content_file) else ""
        pkg = {"platform":platform,"title":content.split(NL)[0].replace("#","").strip() if content else "MoA",
               "content":content[:500],"image":str(image_file) if image_file else "","time":datetime.now().strftime("%Y-%m-%d %H:%M"),
               "price":product_price,"status":"ready"}
        pkg_dir = BASE / "publish_queue"
        os.makedirs(pkg_dir, exist_ok=True)
        pkg_file = pkg_dir / (platform + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
        pkg_file.write_text(json.dumps(pkg, indent=2, ensure_ascii=False))
        self.state.setdefault("published",[]).append(pkg["title"])
        self._save()
        self.log("pkg", platform + ":" + pkg["title"][:30], 0)
        return str(pkg_file)

    def campaign_daily(self):
        """每日作战"""
        print()
        print("  ╔══════════════════════════════╗")
        print("  ║  MoA 指挥官 — 每日作战计划  ║")
        print("  ╚══════════════════════════════╝")
        plan = [("Mac效率工具","xiaohongshu",15),("本地AI部署","zhihu",None),("Python自动化","wechat_oa",None),("副业赚钱","douyin",None)]
        results = []
        for niche, platform, price in plan:
            print("  🚀 命令: 内容小弟 → " + platform + " ← " + niche)
            fname, content = self.order_produce(niche, platform)
            print("     ✅ " + fname)
            print("  🚀 命令: 设计小弟 → 配图")
            img = self.order_image(content[:20], platform)
            print("     ✅ 配图")
            print("  🚀 命令: 发布小弟 → 打包")
            pkg = self.order_publish(platform, self.content_dir / fname, img, price)
            print("     ✅ " + pkg)
            if price:
                desc = moa.rr("写闲鱼商品描述，50字内：" + content[:100] + " 价格¥" + str(price))
                print("  🚀 命令: 文案小弟 → 闲鱼描述")
                print("     ✅ " + desc.strip()[:60])
                # 保存闲鱼描述
                xianyu_file = BASE / "publish_queue" / ("xianyu_" + platform + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt")
                xianyu_file.write_text(str(desc))
            results.append({"niche":niche,"platform":platform,"file":fname,"price":price})
            time.sleep(1)
        self.state["total_rounds"] += 1
        self.state["last_round"] = time.time()
        self._save()
        print()
        print("  📊 本轮: " + str(len(results)) + " 内容 + " + str(len(results)) + " 配图")
        print("  📊 累计: " + str(self.state["total_content"]) + " 篇 | " + str(self.state["total_images"]) + " 张")
        self._git_push()
        return results

    def _git_push(self):
        try:
            subprocess.run("cd " + str(BASE) + " && git add self_media/ publish_queue/ && git commit -m \"auto: " + datetime.now().strftime("%m-%d %H:%M") + "\" && git push", shell=True, capture_output=True, text=True, timeout=30)
            self.log("git", "auto push", 0)
        except:
            pass

    def show_status(self):
        self._load()
        s = self.state
        uptime = int(time.time() - s.get("last_round", time.time()))
        print()
        print("  ╔════════════════════════════╗")
        print("  ║  MoA 指挥官 指挥面板      ║")
        print("  ╚════════════════════════════╝")
        print("  作战轮次: " + str(s["total_rounds"]) + " 次")
        print("  内容产量: " + str(s["total_content"]) + " 篇")
        print("  配图产量: " + str(s["total_images"]) + " 张")
        print("  累计收入: ¥" + str(s["total_revenue"]))
        print("  距上轮: " + str(uptime//60) + " 分钟")
        pkg_dir = BASE / "publish_queue"
        if pkg_dir.exists():
            pkgs = list(pkg_dir.glob("*.json"))
            print("  发布队列: " + str(len(pkgs)) + " 个")
            for p in sorted(pkgs, reverse=True)[:3]:
                try:
                    d = json.loads(p.read_text())
                    print("    [" + d.get("platform","?") + "] " + d.get("title","")[:30])
                except:
                    pass
        if self.log_file.exists():
            logs = self.log_file.read_text().strip().split(NL)
            print("  最近操作:")
            for l in logs[-5:]:
                try:
                    e = json.loads(l)
                    print("    [" + e.get("ts","") + "] " + e.get("action","")[:20] + " " + e.get("detail","")[:40])
                except:
                    pass
        print()

if __name__ == "__main__":
    c = Commander()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "go":
            c.campaign_daily()
        elif cmd == "status":
            c.show_status()
        elif cmd == "loop":
            iv = int(sys.argv[2]) if len(sys.argv) > 2 else 120
            print("  指挥官上线，每 " + str(iv) + " 分钟作战")
            while True:
                c.campaign_daily()
                time.sleep(iv * 60)
        elif cmd == "queue":
            pkg_dir = BASE / "publish_queue"
            for f in sorted(pkg_dir.glob("*")):
                print("  " + f.name)
        else:
            print("cmds: go | status | loop <min> | queue")
    else:
        c.show_status()
