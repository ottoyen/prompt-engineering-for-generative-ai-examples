# -*- coding: utf-8 -*-
"""
內容收集模組 (Content Collection Module)

本模組負責從網路搜尋結果中收集和處理內容，主要功能包括：
1. 使用 SerpAPI 進行 Google 搜尋
2. 從搜尋結果中提取網頁 URL
3. 使用 Playwright 抓取網頁內容
4. 將 HTML 內容轉換為純文字格式

作者: AI Content Generation System
創建日期: 2024
"""

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
import os
import pandas as pd
from serpapi import GoogleSearch
from typing import List


class ChromiumLoader(AsyncChromiumLoader):
    """
    自定義 Chromium 載入器類別

    繼承自 AsyncChromiumLoader，用於非同步載入網頁內容。
    使用 Playwright 引擎進行網頁抓取，支援現代 JavaScript 渲染。
    """

    async def load(self):
        """
        非同步載入網頁內容

        Returns:
            List[Document]: 包含網頁內容的文檔列表
        """
        # 使用 Playwright 非同步抓取所有 URL 的內容
        raw_text = [await self.ascrape_playwright(url) for url in self.urls]
        # 將原始文本轉換為 LangChain Document 格式
        return [Document(page_content=text) for text in raw_text]


async def get_html_content_from_urls(
    df: pd.DataFrame, number_of_urls: int = 3, url_column: str = "link"
) -> List[Document]:
    """
    從 DataFrame 中提取 URL 並獲取網頁內容

    Args:
        df (pd.DataFrame): 包含 URL 的 DataFrame
        number_of_urls (int): 要處理的 URL 數量，預設為 3
        url_column (str): URL 所在的欄位名稱，預設為 "link"

    Returns:
        List[Document]: 包含網頁內容的文檔列表

    Raises:
        ValueError: 當找不到有效的 URL 時拋出異常
    """
    # 從 DataFrame 中提取指定數量的 URL
    urls = df[url_column].values[:number_of_urls].tolist()

    # 如果只有一個 URL，確保轉換為列表格式
    if isinstance(urls, str):
        urls = [urls]

    # 過濾掉空的 URL
    urls = [url for url in urls if url != ""]

    # 移除重複的 URL
    urls = list(set(urls))

    # 如果沒有找到有效的 URL，拋出錯誤
    if len(urls) == 0:
        raise ValueError("找不到有效的 URL！")

    # 使用 ChromiumLoader 而不是 AsyncHtmlLoader，因為更穩定
    # loader = AsyncHtmlLoader(urls) # 速度更快但可能不穩定
    loader = ChromiumLoader(urls)
    docs = await loader.load()
    return docs


def extract_text_from_webpages(documents: List[Document]):
    """
    從網頁文檔中提取純文字內容

    將 HTML 格式的文檔轉換為純文字格式，去除 HTML 標籤和樣式。

    Args:
        documents (List[Document]): 包含 HTML 內容的文檔列表

    Returns:
        List[Document]: 轉換後的純文字文檔列表
    """
    # 初始化 HTML 轉文字轉換器
    html2text = Html2TextTransformer()
    # 執行文檔轉換
    return html2text.transform_documents(documents)


async def collect_serp_data_and_extract_text_from_webpages(
    topic: str,
) -> List[Document]:
    """
    收集搜尋引擎結果並提取網頁文字內容

    這是主要的內容收集函數，整合了以下流程：
    1. 使用 SerpAPI 搜尋指定主題
    2. 提取搜尋結果中的網頁 URL
    3. 抓取網頁 HTML 內容
    4. 轉換為純文字格式

    Args:
        topic (str): 搜尋主題關鍵字

    Returns:
        List[Document]: 包含提取文字的文檔列表

    Raises:
        ValueError: 當 API 金鑰未設定或搜尋失敗時拋出異常
    """
    # 從環境變數中獲取 SERPAPI API 金鑰
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY 環境變數未設定")

    # 初始化 Google 搜尋物件
    search = GoogleSearch(
        {
            "q": topic,  # 搜尋關鍵字
            "location": "Austin,Texas",  # 搜尋地理位置
            "api_key": api_key,  # API 金鑰
        }
    )

    # 執行搜尋並獲取結果
    result = search.get_dict()

    # 檢查搜尋結果是否有錯誤
    if "error" in result:
        raise ValueError(f"SERPAPI 錯誤: {result['error']}")

    # 檢查是否有有機搜尋結果
    if "organic_results" not in result or not result["organic_results"]:
        raise ValueError("沒有找到搜尋結果，請檢查 API 金鑰是否有效")

    # 將搜尋結果轉換為 Pandas DataFrame 以便處理
    serp_results = pd.DataFrame(result["organic_results"])

    # 從 URL 中提取 HTML 內容
    html_documents = await get_html_content_from_urls(serp_results)

    # 將 HTML 內容轉換為純文字
    text_documents = extract_text_from_webpages(html_documents)

    return text_documents
