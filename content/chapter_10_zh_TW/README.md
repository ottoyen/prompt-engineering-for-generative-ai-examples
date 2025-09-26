# AI 智能部落格生成系統

基於 Gradio、LangChain 和 OpenAI 構建的智能內容生成應用程式

## 系統概述

本系統是一個完整的 AI 驅動部落格內容生成平臺，能夠自動化創建高品質的繁體中文部落格文章。系統整合了網路搜尋、內容摘要、專家訪談模擬、文章大綱生成和圖像創建等功能，提供端對端的內容創作解決方案。

## 核心功能

### 🔍 智能內容收集
- 使用 SerpAPI 進行主題相關的網路搜尋
- 基於 Playwright 的高效網頁內容抓取
- 自動將 HTML 內容轉換為可處理的文本文檔

### 📄 文檔智能處理
- AI 驅動的內容摘要生成
- 結構化文檔分析和關鍵信息提取
- 基於主題的專家訪談問題生成

### ✍️ 內容創作流程
- 智能文章大綱規劃
- RAG（檢索增強生成）架構的內容生成
- 記憶機制避免內容重複
- 強制繁體中文輸出

### 🎨 視覺內容創建
- 圖像生成 API 整合
- 自動配圖生成

## 技術架構

```
用戶輸入主題 → 網路搜尋 → 內容抓取 → 文檔摘要 → 專家訪談 → 大綱生成 → 內容創作 → 圖像生成
```

### 核心組件

- **content_collection.py**: 網路內容收集和預處理
- **custom_summarize_chain.py**: 結構化摘要生成鏈
- **expert_interview_chain.py**: 專家訪談問題生成
- **article_outline_generation.py**: 文章大綱智能規劃
- **article_generation.py**: RAG 架構內容生成器
- **image_generation_chain.py**: 圖像生成處理
- **gradio_code_example.py**: Gradio 用戶界面主程式

## 安裝與設定

### 環境需求
- Python 3.8+
- pip Package管理器

### 安裝步驟

1. 複製專案
```bash
git clone <repository-url>
cd chapter_10_zh_TW
```

2. 安裝相依性
```bash
pip install -r requirements.txt
```

3. 設定環境變數
```bash
export SERPAPI_API_KEY="your_serpapi_key"
export OPENAI_API_KEY="your_openai_key"
export STABILITY_API_KEY="your_STABILITY_API_key"
```

### 必要 API 金鑰

- **SERPAPI_API_KEY**: 用於 Google 搜尋結果獲取
- **OPENAI_API_KEY**: 用於 LLM 操作
- **STABILITY_API_KEY**: 用於圖像生成

## 使用方式

### 啟動主應用程式
```bash
python gradio_code_example.py
```

### 啟動簡易演示
```bash
python hello.py
```

## 系統操作流程

1. **輸入主題**: 在 Gradio 界面中輸入要創建部落格的主題
2. **內容收集**: 點擊「Summarize and Generate Questions」開始內容收集
3. **專家訪談**: 回答系統生成的專家訪談問題
4. **生成內容**: 點擊「Generate Blog Post & Image」創建最終內容
5. **獲取結果**: 系統將輸出完整的繁體中文部落格文章和配圖

## 主要依賴套件

- **LangChain**: 核心 LLM 框架和文檔處理
- **Gradio**: 網路用戶界面框架
- **OpenAI**: 大語言模型和圖像生成
- **STABILITY**: 圖像生成
- **ChromaDB**: 向量資料庫用於 RAG
- **Playwright**: 網頁內容抓取
- **SerpAPI**: Google 搜尋結果 API
- **Pydantic**: 資料驗證和序列化

## 技術特色

### RAG 架構
- 使用 ChromaDB 向量資料庫
- 智能文檔檢索和相關性排序
- 上下文感知的內容生成

### 記憶機制
- 自定義 ConversationSummaryBufferMemory
- 避免內容重複和提升一致性
- 支持長文檔的分段處理

### 多語言支持
- 系統提示強制繁體中文輸出
- 支持多種語言輸入主題
- 本地化的用戶界面

## 故障排除

### 常見問題

1. **API 金鑰錯誤**
   - 確認環境變數已正確設定
   - 驗證 API 金鑰的有效性和權限

2. **搜尋結果為空**
   - 檢查 SERPAPI_API_KEY 是否有效
   - 確認網路連接正常

3. **內容生成失敗**
   - 驗證 OPENAI_API_KEY 配置
   - 檢查 OpenAI API 使用額度

## 授權條款

本專案遵循開源授權條款，詳細信息請參閱 LICENSE 文件。

## 貢獻指南

歡迎提交 Pull Request 和 Issue。在貢獻代碼前，請確保：
- 遵循現有的程式碼風格
- 添加適當的註釋和文檔
- 測試新功能的穩定性
