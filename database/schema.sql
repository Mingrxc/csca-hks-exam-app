-- Generated from SQLAlchemy models. Initialize using Alembic upgrade head.

-- This reference contains no credentials or business data.

CREATE DATABASE IF NOT EXISTS csca_hks_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE csca_hks_exam;

CREATE TABLE content_items (
	id INTEGER NOT NULL COMMENT 'Content ID' AUTO_INCREMENT,
	category ENUM('consulting','club','ad','notice') NOT NULL COMMENT 'Content category',
	title VARCHAR(128) NOT NULL COMMENT 'Title',
	summary VARCHAR(255) NOT NULL COMMENT 'Summary',
	body TEXT NOT NULL COMMENT 'Body content',
	cover_image VARCHAR(512) COMMENT 'Cover image URL',
	link_url VARCHAR(512) COMMENT 'Destination URL',
	sort_order INTEGER COMMENT 'Display order',
	is_active TINYINT(1) COMMENT 'Whether the content is active',
	created_at DATETIME COMMENT 'Creation time' DEFAULT now(),
	updated_at DATETIME COMMENT 'Update time' DEFAULT now(),
	PRIMARY KEY (id)
)COMMENT='Home news and promotional content';

CREATE INDEX idx_content_active ON content_items (is_active);

CREATE INDEX idx_content_category ON content_items (category);

CREATE INDEX idx_content_sort ON content_items (sort_order);

CREATE TABLE questions (
	id INTEGER NOT NULL COMMENT 'Question ID' AUTO_INCREMENT,
	bank_id VARCHAR(96) COMMENT 'Stable source question ID',
	exam_version VARCHAR(24),
	level VARCHAR(8),
	knowledge_module VARCHAR(96),
	material_id VARCHAR(96),
	response_mode VARCHAR(32) NOT NULL,
	scoring_mode VARCHAR(40) NOT NULL,
	max_score FLOAT NOT NULL,
	source_data JSON COMMENT 'Lossless private source metadata',
	exam_type ENUM('CSCA','HKS') NOT NULL COMMENT 'Exam type',
	subject VARCHAR(32) NOT NULL COMMENT 'Subject',
	knowledge_point VARCHAR(64) NOT NULL COMMENT 'Knowledge point tag',
	difficulty ENUM('easy','medium','hard') NOT NULL COMMENT 'Difficulty',
	question_type ENUM('single','multi','judge','fill') NOT NULL COMMENT 'Question type',
	stem_text TEXT NOT NULL COMMENT 'Question stem text',
	stem_image VARCHAR(512) COMMENT 'Question stem image URL',
	stem_audio VARCHAR(512) COMMENT 'Question stem audio URL',
	options JSON NOT NULL COMMENT 'Options in [{key, text}] format',
	answer TEXT NOT NULL COMMENT 'Correct or reference answer',
	analysis TEXT COMMENT 'Answer explanation',
	wrong_options_analysis JSON COMMENT 'Distractor analysis',
	usage_count INTEGER COMMENT 'Times included in papers',
	correct_count INTEGER COMMENT 'Correct answer count',
	wrong_count INTEGER COMMENT 'Incorrect answer count',
	wrong_rate FLOAT COMMENT 'Historical incorrect rate',
	is_active TINYINT(1) COMMENT 'Whether the question is active',
	created_at DATETIME DEFAULT now(),
	updated_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	UNIQUE (bank_id)
)COMMENT='Question bank';

CREATE INDEX idx_questions_difficulty ON questions (difficulty);

CREATE INDEX idx_questions_exam_type ON questions (exam_type);

CREATE INDEX idx_questions_knowledge ON questions (knowledge_point);

CREATE INDEX idx_questions_subject ON questions (subject);

CREATE INDEX idx_questions_type ON questions (question_type);

CREATE INDEX idx_questions_version_level ON questions (exam_version, level);

CREATE INDEX idx_questions_wrong_rate ON questions (wrong_rate);

CREATE INDEX ix_questions_material_id ON questions (material_id);

