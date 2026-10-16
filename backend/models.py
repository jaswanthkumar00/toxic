from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    submissions: Mapped[list["Submission"]] = relationship(back_populates="user")


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(30))
    icon: Mapped[str] = mapped_column(String(40), default="code")
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="track", cascade="all, delete-orphan"
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    problem_statement: Mapped[str] = mapped_column(Text)
    starter_code: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(30), default="python")
    difficulty: Mapped[str] = mapped_column(String(30))
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=20)
    skill: Mapped[str] = mapped_column(String(60))
    tasks: Mapped[list] = mapped_column(JSON, default=list)
    test_cases: Mapped[list] = mapped_column(JSON, default=list)
    evaluation_rule: Mapped[str] = mapped_column(String(80))
    track: Mapped[Track] = relationship(back_populates="exercises")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="exercise")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30))
    score: Mapped[int] = mapped_column(Integer, default=0)
    output: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped[User] = relationship(back_populates="submissions")
    exercise: Mapped[Exercise] = relationship(back_populates="submissions")
