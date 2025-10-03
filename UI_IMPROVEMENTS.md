# UI 改進說明

## 🎨 文字選取控制

### 問題
網頁上的所有文字都可以被選取，滑鼠點擊時會顯示文字游標，看起來不夠專業和美觀。

### 解決方案
在 `frontend/static/css/styles.css` 中添加了全局文字選取控制：

#### 1. 禁止一般元素的文字選取
```css
* {
    -webkit-user-select: none; /* Safari */
    -moz-user-select: none; /* Firefox */
    -ms-user-select: none; /* IE10+/Edge */
    user-select: none; /* Standard */
}
```

#### 2. 允許必要元素的文字選取
```css
/* 表單元素 */
input,
textarea,
[contenteditable="true"],
.selectable {
    user-select: text;
}

/* 內容區域（方便使用者複製辯論內容）*/
.debate-content,
.round-content,
.statement-text,
.reply-text,
pre,
code {
    user-select: text;
}
```

#### 3. 改進游標樣式
```css
/* 可點擊元素顯示 pointer 游標 */
button,
a,
[onclick],
[role="button"] {
    cursor: pointer;
}
```

### 效果

#### ✅ 一般文字（禁止選取）
- 導航欄文字
- 按鈕文字
- 標題和標籤
- 狀態徽章
- 用戶暱稱和評分

**優點**：
- 看起來更像應用程式，而不是網頁文件
- 防止意外選取文字
- 整體更美觀專業

#### ✅ 可選取文字（允許選取）
- 輸入框內容
- 文字區域內容
- 辯論陳述和回覆內容
- 程式碼區塊

**優點**：
- 使用者可以複製重要的辯論內容
- 表單輸入正常運作
- 不影響功能性

#### ✅ 游標樣式
- 可點擊元素：顯示手指游標（pointer）
- 文字輸入：顯示文字游標（text）
- 一般區域：預設箭頭游標（default）

## 🔧 如何自訂

### 如果需要讓某個元素可選取
在 HTML 中添加 `selectable` class：
```html
<div class="selectable">這段文字可以被選取</div>
```

### 如果需要讓某個元素不可選取
在元素的 style 中添加：
```html
<div style="user-select: none;">這段文字不能被選取</div>
```

## 📱 瀏覽器支援
- ✅ Chrome/Edge (現代版本)
- ✅ Firefox (現代版本)
- ✅ Safari (現代版本)
- ✅ 使用 vendor prefixes 確保最大兼容性

## 🎯 使用建議

### 應該禁止選取的元素
- 導航選單
- 按鈕和連結的文字
- UI 標籤和徽章
- 裝飾性文字
- 統計數字和評分顯示

### 應該允許選取的元素
- 表單輸入（input, textarea）
- 長篇內容（文章、評論、辯論內容）
- 程式碼範例
- 需要複製的資訊（ID、連結等）

## 🔄 測試清單

重新載入網站後，測試以下項目：

- [ ] 導航欄文字不能被選取 ✅
- [ ] 按鈕文字不能被選取 ✅
- [ ] 可點擊元素顯示手指游標 ✅
- [ ] 輸入框可以正常輸入和選取文字 ✅
- [ ] 辯論內容可以被選取和複製 ✅
- [ ] 整體外觀更專業美觀 ✅

## 📝 注意事項

1. **不要過度使用**：確保真正需要複製的內容（如辯論陳述）仍然可以選取
2. **測試功能**：確認所有表單輸入功能正常
3. **考慮無障礙性**：螢幕閱讀器仍然可以讀取所有文字
4. **行動裝置**：這些設定也適用於觸控設備，防止長按時出現選取框
