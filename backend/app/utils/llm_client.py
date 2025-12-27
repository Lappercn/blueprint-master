# 文件名：llm_client.py
"""
功能说明：LLM客户端工具类
核心功能：调用OpenAI接口（支持豆包等）进行对话生成
依赖模块：openai
"""
import logging
from typing import List, Dict, Generator, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMClient:
    """
    通用LLM客户端，基于OpenAI SDK
    """
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        初始化 LLM 客户端
        :param api_key: API Key
        :param base_url: API Base URL
        :param model: 模型名称
        """
        if not api_key or not base_url:
            raise ValueError("api_key and base_url are required")
            
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=600.0,  # 显式设置超时时间，匹配 Nginx 和 Waitress 配置
            max_retries=3   # 增加自动重试机制
        )
        self.model = model

    def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Generator[str, None, None]:
        """
        流式对话生成
        :param messages: 对话历史 [{"role": "user", "content": "..."}]
        :param temperature: 温度参数
        :return: 生成器，产生流式文本块
        """
        try:
            logger.info(f"Sending request to LLM model: {self.model}")
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=temperature
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"LLM request failed: {str(e)}")
            # 这里抛出异常，让上层处理（比如返回给前端错误信息）
            raise e
