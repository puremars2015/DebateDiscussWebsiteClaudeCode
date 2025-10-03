# 辯論討論網站 - 啟動指南

## 🚀 快速啟動

### 1. 啟動服務
執行 `start.bat` 來同時啟動前端和後端服務：
```
start.bat
```

這會啟動：
- **前端服務器**: http://localhost:8080 (Python HTTP Server)
- **後端服務器**: http://localhost:5000 (Flask API)

### 2. 訪問網站

#### ✅ 正確的 URL（前端在 frontend 目錄下啟動）
- **首頁**: http://localhost:8080/pages/index.html
- **登入頁**: http://localhost:8080/pages/login.html
- **辯論列表**: http://localhost:8080/pages/debates.html
- **話題列表**: http://localhost:8080/pages/topics.html
- **排行榜**: http://localhost:8080/pages/ranking.html
- **管理後台**: http://localhost:8080/pages/admin.html（需管理員權限）

#### ❌ 錯誤的 URL
- ~~http://localhost:8080/frontend/pages/login.html~~ (會出現 404)

### 3. 測試 API
後端 API 根路徑：http://localhost:5000/api

測試 API 是否運行：
```
http://localhost:5000/
```

應該會看到：
```json
{
  "message": "Debate Platform API",
  "version": "1.0.0",
  "status": "running"
}
```

## 📁 目錄結構說明

```
辯論討論網站ClaudeCode/
├── start.bat          # 一鍵啟動腳本
├── backend/
│   ├── .env          # 環境變數配置
│   ├── app.py        # Flask 應用主程式
│   └── ...
└── frontend/         # ← HTTP Server 在這裡啟動
    ├── pages/        # 所有 HTML 頁面
    │   ├── index.html
    │   ├── login.html
    │   └── ...
    └── static/       # CSS 和 JS 資源
        ├── css/
        └── js/
```

**重要**: 因為 HTTP Server 從 `frontend/` 目錄啟動，所以：
- URL 路徑直接從 `frontend/` 開始
- `/pages/login.html` 實際對應 `frontend/pages/login.html`
- `/static/js/api.js` 實際對應 `frontend/static/js/api.js`

## 🔐 Line Login 配置

確認 `.env` 檔案中的設定：
```env
# Line Login 配置
LINE_CHANNEL_ID=2008216645
LINE_CHANNEL_SECRET=d3294c348d203f5c14a48d36b9aa7cba
LINE_CALLBACK_URL=http://localhost:5000/api/auth/callback

# 前端 URL
FRONTEND_URL=http://localhost:8080
```

登入流程：
1. 訪問 http://localhost:8080/pages/login.html
2. 點擊「使用 Line 登入」
3. Line 授權後會自動跳轉回登入頁
4. 顯示「登入成功！歡迎 {你的暱稱}！」
5. 自動跳轉到首頁

## 🛠️ 故障排除

### 前端 404 錯誤
- ✅ 使用: `http://localhost:8080/pages/login.html`
- ❌ 不要使用: `http://localhost:8080/frontend/pages/login.html`

### 後端連接失敗
檢查後端是否正常運行：
```
http://localhost:5000/
```

### CORS 錯誤
確認後端 `app.py` 中已啟用 CORS：
```python
from flask_cors import CORS
CORS(app)
```

### 資料庫連接問題
檢查 `.env` 中的資料庫配置是否正確：
```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=DebatePlatform
DB_USER=sa
DB_PASSWORD=你的密碼
```

## 📝 開發建議

- 修改前端代碼後，重新整理瀏覽器即可看到變更
- 修改後端代碼後，需要重新啟動 `app.py`
- 所有前端路徑都使用相對路徑或從 `/` 開始的絕對路徑
