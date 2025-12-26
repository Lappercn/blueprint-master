# 文件名：__init__.py
"""
功能说明：Flask应用工厂
核心功能：初始化Flask应用，注册蓝图，配置CORS
"""
from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import mongo
from .api.blueprint_api import blueprint_bp
# 导入新增的 API
from .api.auth_api import auth_bp
from .api.feedback_api import feedback_bp
from .api.dashboard_api import dashboard_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    mongo.init_app(app)
    
    # 启用 CORS (允许所有来源，根据需求调整)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    # 所有 API 统一前缀 /api/v1
    app.register_blueprint(blueprint_bp, url_prefix='/api/v1/blueprint')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(feedback_bp, url_prefix='/api/v1/feedback')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    
    return app
