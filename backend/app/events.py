"""轻量“最近事件”记录。

设计原则（非审计后台）：
- 事件写入使用独立 session/事务，与业务主事务完全隔离；
- 任何失败（库不可用、字段过长等）只记日志并吞掉异常，
  绝不能让业务写路径失败；
- 仅保留最近事件流，由 GET /api/recent-mill-events 读取最近 20 条。
"""

import logging

from flask_jwt_extended import get_jwt_identity

from app.database import SessionLocal
from app.models.recent_mill_event import RecentMillEvent
from app.models.user import User

logger = logging.getLogger(__name__)


def record_event(action: str, summary: str, mill_id: int | None = None) -> None:
    """最佳努力写入一条最近事件。永不抛异常。"""
    try:
        actor_id = None
        identity = get_jwt_identity()
        if identity is not None:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.username == identity).first()
                if user:
                    actor_id = user.id
            finally:
                db.close()

        db = SessionLocal()
        try:
            db.add(
                RecentMillEvent(
                    actor_id=actor_id,
                    action=action,
                    mill_id=mill_id,
                    summary=summary[:255],
                )
            )
            db.commit()
        except Exception:
            db.rollback()
            logger.warning("写入最近事件失败，已忽略: action=%s", action, exc_info=True)
        finally:
            db.close()
    except Exception:
        logger.warning("记录最近事件异常，已忽略: action=%s", action, exc_info=True)
