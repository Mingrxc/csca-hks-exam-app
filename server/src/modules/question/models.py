"""题库模块 SQLAlchemy 模型"""

from sqlalchemy import Column, DateTime, Float, Index, Integer, JSON, String, Text
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
        {"comment": "题目表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="题目 ID")
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="考试类型")
    subject = Column(String(32), nullable=False, comment="科目")
    knowledge_point = Column(String(64), nullable=False, comment="知识点标签")
    difficulty = Column(SAEnum("easy", "medium", "hard"), nullable=False, comment="难度")
    question_type = Column(
        SAEnum("single", "multi", "judge", "fill"), nullable=False, comment="题型"
    )
    stem_text = Column(Text, nullable=False, comment="题干文本")
    stem_image = Column(String(512), nullable=True, comment="题干图片 URL")
    stem_audio = Column(String(512), nullable=True, comment="题干音频 URL")
    options = Column(JSON, nullable=False, comment="选项（[{key,text}] 结构）")
    answer = Column(String(256), nullable=False, comment="正确答案")
    analysis = Column(Text, nullable=True, comment="题目解析")
    wrong_options_analysis = Column(JSON, nullable=True, comment="易混选项辨析")
    usage_count = Column(Integer, default=0, comment="被组卷次数")
    correct_count = Column(Integer, default=0, comment="正确作答次数")
    wrong_count = Column(Integer, default=0, comment="错误作答次数")
    wrong_rate = Column(Float, default=0, comment="历史错误率")
    is_active = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=1,
        comment="是否启用",
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
        {"comment": "试卷表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="试卷 ID")
    user_id = Column(Integer, nullable=False, comment="创建者")
    title = Column(String(128), nullable=False, comment="试卷标题")
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="考试类型")
    strategy = Column(
        SAEnum("random", "knowledge", "progressive", "real"),
        nullable=False,
        comment="组卷策略",
    )
    question_ids = Column(JSON, nullable=False, comment="题目 ID 列表及顺序")
    total_score = Column(Integer, default=0, comment="总分")
    time_limit = Column(Integer, default=0, comment="限时（分钟），0=不限时")
    mode = Column(
        SAEnum("exam", "practice"), default="practice", comment="答题模式"
    )
    difficulty = Column(
        SAEnum("all", "easy", "medium", "hard"), default="all", comment="难度筛选"
    )
    is_public = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=0,
        comment="是否公开分享",
    )
    finished_at = Column(DateTime, nullable=True, comment="完成时间")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Paper(id={self.id}, title={self.title}, strategy={self.strategy})>"
