# 文件名：wsgi.py
"""
功能说明：Gunicorn WSGI 入口文件
核心功能：
1. 暴露 WSGI application 对象给 Gunicorn
2. 执行 Gevent Monkey Patching (尽早执行)
"""
from gevent import monkey
monkey.patch_all()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
