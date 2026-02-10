from typing import Optional
from app.database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, ForeignKey

import datetime

class Exercise(Base):
    __tablename__ = "exercise"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    body_parts: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    author: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))