CREATE TABLE users (
	id INTEGER NOT NULL COMMENT 'User ID' AUTO_INCREMENT,
	openid VARCHAR(64) NOT NULL COMMENT 'WeChat OpenID',
	unionid VARCHAR(64) COMMENT 'WeChat UnionID for cross-app identity',
	nickname VARCHAR(64) COMMENT 'Display name',
	avatar_url VARCHAR(512) COMMENT 'Avatar URL',
	target_exam ENUM('CSCA','HKS') COMMENT 'Primary target exam',
	target_date DATE COMMENT 'Primary target exam date',
	total_questions INTEGER COMMENT 'Total questions answered',
	total_objective INTEGER COMMENT 'Automatically graded questions answered',
	total_correct INTEGER COMMENT 'Total correct answers',
	streak_days INTEGER COMMENT 'Current study streak in days',
	last_streak_at DATE COMMENT 'Most recent streak date',
	created_at DATETIME COMMENT 'Registration time' DEFAULT now(),
	updated_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	UNIQUE (openid)
)COMMENT='Application users';

CREATE INDEX idx_users_created ON users (created_at);

CREATE INDEX idx_users_openid ON users (openid);

CREATE TABLE favorites (
	id INTEGER NOT NULL COMMENT 'Favorite ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'User ID',
	question_id INTEGER NOT NULL COMMENT 'Question ID',
	note VARCHAR(256) COMMENT 'Favorite note',
	created_at DATETIME COMMENT 'Creation time' DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT uk_user_favorite_question UNIQUE (user_id, question_id),
	CONSTRAINT fk_favorites_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	CONSTRAINT fk_favorites_question FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE RESTRICT
)COMMENT='User favorite questions';

CREATE INDEX idx_favorites_created ON favorites (created_at);

CREATE INDEX idx_favorites_question ON favorites (question_id);

CREATE INDEX idx_favorites_user ON favorites (user_id);

CREATE TABLE knowledge_stats (
	id INTEGER NOT NULL COMMENT 'Statistics ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'User ID',
	exam_type ENUM('CSCA','HKS') NOT NULL COMMENT 'Exam type',
	knowledge_point VARCHAR(64) NOT NULL COMMENT 'Knowledge point',
	total_answered INTEGER COMMENT 'Total answers',
	total_correct INTEGER COMMENT 'Total correct answers',
	correct_rate FLOAT COMMENT 'Correct answer rate',
	updated_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT uk_user_exam_point UNIQUE (user_id, exam_type, knowledge_point),
	CONSTRAINT fk_knowledge_stats_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)COMMENT='Knowledge-point performance statistics';

CREATE INDEX idx_knowledge_user_exam ON knowledge_stats (user_id, exam_type);

CREATE TABLE papers (
	id INTEGER NOT NULL COMMENT 'Paper ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'Creator user ID',
	title VARCHAR(128) NOT NULL COMMENT 'Paper title',
	exam_type ENUM('CSCA','HKS') NOT NULL COMMENT 'Exam type',
	strategy ENUM('random','knowledge','progressive','real') NOT NULL COMMENT 'Paper generation strategy',
	question_ids JSON NOT NULL COMMENT 'Ordered list of question IDs',
	total_score INTEGER COMMENT 'Total score',
	time_limit INTEGER COMMENT 'Time limit in minutes; zero means unlimited',
	mode ENUM('exam','practice') COMMENT 'Answer mode',
	difficulty ENUM('all','easy','medium','hard') COMMENT 'Difficulty filter',
	selection JSON COMMENT 'Version, level and category selection',
	is_public TINYINT(1) COMMENT 'Whether the paper is publicly shared',
	finished_at DATETIME COMMENT 'Completion time',
	created_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT fk_papers_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)COMMENT='Generated exam papers';

CREATE INDEX idx_papers_exam_type ON papers (exam_type);

CREATE INDEX idx_papers_strategy ON papers (strategy);

CREATE INDEX idx_papers_user ON papers (user_id);

CREATE TABLE streak_records (
	id INTEGER NOT NULL COMMENT 'Record ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'User ID',
	streak_date DATE NOT NULL COMMENT 'Study date',
	question_count INTEGER COMMENT 'Questions answered that day',
	created_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT uk_user_date UNIQUE (user_id, streak_date),
	CONSTRAINT fk_streak_records_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)COMMENT='Daily study streak records';

