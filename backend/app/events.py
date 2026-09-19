import logging

from flask_jwt_extended import get_jwt_identity

from app.database import SessionLocal
from app.models.recent_mill_event import RecentMillEvent
from app.models.user import User

logger = logging.getLogger(__name__)


def record_event(action: str, summary: str, mill_id: int | None = None) -> None:
    """最佳努力写入一条最近事件。

    使用独立 session 提交，任何失败仅记日志、不外抛：
    事件写入失败绝不影响主业务事务。调用方应在主事务 commit 成功后再调用。
    """
    db = SessionLocal()
    try:
        actor_id: int | None = None
        username = get_jwt_identity()
        if username:
            user = db.query(User).filter(User.username == username).first()
            if user:
                actor_id = user.id
        db.add(
            RecentMillEvent(
                actor_id=actor_id,
                action=action,
                mill_id=mill_id,
                summary=summary,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.warning("写入最近事件失败 action=%s", action, exc_info=True)
    finally:
        db.close()
