# 管理員帳號管理指南

## 📋 目錄
1. [概述](#概述)
2. [前置條件](#前置條件)
3. [方法一：使用命令列工具（推薦）](#方法一使用命令列工具推薦)
4. [方法二：使用 SQL 腳本](#方法二使用-sql-腳本)
5. [方法三：使用 Python 腳本](#方法三使用-python-腳本)
6. [驗證管理員權限](#驗證管理員權限)

---

## 概述

管理員帳號可以：
- ✅ 審核辯論話題
- ✅ 管理使用者
- ✅ 強制結束辯論
- ✅ 分配法官
- ✅ 訪問管理後台

**重要**：使用者必須先透過 Line Login 登入一次，才能在資料庫中有記錄。

---

## 前置條件

1. **使用者已註冊**：使用者必須至少登入過一次
2. **資料庫連接正常**：確保 `.env` 中的資料庫設定正確
3. **Python 環境已設置**：虛擬環境已啟動（如果使用 Python 方法）

---

## 方法一：使用命令列工具（推薦）

### 🚀 最簡單的方式

#### 1. 列出所有使用者
```cmd
admin.bat list
```

輸出示例：
```
📋 使用者列表:
----------------------------------------------------------------------------------------------------
ID    LINE ID              暱稱                  Rating   管理員    建立時間
----------------------------------------------------------------------------------------------------
1     U1234567890abcdef    張三                  1500     ❌ 否     2025-10-03 10:30:00
2     U0987654321fedcba    李四                  1500     ❌ 否     2025-10-03 11:00:00
----------------------------------------------------------------------------------------------------
總共 2 位使用者
```

#### 2. 設置管理員
```cmd
admin.bat set 1
```

輸出：
```
✅ 成功將使用者 '張三' (ID: 1) 設置為管理員
```

#### 3. 移除管理員權限
```cmd
admin.bat remove 1
```

#### 4. 透過 LINE ID 設置管理員
```cmd
admin.bat set-line U1234567890abcdef
```

---

## 方法二：使用 SQL 腳本

### 📝 適合熟悉 SQL 的使用者

#### 1. 開啟 SQL Server Management Studio (SSMS)

#### 2. 連接到你的資料庫
```
Server: localhost\SQLEXPRESS
Database: DebatePlatform
```

#### 3. 開啟 SQL 腳本
打開檔案：`database\manage_admin.sql`

#### 4. 執行查詢找到使用者
```sql
SELECT 
    user_id,
    line_id,
    nickname,
    rating,
    CASE WHEN is_admin = 1 THEN '✓ 是' ELSE '✗ 否' END AS 管理員
FROM Users
ORDER BY created_at DESC;
```

#### 5. 設置管理員
```sql
-- 方法 A：透過 User ID
UPDATE Users 
SET is_admin = 1 
WHERE user_id = 1;

-- 方法 B：透過 LINE ID
UPDATE Users 
SET is_admin = 1 
WHERE line_id = 'U1234567890abcdef';

-- 方法 C：透過暱稱
UPDATE Users 
SET is_admin = 1 
WHERE nickname = '張三';
```

#### 6. 驗證
```sql
SELECT * FROM Users WHERE is_admin = 1;
```

---

## 方法三：使用 Python 腳本

### 🐍 適合需要程式化管理的情況

#### 1. 進入 backend 目錄
```cmd
cd backend
```

#### 2. 啟動虛擬環境（如果有）
```cmd
venv\Scripts\activate
```

#### 3. 執行 Python 腳本

**列出所有使用者：**
```cmd
python manage_admin.py --list
```

**設置管理員：**
```cmd
python manage_admin.py --set-admin 1
```

**移除管理員：**
```cmd
python manage_admin.py --remove-admin 1
```

**透過 LINE ID 設置：**
```cmd
python manage_admin.py --set-admin-by-line U1234567890abcdef
```

---

## 驗證管理員權限

### 方法 1：透過 API

訪問登入頁面並登入後，檢查 localStorage：

1. 打開瀏覽器開發者工具（F12）
2. 切換到「應用程式」或「Application」標籤
3. 查看 localStorage 中的 `current_user`
4. 確認 `is_admin: true`

### 方法 2：訪問管理後台

登入後訪問：
```
http://localhost:8080/pages/admin.html
```

如果可以訪問，表示管理員權限設置成功。

### 方法 3：檢查導航欄

登入後，導航欄應該會顯示「管理後台」連結。

---

## 🎯 快速開始流程

### 第一次設置管理員

1. **使用 Line Login 登入網站**
   ```
   訪問 http://localhost:8080/pages/login.html
   點擊「使用 Line 登入」
   ```

2. **列出使用者，找到你的 User ID**
   ```cmd
   admin.bat list
   ```

3. **設置為管理員**
   ```cmd
   admin.bat set 1
   ```
   （將 `1` 替換為你的實際 User ID）

4. **重新整理網頁**
   按 `Ctrl + F5` 強制重新整理

5. **訪問管理後台**
   ```
   http://localhost:8080/pages/admin.html
   ```

---

## 🔧 故障排除

### 問題 1：找不到使用者
**原因**：使用者尚未登入過  
**解決**：先訪問網站並使用 Line Login 登入

### 問題 2：Python 腳本執行錯誤
**原因**：虛擬環境未啟動或資料庫連接失敗  
**解決**：
```cmd
cd backend
venv\Scripts\activate
python manage_admin.py --list
```

### 問題 3：SQL 連接失敗
**原因**：資料庫服務未啟動  
**解決**：確認 SQL Server 服務正在運行

### 問題 4：設置後仍無權限
**原因**：瀏覽器快取  
**解決**：
1. 清除快取或按 Ctrl+F5
2. 登出後重新登入
3. 檢查 localStorage 是否更新

---

## 📝 注意事項

1. **安全性**：不要在生產環境中使用簡單的工具，應該有更嚴格的權限控制
2. **備份**：修改前建議備份資料庫
3. **謹慎操作**：管理員權限很高，不要隨意給予
4. **測試環境**：建議先在測試環境中操作

---

## 🔗 相關文件

- 資料庫 Schema：`database/schema.sql`
- 管理員 API：`backend/app/routes/admin.py`
- 權限驗證：`backend/app/utils/auth.py`