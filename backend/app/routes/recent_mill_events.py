from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.database import SessionLocal
from app.models.recent_mill_event import RecentMillEvent
from app.models.user import User
from app.serializers import recent_mill_event_json
from app.utils import error

bp = Blueprint("recent_mill_events", __name__, url_prefix="/api/recent-mill-events")


@bp.get("")
@jwt_required()
def list_recent_events():
    db = SessionLocal()
    try:
        username = get_jwt_identity()
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return error("未登录或登录已过期", 401)

        q = db.query(RecentMillEvent, User.display_name).outerjoin(
            User, RecentMillEvent.actor_id == User.id
        )
        # admin 看全站；其他角色（grinder）只看自己产生的事件
        if user.role != "admin":
            q = q.filter(RecentMillEvent.actor_id == user.id)

        rows = q.order_by(RecentMillEvent.created_at.desc(), RecentMillEvent.id.desc()).limit(20).all()
        return jsonify([recent_mill_event_json(event, actor_name) for event, actor_name in rows])
    finally:
        db.close()
