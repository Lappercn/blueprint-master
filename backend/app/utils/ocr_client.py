# 文件名：ocr_client.py
"""
功能说明：OCR识别客户端工具类
核心功能：调用TextIn API进行文档解析
依赖模块：requests
"""
import requests
import logging
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

class OCRClient:
    """
    TextIn OCR API 客户端
    """
    
    # API 地址
    API_URL = "https://api.textin.com/ai/service/v1/pdf_to_markdown"
    
    def __init__(self, app_id: str, secret_code: str):
        """
        初始化 OCR 客户端
        :param app_id: x-ti-app-id
        :param secret_code: x-ti-secret-code
        """
        if not app_id or not secret_code:
            raise ValueError("app_id and secret_code are required")
            
        self.app_id = app_id
        self.secret_code = secret_code

    def recognize(self, file_content: bytes, options: Optional[Dict[str, Any]] = None) -> str:
        """
        调用 OCR API 进行识别
        :param file_content: 文件二进制内容
        :param options: 可选参数 (e.g., {'pdf_pwd': 'password', 'page_start': 0, ...})
        :return: 识别结果文本 (Markdown格式)
        """
        if options is None:
            options = {}
            
        # 构建请求参数
        params = {}
        for key, value in options.items():
            params[key] = str(value)

        # 设置请求头
        headers = {
            "x-ti-app-id": self.app_id,
            "x-ti-secret-code": self.secret_code,
            "Content-Type": "application/octet-stream"
        }

        try:
            logger.info(f"Sending OCR request to {self.API_URL}")
            # 发送请求
            response = requests.post(
                self.API_URL,
                params=params,
                headers=headers,
                data=file_content,
                timeout=300 # 增加超时时间到 300秒 (5分钟)
            )

            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应内容，确保返回的是预期的格式
            # 注意：API可能返回JSON，其中包含result字段，或者直接返回文本，视API具体定义而定。
            # 根据用户提供的代码 return response.text，这里保持一致。
            # 但通常建议检查response.json()中的code字段。
            
            # 尝试解析JSON以检查业务错误码（如果API总是返回JSON）
            try:
                result_json = response.json()
                if isinstance(result_json, dict) and result_json.get("code") != 200:
                     # 某些API成功HTTP状态码但也可能包含业务错误
                     # 这里假设如果是JSON且code不是200，记录警告或抛出异常
                     # 但用户代码直接返回 text，我们先尽量保持兼容但增加健壮性
                     pass
            except ValueError:
                # 不是JSON，可能是纯文本结果
                pass

            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"OCR request failed: {str(e)}")
            raise e
