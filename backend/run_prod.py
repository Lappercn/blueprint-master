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
    # host: 监听地址 (0.0.0.0 表示允许外部访问，但在有Nginx/Node代理的情况下，也可以设为127.0.0.1)
    # 这里设为 127.0.0.1 因为我们计划通过前端 Node 服务代理转发
    serve(app, host='127.0.0.1', port=5000, threads=6)
