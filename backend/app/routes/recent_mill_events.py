from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.database import SessionLocal
from app.models.recent_mill_event import RecentMillEvent
from app.models.user import User
from app.serializers import recent_mill_event_json
from app.utils import error

bp = Blueprint("recent_mill_events", __name__, url_prefix="/api/recent-mill-events")

RECENT_LIMIT = 20


@bp.get("")
@jwt_required()
def list_recent_events():
    db = SessionLocal()
    try:
        username = get_jwt_identity()
        actor = db.query(User).filter(User.username == username).first()
        if not actor:
            return error("未登录或登录已过期", 401)

        query = db.query(RecentMillEvent)
        if actor.role != "admin":
            # 非管理员仅能看到自己触发的事件
            query = query.filter(RecentMillEvent.actor_id == actor.id)

        rows = (
            query.order_by(RecentMillEvent.id.desc()).limit(RECENT_LIMIT).all()
        )
        return jsonify([recent_mill_event_json(r) for r in rows])
    finally:
        db.close()
