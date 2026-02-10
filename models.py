import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return uuid.uuid4().hex


def _join_code() -> str:
    return uuid.uuid4().hex[:6].upper()


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    join_code: Mapped[str] = mapped_column(String(6), unique=True, default=_join_code)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    members: Mapped[list["Member"]] = relationship(back_populates="household")
    items: Mapped[list["Item"]] = relationship(back_populates="household")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    name: Mapped[str] = mapped_column(String(200))
    token: Mapped[str] = mapped_column(String(32), unique=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    household: Mapped["Household"] = relationship(back_populates="members")
    items: Mapped[list["Item"]] = relationship(back_populates="added_by_member")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    added_by: Mapped[int] = mapped_column(ForeignKey("members.id"))
    name: Mapped[str] = mapped_column(String(300))
    location: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(100), default="Other")
    raw_input: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    household: Mapped["Household"] = relationship(back_populates="items")
    added_by_member: Mapped["Member"] = relationship(back_populates="items")
