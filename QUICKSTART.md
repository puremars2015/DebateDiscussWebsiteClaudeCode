# 快速開始指南

## 最小可行性方案（MVP）已完成！

本項目已完成 1v1 辯論平台的最小可行性方案開發，包含完整的後端 API 和前端界面。

## 🎯 核心功能

✅ **用戶系統**
- Line Login 認證
- JWT Token 管理
- 用戶個人資料與戰績

✅ **話題管理**
- 用戶提交話題申請
- 管理員審批機制
- 話題列表瀏覽

✅ **辯論系統**
- 回合制辯論流程
- 狀態機管理
- 正反方輪流發言

✅ **投票系統**
- 加權投票（普通用戶 1 分，法官 10 分）
- 投票時限管理
- 即時獲勝判定（≥70% 得票率）

✅ **評分系統**
- Elo 評分算法
- 排行榜顯示
- 戰績記錄

✅ **管理後台**
- 話題審核
- 辯論創建
- 法官分配

## 📦 項目結構

```
辯論討論網站ClaudeCode/
├── backend/                 # Flask 後端
│   ├── app.py              # 主應用
│   ├── config.py           # 配置
│   ├── requirements.txt    # Python 依賴
│   └── app/
│       ├── routes/         # API 路由（8個模組）
│       └── utils/          # 工具函數
├── frontend/               # 前端界面
│   ├── pages/             # HTML 頁面（7個頁面）
│   └── static/            # CSS/JS 資源
├── database/              # 數據庫
│   └── schema.sql         # SQL Server Schema
├── CLAUDE.md              # 項目規格說明
├── DEVELOPMENT.md         # 開發指南
├── DEPLOYMENT.md          # 部署指南
└── QUICKSTART.md          # 本文件
```

## 🚀 立即啟動

### 前置需求

- Python 3.8+
- SQL Server 2016+
- ODBC Driver 17 for SQL Server

### 1. 設置數據庫

```bash
# 創建數據庫
sqlcmd -S localhost -U sa -P your_password -Q "CREATE DATABASE DebatePlatform"

# 執行 Schema
sqlcmd -S localhost -U sa -P your_password -d DebatePlatform -i database/schema.sql
```

### 2. 配置環境

```bash
cd backend
cp .env.example .env
```

編輯 `.env` 文件，填入：
- 數據庫連接資訊
- JWT 密鑰（隨機字符串）
- Line Login 憑證（需先到 Line Developers 申請）

### 3. 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

### 4. 啟動後端

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

或手動啟動：
```bash
cd backend
python app.py
```

### 5. 訪問前端

直接在瀏覽器打開：
```
file:///完整路徑/frontend/pages/login.html
```

或使用 Python HTTP 服務器：
```bash
cd frontend
python -m http.server 8000
```
然後訪問 `http://localhost:8000/pages/login.html`

## 🔑 首次使用

### 創建管理員賬號

1. 先通過 Line Login 登入（或直接在數據庫創建測試用戶）
2. 在數據庫中設置管理員權限：

```sql
-- 查看所有用戶
SELECT user_id, nickname, line_id, is_admin FROM Users;

-- 設置管理員
UPDATE Users SET is_admin = 1 WHERE user_id = 1;
```

### 創建測試數據（可選）

```sql
-- 創建測試用戶
INSERT INTO Users (line_id, nickname, rating, is_admin) VALUES
('test_admin', '管理員', 1500, 1),
('test_user1', '辯手甲', 1500, 0),
('test_user2', '辯手乙', 1500, 0),
('test_voter', '投票者', 1500, 0);

-- 創建測試話題
INSERT INTO DebateTopics (title, description, side_pros, side_cons, status, created_by, rules)
VALUES
('遠距工作是否應該成為常態',
 '隨著科技發展，遠距工作變得越來越普遍，這場辯論將探討遠距工作是否應該成為未來工作的常態模式。',
 '支持遠距工作',
 '反對遠距工作',
 'approved',
 1,
 '{"word_limit": 500, "time_limit_hours": 24}');
```

## 📱 使用流程

### 普通用戶
1. 訪問登入頁面
2. 使用 Line Login 登入
3. 瀏覽話題和辯論
4. 提交新話題申請
5. 對辯論進行投票
6. 查看個人戰績和排行榜

### 辯論參與者
1. 等待管理員分配辯論
2. 按照回合狀態依次提交內容：
   - 正方主張
   - 反方質詢
   - 正方回覆
   - 反方主張
   - 正方質詢
   - 反方回覆
3. 等待投票結果
4. 查看 Elo 評分變化

### 管理員
1. 登入後訪問管理後台
2. 審核用戶提交的話題
3. 創建辯論並分配參與者
4. 必要時強制結束辯論
5. 分配法官評審

## 🎮 測試完整流程

1. **登入** → 使用測試賬號或 Line Login
2. **申請話題** → 提交新的辯論主題
3. **審核話題** → 管理員批准話題
4. **創建辯論** → 管理員創建辯論並分配正反方
5. **進行辯論** → 正反方依次提交內容
6. **投票** → 用戶對辯論進行投票
7. **查看結果** → 檢視勝負與評分變化
8. **排行榜** → 查看玩家排名

## 🔧 技術棧

- **後端**: Python Flask + SQL Server
- **前端**: HTML + JavaScript + Tailwind CSS
- **認證**: Line Login + JWT
- **評分**: Elo Rating Algorithm
- **API**: RESTful API

## 📚 更多文檔

- **開發指南**: 查看 `DEVELOPMENT.md`
- **部署指南**: 查看 `DEPLOYMENT.md`
- **項目規格**: 查看 `CLAUDE.md`

## ⚠️ 注意事項

1. **Line Login 配置**: 需要到 [Line Developers Console](https://developers.line.biz/) 申請憑證
2. **數據庫連接**: 確保 SQL Server 運行並配置正確
3. **CORS 設置**: 開發環境已允許跨域，生產環境請調整
4. **投票截止**: 需要設置定時任務或手動調用 API 關閉投票
5. **安全性**: 生產環境請使用 HTTPS 並設置強密碼

## 🐛 常見問題

**Q: 無法連接數據庫？**
A: 檢查 SQL Server 是否運行，確認 `.env` 配置正確

**Q: Line Login 失敗？**
A: 確認 Channel ID/Secret 正確，Callback URL 已在 Line 後台設置

**Q: API 請求失敗？**
A: 檢查後端是否啟動，確認 API_BASE_URL 配置正確

**Q: 前端頁面無法訪問？**
A: 使用 HTTP 服務器運行前端，或調整瀏覽器 CORS 設置

## 🎉 MVP 完成！

恭喜！您已經擁有一個功能完整的 1v1 辯論平台最小可行性方案。

現在可以：
- ✅ 開始測試所有功能
- ✅ 邀請用戶體驗
- ✅ 收集反饋意見
- ✅ 規劃下一階段功能

## 📈 後續優化建議

1. **用戶體驗**: 優化前端界面，增加動畫效果
2. **通知系統**: 增加電子郵件或推播通知
3. **即時功能**: 使用 WebSocket 實現即時更新
4. **數據分析**: 增加統計圖表和數據分析
5. **社交功能**: 增加好友系統和私訊功能
6. **移動應用**: 開發 iOS/Android App
7. **性能優化**: 增加緩存和資料庫優化
8. **安全強化**: 增加防作弊和反垃圾機制

祝使用愉快！🚀
