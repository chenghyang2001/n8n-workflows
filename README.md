# n8n-workflows

chenghyang2001 的 n8n Cloud workflow 版本控制倉庫。

## 架構

```
n8n-workflows/
├── workflows/          ← 所有 workflow JSON 檔案
├── scripts/
│   ├── deploy.py       ← 部署本地 JSON 到 n8n Cloud
│   └── pull.py         ← 從 n8n Cloud 拉取 workflow 到本地
├── .github/
│   └── workflows/
│       └── deploy.yml  ← git push 後自動部署
└── README.md
```

## 本地操作

### 環境設定（Windows CMD）
```cmd
set N8N_HOST=https://chenghyang2001.app.n8n.cloud
set N8N_API_KEY=your-api-key-here
```

### 拉取所有 workflow 到本地
```bash
python scripts/pull.py
```

### 部署單一 workflow
```bash
python scripts/deploy.py workflows/hello-claude.json
```

### 部署所有 workflow
```bash
python scripts/deploy.py
```

## GitOps 流程

```
編輯 workflows/*.json
    ↓
git add . && git commit -m "更新 xxx workflow"
    ↓
git push
    ↓
GitHub Actions 自動偵測變更的 JSON 檔案
    ↓
deploy.py 部署到 n8n Cloud
```

## GitHub Actions 設定

需要在 GitHub repo 設定以下 Secrets / Variables：

| 名稱 | 類型 | 說明 |
|------|------|------|
| `N8N_API_KEY` | Secret | n8n Cloud API Key |
| `N8N_HOST` | Variable | `https://chenghyang2001.app.n8n.cloud` |

設定路徑：GitHub repo → Settings → Secrets and variables → Actions

## n8n Cloud

- **帳號**：chenghyang2001.app.n8n.cloud
- **API**：`/api/v1/workflows`（Bearer token）
