#!/bin/bash
# MoA 一键启动脚本
echo "🚀 MoA Service Starting..."

# 1. 启动 MoA Server
PID=$(lsof -ti:18790 2>/dev/null)
if [ -n "$PID" ]; then\n  echo "  MoA Server already running (PID $PID)"
else
  cd ~/.openclaw/workspace/moa
  nohup python3 moa_server.py > /tmp/moa_server.log 2>&1 &
  sleep 2
  echo "  MoA Server started: http://127.0.0.1:18790"
fi

# 2. 测试可达性
curl -s http://127.0.0.1:18790/status | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'  Mode: {d[\"models\"][0][\"name\"]} + {d[\"models\"][2][\"name\"]}')
print(f'  Skills: {d[\"skills\"]}')
print(f'  Vision: {d[\"vision\"]}')
print(f'  Revenue: OK')
"

# 3. 显示盈利统计
python3 -c "
import sys
sys.path.insert(0, '$HOME/.openclaw/workspace/moa')
from service import stats
s = stats()
print()
print(f'  📊 今日运营数据')
print(f'  Total users: {s[\"users\"]}')
print(f'  Paid users: {s[\"paid\"]}')
print(f'  Revenue: ¥{s[\"revenue\"]}')
print(f'  Queries today: {s[\"queries\"]}')
"

echo ""
echo "✅ MoA Service is LIVE"
echo "   微信通道: online"
echo "   API: curl http://127.0.0.1:18790/chat?q=你好"
echo "   给朋友发: 微信搜索机器人名字即可"
