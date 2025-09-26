# -*- coding: utf-8 -*-
"""
自定義摘要鏈模組 (Custom Summarize Chain Module)

本模組負責創建結構化的文檔摘要，主要功能包括：
1. 使用 Pydantic 模型定義摘要結構
2. 利用 LLM 生成高品質摘要
3. 提取關鍵點和專家觀點
4. 支持並行處理多個文檔
5. 強制繁體中文輸出

作者: AI Content Generation System
創建日期: 2024
"""

import asyncio
from langchain_openai.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pydantic import BaseModel
from langchain.chains import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from typing import Dict, List, Optional, Union
import time
from langchain_core.prompts import PromptTemplate


class DocumentSummary(BaseModel):
    """
    文檔摘要結構化模型

    使用 Pydantic 定義的資料模型，用於標準化文檔摘要的輸出格式。
    確保所有摘要都包含必要的結構化信息。

    Attributes:
        concise_summary (str): 簡潔的文檔摘要
        writing_style (str): 文章的寫作風格分析
        key_points (List[str]): 關鍵要點列表
        expert_opinions (Optional[List[str]]): 專家觀點列表，可選
        metadata (Optional[Dict[str, str]]): 文檔元數據，來自 LangChain 文檔載入器
    """
    concise_summary: str
    writing_style: str
    key_points: List[str]
    expert_opinions: Optional[List[str]] = None
    metadata: Optional[
        Dict[str, str]
    ] = {}  # 這些元數據來自 LangChain 文檔載入器


async def create_summary_from_text(
    document: Document,
    parser: PydanticOutputParser,
    llm: ChatOpenAI,
    text_splitter: RecursiveCharacterTextSplitter,
) -> Union[DocumentSummary, None]:
    """
    從單個文檔創建結構化摘要

    使用 LLM 分析文檔內容，提取關鍵信息並生成結構化摘要。
    採用 StuffDocumentsChain 策略處理文檔內容。

    Args:
        document (Document): 要摘要的 LangChain 文檔
        parser (PydanticOutputParser): Pydantic 輸出解析器
        llm (ChatOpenAI): OpenAI 聊天模型實例
        text_splitter (RecursiveCharacterTextSplitter): 文本分割器

    Returns:
        Union[DocumentSummary, None]: 結構化摘要物件，如果處理失敗則返回 None
    """
    # 將文檔分割成較小的片段以便處理
    split_docs = text_splitter.split_documents([document])

    # 如果分割後沒有文檔，返回 None
    if len(split_docs) == 0:
        return None

    # 取得第一個文檔片段進行摘要（通常是最重要的部分）
    first_document = split_docs[0]

    # 定義用於摘要的提示模板，強制繁體中文輸出
    prompt_template = """
    所有內容必須以繁體中文輸出。
    作為內容 SEO 研究員，你需要總結並提取以下文本的關鍵點。
    獲得的見解將用於內容研究，我們將比較多篇文章的關鍵點、見解和摘要。
    ---
    - 你必須分析文本並從以下文本中提取關鍵點和觀點
    - 你必須從以下文本中提取關鍵點和觀點：
    {text}
    {format_instructions}
    """

    # 建立 LLM 鏈，使用 GPT-5 模型確保高品質輸出
    llm = ChatOpenAI(temperature=0, model="gpt-5")
    llm_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))

    print("開始生成文檔摘要...")

    # 記錄處理開始時間
    start_time = time.time()

    # 建立文檔處理鏈
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="text",  # 文檔內容的變數名
    )

    # 非同步執行摘要生成
    summary_result = await stuff_chain.ainvoke(
        {
            "input_documents": [first_document],
            "format_instructions": parser.get_format_instructions(),
        },
    )

    # 輸出處理時間
    print(f"處理時間: {time.time() - start_time:.2f} 秒")
    print("文檔摘要生成完成！\n---")

    # 解析 LLM 輸出為結構化物件
    document_summary = parser.parse(summary_result["output_text"])
    # 保留原始文檔的元數據
    document_summary.metadata = document.metadata

    return document_summary


async def create_all_summaries(
    text_documents: List[Document],
    parser: PydanticOutputParser,
    llm: ChatOpenAI,
    text_splitter: RecursiveCharacterTextSplitter,
) -> List[DocumentSummary]:
    """
    並行創建多個文檔的摘要

    使用 asyncio 並行處理多個文檔，提高處理效率。
    每個文檔都會生成一個結構化摘要。

    Args:
        text_documents (List[Document]): 要處理的文檔列表
        parser (PydanticOutputParser): Pydantic 輸出解析器
        llm (ChatOpenAI): OpenAI 聊天模型實例
        text_splitter (RecursiveCharacterTextSplitter): 文本分割器

    Returns:
        List[DocumentSummary]: 結構化摘要列表

    Raises:
        ValueError: 當沒有成功創建任何摘要時拋出異常
    """
    # 為每個文檔創建非同步任務
    tasks = [
        create_summary_from_text(document, parser, llm, text_splitter)
        for document in text_documents
    ]

    print(f"開始並行處理 {len(tasks)} 個文檔的摘要生成...")

    # 並行執行所有任務並收集結果
    results = await asyncio.gather(*tasks)

    # 過濾掉 None 值（處理失敗的文檔）
    summaries = [summary for summary in results if summary is not None]

    # 檢查是否有成功創建的摘要
    if len(summaries) == 0:
        raise ValueError("沒有成功創建任何摘要！請檢查輸入文檔和 API 配置。")

    print(f"成功創建了 {len(summaries)} 個文檔摘要")
    return summaries
