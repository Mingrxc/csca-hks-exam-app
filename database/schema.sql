-- =====================================================
-- 留学考霸 — CSCA & HKS 备考刷题小程序
-- 数据库建表脚本 (MySQL 8.0+)
-- =====================================================

CREATE DATABASE IF NOT EXISTS csca_hks_exam
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE csca_hks_exam;

-- ==================== 用户表 ====================
CREATE TABLE users (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '用户 ID',
    openid          VARCHAR(64)     NOT NULL UNIQUE             COMMENT '微信 OpenID',
    unionid         VARCHAR(64)     DEFAULT NULL                COMMENT '微信 UnionID（多端互通）',
    nickname        VARCHAR(64)     DEFAULT '考霸同学'           COMMENT '昵称',
    avatar_url      VARCHAR(512)    DEFAULT NULL                COMMENT '头像 URL',
    target_exam     ENUM('CSCA','HKS') DEFAULT 'CSCA'           COMMENT '目标考试类型',
    target_date     DATE            DEFAULT NULL                COMMENT '考试日期',
    total_questions INT             DEFAULT 0                   COMMENT '累计刷题数',
    total_correct   INT             DEFAULT 0                   COMMENT '累计正确数',
    streak_days     INT             DEFAULT 0                   COMMENT '连续打卡天数',
    last_streak_at  DATE            DEFAULT NULL                COMMENT '最近打卡日期',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP   COMMENT '注册时间',
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_openid (openid),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


-- ==================== 题目表 ====================
CREATE TABLE questions (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '题目 ID',
    exam_type       ENUM('CSCA','HKS') NOT NULL                 COMMENT '考试类型',
    subject         VARCHAR(32)     NOT NULL                    COMMENT '科目',
    knowledge_point VARCHAR(64)     NOT NULL                    COMMENT '知识点标签',
    difficulty      ENUM('easy','medium','hard') NOT NULL       COMMENT '难度',
    question_type   ENUM('single','multi','judge','fill') NOT NULL COMMENT '题型',
    stem_text       TEXT            NOT NULL                    COMMENT '题干文本',
    stem_image      VARCHAR(512)    DEFAULT NULL                COMMENT '题干图片 URL',
    stem_audio      VARCHAR(512)    DEFAULT NULL                COMMENT '题干音频 URL',
    options         JSON            NOT NULL                    COMMENT '选项（[{key,text}] 结构）',
    answer          VARCHAR(256)    NOT NULL                    COMMENT '正确答案',
    analysis        TEXT            DEFAULT NULL                COMMENT '题目解析',
    wrong_options_analysis JSON     DEFAULT NULL                COMMENT '易混选项辨析',
    usage_count     INT             DEFAULT 0                   COMMENT '被组卷次数',
    correct_count   INT             DEFAULT 0                   COMMENT '正确作答次数',
    wrong_count     INT             DEFAULT 0                   COMMENT '错误作答次数',
    wrong_rate      FLOAT           DEFAULT 0                   COMMENT '历史错误率',
    is_active       TINYINT(1)      DEFAULT 1                   COMMENT '是否启用',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_exam_type (exam_type),
    INDEX idx_subject (subject),
    INDEX idx_knowledge (knowledge_point),
    INDEX idx_difficulty (difficulty),
    INDEX idx_type (question_type),
    INDEX idx_wrong_rate (wrong_rate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目表';


-- ==================== 试卷表 ====================
CREATE TABLE papers (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '试卷 ID',
    user_id         INT             NOT NULL                    COMMENT '创建者',
    title           VARCHAR(128)    NOT NULL                    COMMENT '试卷标题',
    exam_type       ENUM('CSCA','HKS') NOT NULL                 COMMENT '考试类型',
    strategy        ENUM('random','knowledge','progressive','real') NOT NULL COMMENT '组卷策略',
    question_ids    JSON            NOT NULL                    COMMENT '题目 ID 列表及顺序',
    total_score     INT             DEFAULT 0                   COMMENT '总分',
    time_limit      INT             DEFAULT 0                   COMMENT '限时（分钟），0=不限时',
    mode            ENUM('exam','practice') DEFAULT 'practice'  COMMENT '答题模式',
    difficulty      ENUM('all','easy','medium','hard') DEFAULT 'all' COMMENT '难度筛选',
    is_public       TINYINT(1)      DEFAULT 0                   COMMENT '是否公开分享',
    finished_at     DATETIME        DEFAULT NULL                COMMENT '完成时间',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user (user_id),
    INDEX idx_exam_type (exam_type),
    INDEX idx_strategy (strategy)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='试卷表';


-- ==================== 答题记录表 ====================
CREATE TABLE answer_records (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '记录 ID',
    user_id         INT             NOT NULL                    COMMENT '用户 ID',
    paper_id        INT             NOT NULL                    COMMENT '试卷 ID',
    question_id     INT             NOT NULL                    COMMENT '题目 ID',
    user_answer     VARCHAR(256)    DEFAULT NULL                COMMENT '用户答案',
    is_correct      TINYINT(1)      DEFAULT NULL                COMMENT '是否正确',
    time_spent      INT             DEFAULT 0                   COMMENT '该题用时（秒）',
    wrong_reason    ENUM('知识点不会','粗心大意','审题错误','时间不够','选项混淆','其他') DEFAULT NULL COMMENT '错因标签',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP   COMMENT '答题时间',

    INDEX idx_user_paper (user_id, paper_id),
    INDEX idx_question (question_id),
    INDEX idx_correct (is_correct),
    INDEX idx_wrong_reason (wrong_reason)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答题记录表';


-- ==================== 错题本表 ====================
CREATE TABLE wrong_book (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '记录 ID',
    user_id         INT             NOT NULL                    COMMENT '用户 ID',
    question_id     INT             NOT NULL                    COMMENT '题目 ID',
    wrong_count     INT             DEFAULT 1                   COMMENT '累计错误次数',
    correct_count   INT             DEFAULT 0                   COMMENT '连续正确次数',
    is_mastered     TINYINT(1)      DEFAULT 0                   COMMENT '是否已掌握（连续正确 N 次自动标）',
    first_wrong_at  DATETIME        DEFAULT CURRENT_TIMESTAMP   COMMENT '首次错误时间',
    last_wrong_at   DATETIME        DEFAULT CURRENT_TIMESTAMP   COMMENT '最近错误时间',
    last_review_at  DATETIME        DEFAULT NULL                COMMENT '最近复习时间',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_question (user_id, question_id),
    INDEX idx_user (user_id),
    INDEX idx_mastered (is_mastered),
    INDEX idx_last_wrong (last_wrong_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='错题本表';


-- ==================== 知识点统计表 ====================
CREATE TABLE knowledge_stats (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '统计 ID',
    user_id         INT             NOT NULL                    COMMENT '用户 ID',
    exam_type       ENUM('CSCA','HKS') NOT NULL                 COMMENT '考试类型',
    knowledge_point VARCHAR(64)     NOT NULL                    COMMENT '知识点',
    total_answered  INT             DEFAULT 0                   COMMENT '总答题数',
    total_correct   INT             DEFAULT 0                   COMMENT '总正确数',
    correct_rate    FLOAT           DEFAULT 0                   COMMENT '正确率',
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_exam_knowledge (user_id, exam_type, knowledge_point),
    INDEX idx_user_exam (user_id, exam_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点统计表';


-- ==================== 打卡记录表 ====================
CREATE TABLE streak_records (
    id              INT             PRIMARY KEY AUTO_INCREMENT  COMMENT '记录 ID',
    user_id         INT             NOT NULL                    COMMENT '用户 ID',
    streak_date     DATE            NOT NULL                    COMMENT '打卡日期',
    question_count  INT             DEFAULT 0                   COMMENT '当日刷题数',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_date (user_id, streak_date),
    INDEX idx_user (user_id),
    INDEX idx_date (streak_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='打卡记录表';