CREATE INDEX idx_streak_date ON streak_records (streak_date);

CREATE INDEX idx_streak_user ON streak_records (user_id);

CREATE TABLE user_exam_targets (
	id INTEGER NOT NULL COMMENT 'Record ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'User ID',
	exam_type ENUM('CSCA','HKS') NOT NULL COMMENT 'Exam type',
	target_date DATE NOT NULL COMMENT 'Target date for this exam',
	created_at DATETIME COMMENT 'Creation time' DEFAULT now(),
	updated_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT uk_user_exam_target UNIQUE (user_id, exam_type),
	CONSTRAINT fk_user_exam_targets_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
)COMMENT='Per-exam target dates for users';

CREATE INDEX idx_user_exam_target_exam ON user_exam_targets (exam_type);

CREATE INDEX idx_user_exam_target_user ON user_exam_targets (user_id);

CREATE TABLE wrong_book (
	id INTEGER NOT NULL COMMENT 'Record ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'User ID',
	question_id INTEGER NOT NULL COMMENT 'Question ID',
	wrong_count INTEGER COMMENT 'Cumulative incorrect-answer count',
	correct_count INTEGER COMMENT 'Consecutive correct-answer count',
	is_mastered TINYINT(1) COMMENT 'Whether mastered after the required correct-answer streak',
	first_wrong_at DATETIME COMMENT 'First incorrect-answer time' DEFAULT now(),
	last_wrong_at DATETIME COMMENT 'Most recent incorrect-answer time' DEFAULT now(),
	last_review_at DATETIME COMMENT 'Most recent review time',
	created_at DATETIME DEFAULT now(),
	updated_at DATETIME DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT uk_user_question UNIQUE (user_id, question_id),
	CONSTRAINT fk_wrong_book_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	CONSTRAINT fk_wrong_book_question FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE RESTRICT
)COMMENT='User wrong-book entries';

CREATE INDEX idx_wrongbook_last_wrong ON wrong_book (last_wrong_at);

CREATE INDEX idx_wrongbook_mastered ON wrong_book (is_mastered);

CREATE INDEX idx_wrongbook_question ON wrong_book (question_id);

CREATE INDEX idx_wrongbook_user ON wrong_book (user_id);

CREATE TABLE answer_records (
	id INTEGER NOT NULL COMMENT 'Record ID' AUTO_INCREMENT,
	user_id INTEGER NOT NULL COMMENT 'User ID',
	paper_id INTEGER NOT NULL COMMENT 'Paper ID',
	question_id INTEGER NOT NULL COMMENT 'Question ID',
	user_answer TEXT COMMENT 'Submitted answer',
	evaluation_status VARCHAR(32) NOT NULL,
	self_score FLOAT COMMENT 'Self-assessed practice score',
	is_correct TINYINT(1) COMMENT 'Whether the submitted answer is correct',
	time_spent INTEGER COMMENT 'Time spent on this question in seconds',
	wrong_reason ENUM('知识点不会','粗心大意','审题错误','时间不够','选项混淆','其他') COMMENT 'Incorrect-answer reason tag',
	created_at DATETIME COMMENT 'Submission time' DEFAULT now(),
	PRIMARY KEY (id),
	CONSTRAINT uk_user_paper_question UNIQUE (user_id, paper_id, question_id),
	CONSTRAINT fk_answer_records_user FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	CONSTRAINT fk_answer_records_paper FOREIGN KEY(paper_id) REFERENCES papers (id) ON DELETE CASCADE,
	CONSTRAINT fk_answer_records_question FOREIGN KEY(question_id) REFERENCES questions (id) ON DELETE RESTRICT
)COMMENT='Answer submission records';

CREATE INDEX idx_correct ON answer_records (is_correct);

CREATE INDEX idx_question ON answer_records (question_id);

CREATE INDEX idx_user_paper ON answer_records (user_id, paper_id);

CREATE INDEX idx_wrong_reason ON answer_records (wrong_reason);
