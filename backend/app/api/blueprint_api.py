# 文件名：blueprint_api.py
"""
功能说明：蓝图分析API接口
核心功能：
1. 接收文件上传
2. 接收用户自定义提示词
3. 接收用户选择的方法论
4. 调用Service进行分析
5. 返回SSE流式响应
依赖模块：flask, analysis_service
"""
from flask import Blueprint, request, Response, stream_with_context, jsonify, send_file
from app.services.analysis_service import AnalysisService
from app.extensions import mongo
from app.utils.docx_generator import generate_blueprint_docx
from datetime import datetime
import logging
import urllib.parse

# 创建蓝图对象
blueprint_bp = Blueprint('blueprint', __name__)
logger = logging.getLogger(__name__)
STREAM_DONE_MARKER = "\n\n[[__STREAM_DONE__]]\n\n"

# 初始化 Service
# 注意：在实际生产中，建议使用依赖注入或在请求上下文中获取
analysis_service = AnalysisService()

@blueprint_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    POST /api/v1/blueprint/analyze
    接收文件、提示词、方法论，并进行流式分析
    """
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "No file part", "data": None}), 400
        
    file = request.files['file']
    custom_prompt = request.form.get('custom_prompt', '') # 获取用户自定义提示词
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    role = request.form.get('role', 'unknown') # 获取用户角色
    
    if user_id:
        pass # Log logic moved to generate()

    # 获取方法论选择 (前端可能传递为 'huawei,alibaba' 或多次传递 'methodologies')
    # 处理 multipart/form-data 中的数组
    methodologies = request.form.getlist('methodologies')
    # 兼容处理：如果是逗号分隔的字符串
    if len(methodologies) == 1 and ',' in methodologies[0]:
        methodologies = methodologies[0].split(',')

    # 获取用户自定义方法论 (这里复用字段，实际含义已扩展为包含书籍)
    custom_methodologies = request.form.getlist('custom_methodologies')

    if len(methodologies) == 0 and len(custom_methodologies) == 0:
        return jsonify({"code": 400, "message": "请至少选择系统内置方法论或添加书籍作为评审依据", "data": None}), 400
    
    if file.filename == '':
        return jsonify({"code": 400, "message": "No selected file", "data": None}), 400

    try:
        file_name = file.filename
        
        # 准备日志数据
        log_data = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "action": "analyze_blueprint",
            "filename": file_name,
            "custom_prompt": custom_prompt,
            "created_at": datetime.utcnow()
        }
        
        # 定义生成器函数
        def generate():
            try:
                yield "🔄 正在解析文档内容，请稍候...\n\n"

                file_content = file.read()

                generator = analysis_service.analyze_blueprint(
                    file_content,
                    file_name,
                    custom_prompt,
                    methodologies,
                    custom_methodologies
                )

                first_chunk = None
                try:
                    first_chunk = next(generator)
                except StopIteration:
                    return
                except Exception as e:
                    logger.error(f"Error starting analysis: {str(e)}")
                    yield f"\n\n**系统错误**: {str(e)}"
                    return

                if first_chunk and first_chunk.strip() != "🔄 正在解析文档内容，请稍候...":
                    yield first_chunk

                if user_id:
                    try:
                        mongo.db.usage_logs.insert_one(log_data)

                        if custom_methodologies:
                            for book in custom_methodologies:
                                if book and book.strip():
                                    mongo.db.book_stats.update_one(
                                        {"book_name": book.strip(), "role": "all"},
                                        {"$inc": {"count": 1}, "$set": {"last_used_at": datetime.utcnow()}},
                                        upsert=True
                                    )
                                    if role and role != 'unknown':
                                        mongo.db.book_stats.update_one(
                                            {"book_name": book.strip(), "role": role},
                                            {"$inc": {"count": 1}, "$set": {"last_used_at": datetime.utcnow()}},
                                            upsert=True
                                        )
                    except Exception as e:
                        logger.error(f"Failed to log usage: {str(e)}")

                for chunk in generator:
                    yield chunk
            except Exception as e:
                logger.error(f"Error during analysis stream: {str(e)}")
                yield f"\n\n**系统错误**: {str(e)}"
            finally:
                yield STREAM_DONE_MARKER

        # 返回流式响应
        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'X-Accel-Buffering': 'no',  # 禁用 Nginx 缓冲
                'Cache-Control': 'no-cache' # 禁用浏览器/代理缓存
            }
        )

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500

@blueprint_bp.route('/analyze_mindmap', methods=['POST'])
def analyze_mindmap():
    """
    POST /api/v1/blueprint/analyze_mindmap
    接收文件，直接进行流式分析并返回思维导图
    """
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "No file part", "data": None}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"code": 400, "message": "No selected file", "data": None}), 400

    try:
        file_content = file.read()
        file_name = file.filename
        
        def generate():
            try:
                generator = analysis_service.analyze_blueprint_to_mindmap(
                    file_content,
                    file_name
                )
                for chunk in generator:
                    yield chunk
            except Exception as e:
                logger.error(f"Error during mindmap analysis stream: {str(e)}")
                yield f"\n\n**系统错误**: {str(e)}"
            finally:
                yield STREAM_DONE_MARKER

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'X-Accel-Buffering': 'no',  # 禁用 Nginx 缓冲
                'Cache-Control': 'no-cache' # 禁用浏览器/代理缓存
            }
        )
    except Exception as e:
        logger.error(f"Error starting mindmap analysis: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500

@blueprint_bp.route('/smart_mindmap', methods=['POST'])
def smart_mindmap():
    """
    POST /api/v1/blueprint/smart_mindmap
    接收文件，直接进行智能思维导图生成（非诊断模式）
    """
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "No file part", "data": None}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"code": 400, "message": "No selected file", "data": None}), 400

    try:
        file_content = file.read()
        file_name = file.filename
        
        def generate():
            try:
                generator = analysis_service.generate_smart_mindmap(
                    file_content,
                    file_name
                )
                for chunk in generator:
                    yield chunk
            except Exception as e:
                logger.error(f"Error during smart mindmap stream: {str(e)}")
                yield f"\n\n**系统错误**: {str(e)}"
            finally:
                yield STREAM_DONE_MARKER

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'X-Accel-Buffering': 'no',  # 禁用 Nginx 缓冲
                'Cache-Control': 'no-cache' # 禁用浏览器/代理缓存
            }
        )
    except Exception as e:
        logger.error(f"Error starting smart mindmap analysis: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500

@blueprint_bp.route('/generate_mindmap', methods=['POST'])
def generate_mindmap():
    """
    POST /api/v1/blueprint/generate_mindmap
    接收分析报告内容，生成Markmap思维导图
    """
    data = request.json
    markdown_content = data.get('content')
    
    if not markdown_content:
        return jsonify({"code": 400, "message": "Content is required", "data": None}), 400
        
    try:
        def generate():
            try:
                for chunk in analysis_service.generate_mindmap(markdown_content):
                    yield chunk
            except Exception as e:
                logger.error(f"Error during mindmap generation stream: {str(e)}")
                yield f"\n\n**系统错误**: {str(e)}"
            finally:
                yield STREAM_DONE_MARKER
                
        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'X-Accel-Buffering': 'no',
                'Cache-Control': 'no-cache'
            }
        )
    except Exception as e:
        logger.error(f"Mindmap API Error: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500

@blueprint_bp.route('/generate_proposal', methods=['POST'])
def generate_proposal():
    """
    POST /api/v1/blueprint/generate_proposal
    接收需求、想法、方法论，生成蓝图方案
    """
    reference_file = None
    if request.is_json:
        data = request.get_json(silent=True) or {}
        client_needs = data.get('client_needs', '')
        user_ideas = data.get('user_ideas', '')
        methodologies = data.get('methodologies', [])
        custom_methodologies = data.get('custom_methodologies', [])
    else:
        client_needs = request.form.get('client_needs', '')
        user_ideas = request.form.get('user_ideas', '')
        methodologies = request.form.getlist('methodologies')
        if len(methodologies) == 1 and ',' in methodologies[0]:
            methodologies = methodologies[0].split(',')

        custom_methodologies = request.form.getlist('custom_methodologies')
        reference_file = request.files.get('reference_file') or request.files.get('file')
        if reference_file and reference_file.filename == '':
            reference_file = None
    
    if not client_needs:
        return jsonify({"code": 400, "message": "Client needs are required", "data": None}), 400

    if len(methodologies) == 0 and len(custom_methodologies) == 0:
        return jsonify({"code": 400, "message": "请至少选择系统内置方法论或添加书籍作为设计依据", "data": None}), 400
        
    try:
        reference_file_content = None
        reference_file_name = None
        if reference_file:
            reference_file_content = reference_file.read()
            reference_file_name = reference_file.filename

        def generate():
            try:
                generator = analysis_service.generate_proposal(
                    client_needs,
                    user_ideas,
                    methodologies,
                    custom_methodologies,
                    reference_file_content,
                    reference_file_name
                )
                for chunk in generator:
                    yield chunk
            except Exception as e:
                logger.error(f"Error during proposal generation stream: {str(e)}")
                yield f"\n\n**系统错误**: {str(e)}"
            finally:
                yield STREAM_DONE_MARKER

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'X-Accel-Buffering': 'no',
                'Cache-Control': 'no-cache'
            }
        )
    except Exception as e:
        logger.error(f"Error starting proposal generation: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500

@blueprint_bp.route('/generate_sub_proposal', methods=['POST'])
def generate_sub_proposal():
    parent_file = request.files.get('parent_file') or request.files.get('file')
    sub_plan_title = request.form.get('sub_plan_title', '')
    sub_plan_details = request.form.get('sub_plan_details', '')

    methodologies = request.form.getlist('methodologies')
    if len(methodologies) == 1 and ',' in methodologies[0]:
        methodologies = methodologies[0].split(',')
    custom_methodologies = request.form.getlist('custom_methodologies')

    if not parent_file or parent_file.filename == '':
        return jsonify({"code": 400, "message": "请上传父方案文档", "data": None}), 400

    if not sub_plan_title:
        return jsonify({"code": 400, "message": "请填写要生成的子专项/子方案名称", "data": None}), 400

    if len(methodologies) == 0 and len(custom_methodologies) == 0:
        return jsonify({"code": 400, "message": "请至少选择系统内置方法论或添加书籍作为设计依据", "data": None}), 400

    try:
        parent_file_content = parent_file.read()
        parent_file_name = parent_file.filename

        def generate():
            try:
                generator = analysis_service.generate_sub_proposal(
                    parent_file_content,
                    parent_file_name,
                    sub_plan_title,
                    sub_plan_details,
                    methodologies,
                    custom_methodologies
                )
                for chunk in generator:
                    yield chunk
            except Exception as e:
                logger.error(f"Error during sub proposal generation stream: {str(e)}")
                yield f"\n\n**系统错误**: {str(e)}"
            finally:
                yield STREAM_DONE_MARKER

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream; charset=utf-8',
            headers={
                'X-Accel-Buffering': 'no',
                'Cache-Control': 'no-cache'
            }
        )
    except Exception as e:
        logger.error(f"Error starting sub proposal generation: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500

@blueprint_bp.route('/export/docx', methods=['POST'])
def export_docx():
    """
    POST /api/v1/blueprint/export/docx
    接收 markdown 文本，返回 docx 文件
    """
    data = request.json
    markdown_text = data.get('content')
    filename = data.get('filename', '蓝图大师评审报告.docx')
    
    if not markdown_text:
        return jsonify({"code": 400, "message": "Content is required", "data": None}), 400
        
    try:
        docx_stream = generate_blueprint_docx(markdown_text)
        
        # 处理文件名中文编码
        encoded_filename = urllib.parse.quote(filename)
        
        return send_file(
            docx_stream,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Export Error: {str(e)}")
        return jsonify({"code": 500, "message": str(e), "data": None}), 500
