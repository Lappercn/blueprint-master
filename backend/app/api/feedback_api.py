# 文件名：feedback_api.py
"""
功能说明：用户反馈API
核心功能：提交反馈
依赖模块：flask, pymongo
"""
from flask import Blueprint, request, jsonify
from app.extensions import mongo
from datetime import datetime
import logging

feedback_bp = Blueprint('feedback', __name__)
logger = logging.getLogger(__name__)

@feedback_bp.route('/submit', methods=['POST'])
def submit_feedback():
    """
    POST /api/v1/feedback/submit
    参数：
      - user_id: 用户ID (可选)
      - username: 用户名 (可选)
      - content: 反馈内容
    """
    data = request.json
    content = data.get('content')
    user_id = data.get('user_id')
    username = data.get('username')

    if not content:
        return jsonify({"code": 400, "message": "Content is required", "data": None}), 400

    feedback_collection = mongo.db.feedbacks
    
    new_feedback = {
        "user_id": user_id,
        "username": username,
        "content": content,
        "created_at": datetime.utcnow()
    }
    
    feedback_collection.insert_one(new_feedback)

    return jsonify({"code": 200, "message": "Feedback submitted successfully", "data": None})
