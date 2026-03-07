"""
open_in_n8n.py — 開啟目前 workflow JSON 在 n8n Cloud 瀏覽器頁面
用法：python scripts/open_in_n8n.py <workflow_json_path>
"""
import sys, json, webbrowser

N8N_HOST = "https://chenghyang2001.app.n8n.cloud"

if len(sys.argv) < 2:
    print("用法: python scripts/open_in_n8n.py <workflow_json_path>")
    sys.exit(1)

filepath = sys.argv[1]
with open(filepath, encoding="utf-8") as f:
    data = json.load(f)

wid = data.get("id")
url = f"{N8N_HOST}/workflow/{wid}" if wid else N8N_HOST
print(f"Opening: {url}")
webbrowser.open(url)
