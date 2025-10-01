# 部署指南

本文檔說明如何部署辯論平台。

## 系統需求

- Python 3.8+
- SQL Server 2016+
- Windows Server 或 Linux Server
- IIS（Windows）或 Nginx（Linux）

## 安裝步驟

### 1. 安裝 Python 依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置數據庫

1. 在 SQL Server 中創建數據庫：
```sql
CREATE DATABASE DebatePlatform;
```

2. 執行 schema 腳本：
```bash
sqlcmd -S localhost -U sa -P your_password -d DebatePlatform -i database/schema.sql
```

### 3. 配置環境變量

複製 `.env.example` 為 `.env` 並填寫配置：

```bash
cd backend
cp .env.example .env
```

編輯 `.env` 文件：
- 填寫數據庫連接資訊
- 設置 JWT 密鑰（使用隨機字符串）
- 配置 Line Login 憑證
- 設置回調 URL

### 4. 申請 Line Login

1. 訪問 [Line Developers Console](https://developers.line.biz/)
2. 創建新的 Provider 和 Channel
3. 選擇 "LINE Login" 類型
4. 獲取 Channel ID 和 Channel Secret
5. 設置 Callback URL（例如：`https://yourdomain.com/api/auth/callback`）

### 5. 啟動後端服務

#### 開發環境
```bash
cd backend
python app.py
```

#### 生產環境（使用 Gunicorn）
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 6. 配置 Web 服務器

#### Nginx 配置示例

創建 `/etc/nginx/sites-available/debate-platform`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端靜態文件
    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /pages/login.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

啟用站點：
```bash
sudo ln -s /etc/nginx/sites-available/debate-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### IIS 配置（Windows）

1. 安裝 IIS 和 URL Rewrite 模組
2. 安裝 Python 和 wfastcgi
3. 配置應用程序池
4. 添加 web.config 文件（見下方）

### 7. SSL 證書配置

使用 Let's Encrypt 獲取免費 SSL 證書：

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 後台管理

### 創建管理員用戶

1. 先通過 Line Login 創建普通用戶
2. 在數據庫中手動設置管理員權限：

```sql
UPDATE Users SET is_admin = 1 WHERE line_id = 'your_line_id';
```

### 定時任務（投票截止檢查）

創建定時任務來關閉過期的投票：

```bash
# 添加到 crontab
*/5 * * * * curl -X POST http://localhost:5000/api/votes/check_deadlines
```

或使用 Python 腳本配合 schedule 庫。

## 監控和維護

### 查看日誌

```bash
# Nginx 日誌
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 應用日誌
tail -f backend/app.log
```

### 備份數據庫

```bash
# 備份
sqlcmd -S localhost -U sa -P password -Q "BACKUP DATABASE DebatePlatform TO DISK='/backup/debate.bak'"

# 還原
sqlcmd -S localhost -U sa -P password -Q "RESTORE DATABASE DebatePlatform FROM DISK='/backup/debate.bak'"
```

## 安全建議

1. 使用強密碼和 JWT 密鑰
2. 啟用 HTTPS
3. 定期更新依賴
4. 設置防火牆規則
5. 定期備份數據庫
6. 限制 API 請求頻率
7. 使用環境變量存儲敏感信息

## 故障排除

### 數據庫連接失敗
- 檢查 SQL Server 是否運行
- 確認連接字符串正確
- 檢查防火牆設置

### Line Login 失敗
- 確認 Callback URL 正確
- 檢查 Channel ID 和 Secret
- 查看 Line Developers Console 錯誤日誌

### API 請求失敗
- 檢查 CORS 配置
- 確認 JWT token 有效
- 查看服務器日誌
