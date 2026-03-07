"""
deploy.py — 將本地 JSON workflow 部署到 n8n Cloud

用法：
    python scripts/deploy.py workflows/hello-claude.json   # 部署單一
    python scripts/deploy.py                               # 部署全部 workflows/

行為：
    - 若 n8n 已有同名 workflow → PATCH 更新
    - 若不存在 → POST 新建
"""
import os
import sys
import json
import glob
import urllib.request
import urllib.error

N8N_HOST = os.environ.get("N8N_HOST", "https://chenghyang2001.app.n8n.cloud")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")
WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")

# 部署時不應傳送的欄位（唯讀或由 n8n 自動管理）
READONLY_FIELDS = ["id", "createdAt", "updatedAt", "versionId", "triggerCount",
                   "scopes", "canExecute", "isArchived", "active", "parentFolderId", "tags", "meta"]


def api_request(method, path, body=None):
    url = f"{N8N_HOST}/api/v1{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {err_body}")


def get_existing_workflow(name):
    """以名稱搜尋 n8n 中現有的 workflow，回傳 id 或 None"""
    result = api_request("GET", f"/workflows?limit=200")
    for wf in result.get("data", []):
        if wf["name"] == name:
            return wf["id"]
    return None


def prepare_body(wf):
    """移除唯讀欄位，準備 API 請求 body"""
    return {k: v for k, v in wf.items() if k not in READONLY_FIELDS}


def deploy_file(filepath):
    print(f"部署: {os.path.basename(filepath)}")
    with open(filepath, encoding="utf-8") as f:
        wf = json.load(f)

    name = wf.get("name", "unknown")
    body = prepare_body(wf)

    existing_id = get_existing_workflow(name)

    if existing_id:
        print(f"  → 已存在 (ID: {existing_id})，執行更新 (PATCH)...")
        result = api_request("PATCH", f"/workflows/{existing_id}", body)
        print(f"  ✓ 更新成功: {N8N_HOST}/workflow/{existing_id}")
        return existing_id
    else:
        print(f"  → 不存在，執行新建 (POST)...")
        result = api_request("POST", "/workflows", body)
        new_id = result.get("id")
        # 同步回寫 id 到本地 JSON（方便下次 PATCH）
        wf["id"] = new_id
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 新建成功: {N8N_HOST}/workflow/{new_id}")
        return new_id


def deploy_all():
    files = sorted(glob.glob(os.path.join(WORKFLOWS_DIR, "*.json")))
    if not files:
        print("workflows/ 資料夾中沒有 JSON 檔案")
        return
    print(f"找到 {len(files)} 個 workflow 檔案\n")
    success, failed = 0, []
    for fp in files:
        try:
            deploy_file(fp)
            success += 1
        except Exception as e:
            print(f"  ✗ 失敗: {e}")
            failed.append(os.path.basename(fp))
        print()
    print(f"完成！成功 {success} / 失敗 {len(failed)}")
    if failed:
        print("失敗清單:", failed)
        sys.exit(1)


if __name__ == "__main__":
    if not N8N_API_KEY:
        print("錯誤：請設定 N8N_API_KEY 環境變數")
        sys.exit(1)

    if len(sys.argv) > 1:
        deploy_file(sys.argv[1])
    else:
        deploy_all()
