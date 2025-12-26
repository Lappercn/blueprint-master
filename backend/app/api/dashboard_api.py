# 文件名：dashboard_api.py
"""
功能说明：仪表盘统计API
核心功能：
1. 获取书籍使用排行榜
2. 获取用户活跃统计
依赖模块：flask, pymongo
"""
from flask import Blueprint, jsonify
from app.extensions import mongo
import logging

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/stats/books', methods=['GET'])
def get_book_stats():
    """
    GET /api/v1/dashboard/stats/books
    获取书籍使用排行榜 (Top 10)，支持按角色筛选
    """
    try:
        pipeline = [
            {"$match": {"role": "all"}}, # 默认只查总榜，暂不前端筛选
            {"$sort": {"count": -1}},
            {"$limit": 10},
            {"$project": {"_id": 0, "book_name": 1, "count": 1}}
        ]
        
        # 聚合每个角色的 Top 书籍
        roles = ['cxo', 'iron_triangle', 'pdt_manager', 'cio', 'ar', 'sr', 'fr', 'pdt', 'cfo', 'supply', 'hr']
        role_stats = {}
        
        # 获取总榜
        total_books = list(mongo.db.book_stats.aggregate(pipeline))
        role_stats['all'] = total_books
        
        # 获取各角色榜单
        for role in roles:
             role_pipeline = [
                {"$match": {"role": role}},
                {"$sort": {"count": -1}},
                {"$limit": 5}, # 角色榜单只取前5
                {"$project": {"_id": 0, "book_name": 1, "count": 1}}
            ]
             role_books = list(mongo.db.book_stats.aggregate(role_pipeline))
             if role_books:
                 role_stats[role] = role_books

        return jsonify({"code": 200, "message": "success", "data": role_stats})
    except Exception as e:
        logger.error(f"Error fetching book stats: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": {}}), 500

@dashboard_bp.route('/stats/users', methods=['GET'])
def get_user_stats():
    """
    GET /api/v1/dashboard/stats/users
    获取用户活跃度统计 (最近24小时活跃用户数，总用户数，活跃用户列表)
    """
    try:
        total_users = mongo.db.users.count_documents({})
        
        # 获取最近活跃的用户（基于最后登录时间）
        # 取前20位最近登录的用户
        active_users_cursor = mongo.db.users.find(
            {}, 
            {"_id": 0, "username": 1, "last_login": 1}
        ).sort("last_login", -1).limit(20)
        
        active_users = []
        for user in active_users_cursor:
            user_data = {
                "username": user["username"],
                "last_login": user.get("last_login")
            }
            active_users.append(user_data)
        
        # 简单统计：获取最近10条使用记录
        recent_logs = list(mongo.db.usage_logs.find({}, {"_id": 0, "username": 1, "action": 1, "created_at": 1}).sort("created_at", -1).limit(10))
        
        return jsonify({
            "code": 200, 
            "message": "success", 
            "data": {
                "total_users": total_users,
                "active_users": active_users,
                "recent_activities": recent_logs
            }
        })
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500
