from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# 轻量事件动作，仅用于“最近事件”抽屉，不做审计后台
RECENT_EVENT_ACTIONS = (
    "mill.created",
    "mill.updated",
    "mill.deleted",
    "sample.created",
    "sample.updated",
    "sample.deleted",
    "pass.created",
    "pass.updated",
    "pass.deleted",
)


class RecentMillEvent(Base):
    __tablename__ = "recent_mill_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    mill_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp(), index=True
    )
