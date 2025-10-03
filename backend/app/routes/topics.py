from flask import Blueprint, request, jsonify
import json
from app.utils.database import db
from app.utils.auth import token_required

bp = Blueprint('topics', __name__)


@bp.route('/', methods=['GET', 'OPTIONS'])
def get_topics():
    """獲取話題列表"""
    # 處理 OPTIONS 請求（CORS preflight）
    if request.method == 'OPTIONS':
        return '', 204
    
    status = request.args.get('status', 'approved')

    query = """
        SELECT t.*, u.nickname as creator_nickname
        FROM DebateTopics t
        JOIN Users u ON t.created_by = u.user_id
        WHERE t.status = ?
        ORDER BY t.created_at DESC
    """

    topics = db.execute_query(query, (status,), fetch_all=True)
    return jsonify({'topics': topics})


@bp.route('/<int:topic_id>', methods=['GET', 'OPTIONS'])
def get_topic(topic_id):
    """獲取話題詳情"""
    if request.method == 'OPTIONS':
        return '', 204
    topic = db.execute_query(
        """
        SELECT t.*, u.nickname as creator_nickname
        FROM DebateTopics t
        JOIN Users u ON t.created_by = u.user_id
        WHERE t.topic_id = ?
        """,
        (topic_id,),
        fetch_one=True
    )

    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    # 解析 JSON 規則
    if topic.get('rules'):
        try:
            topic['rules'] = json.loads(topic['rules'])
        except:
            topic['rules'] = {}

    return jsonify(topic)


@bp.route('/apply', methods=['POST'])
@token_required
def apply_topic():
    """申請新話題"""
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    side_pros = data.get('side_pros')
    side_cons = data.get('side_cons')
    rules = data.get('rules', {})

    if not all([title, description, side_pros, side_cons]):
        return jsonify({'error': 'Missing required fields'}), 400

    # 將規則轉換為 JSON 字符串
    rules_json = json.dumps(rules, ensure_ascii=False)

    topic_id = db.execute_insert(
        """
        INSERT INTO DebateTopics (title, description, side_pros, side_cons, rules, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, description, side_pros, side_cons, rules_json, request.current_user['user_id'])
    )

    return jsonify({
        'message': 'Topic application submitted',
        'topic_id': topic_id
    }), 201
