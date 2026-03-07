"""
pull.py — 從 n8n Cloud 拉取所有 workflow 並儲存為本地 JSON 檔案

用法：
    python scripts/pull.py              # 拉取全部
    python scripts/pull.py <workflow_id> # 拉取單一 workflow

輸出位置：workflows/<workflow-name>.json
"""
import os
import sys
import json
import re
import urllib.request
import urllib.error

N8N_HOST = os.environ.get("N8N_HOST", "https://chenghyang2001.app.n8n.cloud")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")
WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")

# 從 workflow 名稱產生安全的檔名
STRIP_FIELDS = ["createdAt", "updatedAt", "versionId", "triggerCount", "scopes", "canExecute"]


def api_get(path):
    url = f"{N8N_HOST}/api/v1{path}"
    req = urllib.request.Request(url, headers={"X-N8N-API-KEY": N8N_API_KEY})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def name_to_filename(name):
    """workflow 名稱 → 安全的 ASCII 檔名"""
    safe = re.sub(r'[^\w\s-]', '', name, flags=re.UNICODE)
    safe = re.sub(r'[\s]+', '-', safe.strip())
    safe = safe.lower()
    if not safe:
        safe = "workflow"
    return f"{safe}.json"


def clean_workflow(wf):
    """移除不需要版本控制的欄位（時間戳、執行次數等）"""
    cleaned = {k: v for k, v in wf.items() if k not in STRIP_FIELDS}
    # 移除 credentials 中的敏感 id（保留名稱供參考）
    for node in cleaned.get("nodes", []):
        for cred_type, cred_info in node.get("credentials", {}).items():
            if isinstance(cred_info, dict):
                cred_info.pop("id", None)
    return cleaned


def pull_workflow(wf_id):
    print(f"  拉取 workflow ID: {wf_id} ...", end=" ")
    wf = api_get(f"/workflows/{wf_id}")
    wf = clean_workflow(wf)
    filename = name_to_filename(wf["name"])
    filepath = os.path.join(WORKFLOWS_DIR, filename)
    os.makedirs(WORKFLOWS_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    print(f"→ {filename}")
    return filepath


def pull_all():
    print(f"從 {N8N_HOST} 拉取所有 workflow...\n")
    result = api_get("/workflows?limit=200")
    workflows = result.get("data", [])
    print(f"找到 {len(workflows)} 個 workflow\n")
    saved = []
    for wf in workflows:
        if wf.get("isArchived"):
            print(f"  跳過 (archived): {wf['name']}")
            continue
        fp = pull_workflow(wf["id"])
        saved.append(fp)
    print(f"\n完成！共儲存 {len(saved)} 個檔案到 workflows/")
    return saved


if __name__ == "__main__":
    if not N8N_API_KEY:
        print("錯誤：請設定 N8N_API_KEY 環境變數")
        sys.exit(1)

    if len(sys.argv) > 1:
        pull_workflow(sys.argv[1])
    else:
        pull_all()
