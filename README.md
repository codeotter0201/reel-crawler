# Reel Crawler

Facebook Reel 爬蟲工具，專門用於擷取 Reel 影片的相關資訊，包含影片內容、互動數據、留言及標籤等資料。

## 功能特點

- 自動化擷取 Facebook Reel 資訊
- 支援批次處理多個 Reel 網址
- 完整擷取留言及回覆內容
- 自動展開所有回覆及載入更多留言
- 支援標籤及使用者資訊提取

## 環境需求

- Python `3.12`
- 主要依賴套件：
  ```toml
  pydantic >= 2.0
  pydantic-settings >= 2.2.1, < 3.0.0
  selenium == 4.29.0
  beautifulsoup4 == 4.13.3
  ```

## 快速開始

### 1. 安裝專案

```bash
git clone https://github.com/codeotter0201/reel-crawler.git
```

### 2. 安裝套件管理工具

請先安裝 [uv](https://docs.astral.sh/uv/getting-started/installation/)

### 3. 設定環境

```bash
# 安裝依賴套件
uv sync

# 設定環境變數
cp .env.example .env
```

環境變數設定範例：

```env
USER_EMAIL=your_facebook_email@gmail.com
USER_PASSWORD=your_facebook_password

# driver 預設資料夾名稱，不需調整，可自行修改
WEB_DRIVER_PATH=user_data
```

### 4. 初次使用設定

1. 手動登入 Facebook
2. 完成裝置驗證
3. 關閉瀏覽器

### 5. 執行爬蟲

```bash
uv run app/main.py <reel_url1> <reel_url2> ...
```

## 專案結構

### 核心模組

- `config.py`：管理敏感資訊
- `main.py`：程式進入點，處理參數及協調執行流程
- `page_actions.py`：頁面互動操作（登入、滾動、點擊等）
- `page_parser.py`：頁面內容解析（標籤、描述、數據提取）
- `webdriver_setup.py`：Selenium WebDriver 設定
- `models.py`：資料模型定義（使用 Pydantic）
- `utils.py`：通用工具函式

## 執行流程

1. Facebook 登入驗證
2. 跳轉至指定 Reel
3. 資料擷取流程：
   - 影片內容及標籤提取
   - 留言及回覆展開
   - 使用者資訊擷取
   - 互動數據收集

## 支援的 Reel 類型

- 一般貼文（含/不含賞星星按鈕）
- Instagram 轉發貼文
- 廣告貼文
- 無留言貼文

### 測試範例

```python
# 一般貼文（含賞星星）
"https://www.facebook.com/reel/1261058915181865"
"https://www.facebook.com/reel/1710788673178979"

# 一般貼文（無賞星星）
"https://www.facebook.com/reel/976095654399185"
"https://www.facebook.com/reel/8712802535486571"

# Instagram 轉發
"https://www.facebook.com/reel/968163031712451"

# 廣告貼文
"https://www.facebook.com/reel/1313719486554645"

# 無留言一般貼文
"https://www.facebook.com/reel/1529668634395562"
```

## 資料存取

### 資料儲存

爬取的資料會自動儲存至 `download_data/data.pkl`，包含所有 Reel 的相關資訊：

- 影片基本資訊
- 互動數據
- 留言內容
- 使用者資料
- 標籤資訊

### 資料讀取

使用以下方式讀取已下載的資料：

```python
from app.utils import load_reels

# 讀取所有已下載的 Reel 資料
reels = load_reels()
```

## 待優化項目

1. 效能優化

   - 將 `time.sleep` 改為等待渲染機制
   - 優化 `page_actions.py` 使用 ActionChain
   - 執行動作後的延遲改為隨機數

2. 程式架構優化

   - 重構 xpath 定位方式
   - 將重要 xpath 路徑抽出至設定檔
   - 環境變數統一管理
   - 使用 enum 判斷 Reel 類型

3. 測試與維護

   - 撰寫 pytest 測試案例
   - 模擬各種類型貼文的測試情境

4. 功能優化
   - 支援長留言的「查看全部」展開功能
