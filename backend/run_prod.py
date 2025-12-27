# 文件名：run_prod.py
"""
功能说明：生产环境启动脚本
核心功能：使用Waitress作为WSGI服务器启动应用
依赖模块：app, waitress
"""
from app import create_app
from waitress import serve
import logging

# 初始化应用
app = create_app()

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('waitress')
    logger.info("Starting Blueprint Master Backend on port 5000...")
    
    # 启动Waitress服务器
    # threads: 处理请求的线程数
    # host: 监听地址 (0.0.0.0 表示允许外部访问；如仅本机反代可使用 127.0.0.1)
    # 生产部署需要外部访问时，建议使用 0.0.0.0
    # channel_timeout: 连接保持时间，默认为120s。生成蓝图需要较长时间，需调大。
    serve(app, host='0.0.0.0', port=5000, threads=6, channel_timeout=600)
