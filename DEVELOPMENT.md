# 開發指南

## 快速開始

### 1. 安裝依賴

```bash
# 後端
cd backend
pip install -r requirements.txt

# 確保已安裝 SQL Server ODBC Driver 17
```

### 2. 設置數據庫

```bash
# 創建數據庫
sqlcmd -S localhost -U sa -P your_password -Q "CREATE DATABASE DebatePlatform"

# 執行 schema
sqlcmd -S localhost -U sa -P your_password -d DebatePlatform -i database/schema.sql
```

### 3. 配置環境變量

```bash
cd backend
cp .env.example .env
# 編輯 .env 填入配置
```

### 4. 啟動開發服務器

```bash
cd backend
python app.py
```

後端將運行在 `http://localhost:5000`

### 5. 訪問前端

直接在瀏覽器打開 `frontend/pages/login.html`

或使用 Python 簡單服務器：
```bash
cd frontend
python -m http.server 8000
```

然後訪問 `http://localhost:8000/pages/login.html`

## 項目結構

```
├── backend/
│   ├── app.py              # Flask 主應用
│   ├── config.py           # 配置文件
│   ├── requirements.txt    # Python 依賴
│   └── app/
│       ├── routes/         # API 路由
│       │   ├── auth.py     # 認證相關
│       │   ├── users.py    # 用戶管理
│       │   ├── topics.py   # 話題管理
│       │   ├── debates.py  # 辯論管理
│       │   ├── rounds.py   # 回合管理
│       │   ├── votes.py    # 投票管理
│       │   ├── ranking.py  # 排行榜
│       │   └── admin.py    # 管理員功能
│       ├── models/         # 數據模型（目前使用原生 SQL）
│       └── utils/          # 工具函數
│           ├── database.py # 數據庫連接
│           ├── auth.py     # JWT 認證
│           └── elo.py      # Elo 評分計算
├── frontend/
│   ├── pages/              # HTML 頁面
│   │   ├── login.html      # 登入頁
│   │   ├── index.html      # 首頁
│   │   ├── debates.html    # 辯論列表
│   │   ├── debate.html     # 辯論詳情
│   │   ├── topics.html     # 話題廣場
│   │   ├── ranking.html    # 排行榜
│   │   └── admin.html      # 管理後台
│   └── static/
│       ├── css/
│       │   └── styles.css  # 自定義樣式
│       └── js/
│           ├── api.js      # API 調用封裝
│           └── utils.js    # 前端工具函數
└── database/
    └── schema.sql          # 數據庫 Schema

```

## API 開發

### 添加新的 API 端點

1. 在 `backend/app/routes/` 創建或編輯對應的路由文件
2. 使用 Blueprint 組織路由
3. 在 `app.py` 中註冊 Blueprint

示例：
```python
from flask import Blueprint, request, jsonify
from app.utils.auth import token_required
from app.utils.database import db

bp = Blueprint('example', __name__)

@bp.route('/example', methods=['GET'])
@token_required
def get_example():
    # 實現邏輯
    return jsonify({'message': 'success'})
```

### 數據庫操作

使用 `app/utils/database.py` 中的 `db` 對象：

```python
# 查詢單條
user = db.execute_query(
    "SELECT * FROM Users WHERE user_id = ?",
    (user_id,),
    fetch_one=True
)

# 查詢多條
users = db.execute_query(
    "SELECT * FROM Users",
    fetch_all=True
)

# 插入並返回 ID
user_id = db.execute_insert(
    "INSERT INTO Users (nickname) VALUES (?)",
    ('John',)
)

# 更新/刪除
db.execute_query(
    "UPDATE Users SET nickname = ? WHERE user_id = ?",
    ('Jane', user_id)
)
```

## 前端開發

### API 調用

使用 `frontend/static/js/api.js` 中封裝的 API 方法：

```javascript
// 獲取辯論列表
const data = await DebateAPI.getDebates('ONGOING');

// 提交投票
await VoteAPI.submitVote(roundId, 'pros');

// 錯誤處理
try {
    const result = await SomeAPI.someMethod();
} catch (error) {
    showError('操作失敗：' + error.message);
}
```

### 工具函數

使用 `frontend/static/js/utils.js` 中的工具函數：

```javascript
// 檢查登入狀態
checkAuth();

// 顯示提示訊息
showSuccess('操作成功');
showError('操作失敗');

// 格式化日期
formatDate(dateString);
formatRelativeTime(dateString);

// 獲取狀態文本和顏色
getStatusText('ONGOING');
getStatusColor('ONGOING');
```

## 測試

### 手動測試流程

1. 登入系統（需要 Line Login 或手動創建測試用戶）
2. 申請話題
3. 管理員批准話題
4. 管理員創建辯論
5. 辯論雙方依次提交內容
6. 用戶投票
7. 查看結果和排行榜

### 創建測試用戶

```sql
-- 創建測試用戶
INSERT INTO Users (line_id, nickname, rating, is_admin)
VALUES
    ('test_line_id_1', '測試用戶1', 1500, 1),  -- 管理員
    ('test_line_id_2', '測試用戶2', 1500, 0),
    ('test_line_id_3', '測試用戶3', 1500, 0);

-- 創建測試話題
INSERT INTO DebateTopics (title, description, side_pros, side_cons, status, created_by)
VALUES ('測試話題', '這是一個測試話題', '支持', '反對', 'approved', 1);
```

## 常見問題

### Q: 如何修改 API 基礎 URL？
A: 編輯 `frontend/static/js/api.js` 中的 `API_BASE_URL` 常量。

### Q: 如何添加新的辯論規則？
A: 在 `DebateTopics.rules` JSON 字段中添加新規則，並在前端和後端相應處理。

### Q: 如何自定義 Elo 評分參數？
A: 修改 `backend/config.py` 中的 `ELO_K_FACTOR` 和 `INITIAL_RATING`。

### Q: 如何實現投票截止自動檢查？
A: 創建定時任務或 Cron Job 定期調用 `/api/votes/<round_id>/close_voting` 端點。

## 代碼規範

- Python: 遵循 PEP 8
- JavaScript: 使用 ES6+ 語法
- 命名: 使用有意義的變量名
- 註釋: 為複雜邏輯添加註釋
- 錯誤處理: 使用 try-catch 捕獲錯誤

## 貢獻指南

1. Fork 項目
2. 創建特性分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request
