from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# 轻量最近事件动作码，前缀对应前端可跳转的页面：
# mill.* → 研磨机，sample.* → 粘度取样，pass.* → 研磨遍次
EVENT_ACTIONS = (
    "mill.create",
    "mill.update",
    "mill.delete",
    "sample.create",
    "sample.update",
    "sample.delete",
    "pass.create",
    "pass.update",
    "pass.delete",
)


class RecentMillEvent(Base):
    __tablename__ = "recent_mill_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    mill_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("mills.id", ondelete="SET NULL"), nullable=True
    )
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    actor: Mapped["User | None"] = relationship("User")
