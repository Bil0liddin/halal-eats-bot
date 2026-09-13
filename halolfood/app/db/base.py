"""Barcha ORM modellari uchun umumiy asos."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Barcha jadvallar shu klassdan meros oladi."""

    pass


class TimestampMixin:
    """created_at va updated_at ustunlarini avtomatik qo'shadi."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
