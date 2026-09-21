"""Question bank SQLAlchemy models."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func

from src.config.database import Base


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        Index("idx_questions_exam_type", "exam_type"),
        Index("idx_questions_subject", "subject"),
        Index("idx_questions_knowledge", "knowledge_point"),
        Index("idx_questions_difficulty", "difficulty"),
        Index("idx_questions_type", "question_type"),
        Index("idx_questions_wrong_rate", "wrong_rate"),
        {"comment": "Question bank"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Question ID")
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="Exam type")
    subject = Column(String(32), nullable=False, comment="Subject")
    knowledge_point = Column(String(64), nullable=False, comment="Knowledge point tag")
    difficulty = Column(SAEnum("easy", "medium", "hard"), nullable=False, comment="Difficulty")
    question_type = Column(
        SAEnum("single", "multi", "judge", "fill"), nullable=False, comment="Question type"
    )
    stem_text = Column(Text, nullable=False, comment="Question stem text")
    stem_image = Column(String(512), nullable=True, comment="Question stem image URL")
    stem_audio = Column(String(512), nullable=True, comment="Question stem audio URL")
    options = Column(JSON, nullable=False, comment="Options in [{key, text}] format")
    answer = Column(String(256), nullable=False, comment="Correct answer")
    analysis = Column(Text, nullable=True, comment="Answer explanation")
    wrong_options_analysis = Column(JSON, nullable=True, comment="Distractor analysis")
    usage_count = Column(Integer, default=0, comment="Times included in papers")
    correct_count = Column(Integer, default=0, comment="Correct answer count")
    wrong_count = Column(Integer, default=0, comment="Incorrect answer count")
    wrong_rate = Column(Float, default=0, comment="Historical incorrect rate")
    is_active = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=1,
        comment="Whether the question is active",
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Question(id={self.id}, type={self.question_type}, point={self.knowledge_point})>"


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (
        Index("idx_papers_user", "user_id"),
        Index("idx_papers_exam_type", "exam_type"),
        Index("idx_papers_strategy", "strategy"),
        {"comment": "Generated exam papers"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Paper ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_papers_user", ondelete="CASCADE"),
        nullable=False,
        comment="Creator user ID",
    )
    title = Column(String(128), nullable=False, comment="Paper title")
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="Exam type")
    strategy = Column(
        SAEnum("random", "knowledge", "progressive", "real"),
        nullable=False,
        comment="Paper generation strategy",
    )
    question_ids = Column(JSON, nullable=False, comment="Ordered list of question IDs")
    total_score = Column(Integer, default=0, comment="Total score")
    time_limit = Column(Integer, default=0, comment="Time limit in minutes; zero means unlimited")
    mode = Column(
        SAEnum("exam", "practice"), default="practice", comment="Answer mode"
    )
    difficulty = Column(
        SAEnum("all", "easy", "medium", "hard"), default="all", comment="Difficulty filter"
    )
    is_public = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=0,
        comment="Whether the paper is publicly shared",
    )
    finished_at = Column(DateTime, nullable=True, comment="Completion time")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Paper(id={self.id}, title={self.title}, strategy={self.strategy})>"
