# 文件名：auth_api.py
"""
功能说明：用户认证API
核心功能：用户注册/登录（基于用户名 + 浏览器指纹）
依赖模块：flask, pymongo
"""
from flask import Blueprint, request, jsonify
from app.extensions import mongo
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/v1/auth/login
    参数：
      - username: 中文姓名
      - fingerprint: 浏览器指纹
    逻辑：
      1. 如果用户名不存在 -> 注册新用户 (绑定指纹)
      2. 如果用户名存在：
         - 指纹匹配 -> 登录成功
         - 指纹不匹配 -> 登录失败 (用户名已被占用)
    """
    data = request.json
    username = data.get('username')
    fingerprint = data.get('fingerprint')

    if not username or not fingerprint:
        return jsonify({"code": 400, "message": "Username and fingerprint are required", "data": None}), 400

    users_collection = mongo.db.users
    
    # 查找用户
    user = users_collection.find_one({"username": username})

    if user:
        # 用户已存在，允许任意指纹登录（多端登录）
        # 更新指纹信息和最后登录时间
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "last_login": datetime.utcnow(),
                "fingerprint": fingerprint # 更新为当前设备的指纹
            }}
        )
        return jsonify({
            "code": 200, 
            "message": "Login success", 
            "data": {
                "user_id": str(user["_id"]),
                "username": user["username"]
            }
        })
    else:
        # 用户不存在，注册新用户
        new_user = {
            "username": username,
            "fingerprint": fingerprint,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        result = users_collection.insert_one(new_user)
        return jsonify({
            "code": 200, 
            "message": "Register success", 
            "data": {
                "user_id": str(result.inserted_id),
                "username": username
            }
        })
