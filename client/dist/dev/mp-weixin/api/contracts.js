"use strict";
const constants_exam = require("../constants/exam.js");
function toQuestion(item) {
  return {
    id: item.id,
    examType: item.exam_type,
    subject: item.subject,
    type: item.question_type,
    difficulty: item.difficulty,
    knowledgePoint: item.knowledge_point,
    stem: item.stem_text,
    options: item.options,
    answer: item.answer,
    analysis: item.analysis,
    isFavorite: item.is_favorite
  };
}
function toHistoryPaper(item) {
  var _a;
  return {
    id: item.id,
    title: item.title,
    correctRate: item.correct_rate,
    timeUsed: formatSeconds(item.time_used),
    date: ((_a = item.finished_at) == null ? void 0 : _a.slice(0, 10)) || "",
    passed: item.passed
  };
}
function toDashboardData(item) {
  return {
    userName: item.user_name,
    targetExam: item.target_exam,
    targetDate: item.target_date || "",
    countdown: calculateCountdown(item.target_date),
    todayStats: {
      questionCount: item.today_stats.question_count,
      correctRate: item.today_stats.correct_rate,
      wrongCount: item.today_stats.wrong_count
    },
    pendingWrongCount: item.pending_wrong_count,
    favoriteCount: item.favorite_count,
    recentPapers: item.recent_papers.map((paper) => {
      var _a;
      return {
        id: paper.id,
        title: paper.title,
        questionCount: paper.question_count,
        score: paper.score,
        date: ((_a = paper.finished_at) == null ? void 0 : _a.slice(0, 10)) || ""
      };
    })
  };
}
function toUserProfile(item) {
  return {
    nickname: item.nickname,
    avatarUrl: item.avatar_url || "",
    targetExam: item.target_exam,
    targetDate: item.target_date || "",
    totalQuestions: item.total_questions,
    correctRate: item.correct_rate,
    streakDays: item.streak_days,
    favoriteCount: item.favorite_count
  };
}
function calculateCountdown(targetDate) {
  if (!targetDate)
    return { days: "0", hours: "00", minutes: "00" };
  const [year, month, day] = targetDate.split("-").map(Number);
  const target = new Date(year, month - 1, day, 23, 59, 59).getTime();
  const remaining = Math.max(target - Date.now(), 0);
  const days = Math.floor(remaining / 864e5);
  const hours = Math.floor(remaining % 864e5 / 36e5);
  const minutes = Math.floor(remaining % 36e5 / 6e4);
  return {
    days: String(days),
    hours: String(hours).padStart(2, "0"),
    minutes: String(minutes).padStart(2, "0")
  };
}
function toExamResultSummary(item) {
  return {
    score: item.score,
    correctCount: item.correct_count,
    totalCount: item.total_count,
    correctRate: item.correct_rate,
    timeUsed: formatSeconds(item.time_used)
  };
}
function toResultWrongQuestions(item) {
  return item.wrong_questions.map((question) => ({
    id: question.id,
    stem: question.stem,
    typeLabel: question.type_label,
    yourAnswer: question.your_answer,
    correctAnswer: question.correct_answer
  }));
}
function toResultReviewQuestions(item) {
  return item.review_questions.map((question) => ({
    id: question.id,
    stem: question.stem,
    typeLabel: constants_exam.QUESTION_TYPE_MAP[question.type_label] || question.type_label,
    options: question.options,
    userAnswer: question.user_answer,
    correctAnswer: question.correct_answer,
    analysis: question.analysis,
    correct: question.is_correct
  }));
}
function toWrongBookListItem(item) {
  var _a;
  return {
    id: item.id,
    examType: item.exam_type,
    subject: item.subject,
    typeLabel: constants_exam.QUESTION_TYPE_MAP[item.type] || item.type,
    diffLabel: constants_exam.DIFFICULTY_MAP[item.difficulty] || item.difficulty,
    difficulty: item.difficulty,
    knowledgePoint: item.knowledge_point,
    wrongCount: item.wrong_count,
    mastered: item.is_mastered,
    stem: item.stem,
    lastWrongAt: ((_a = item.last_wrong_at) == null ? void 0 : _a.slice(0, 10)) || ""
  };
}
function toWrongBookDetail(item) {
  const question = toQuestion(item.question);
  const confusionEntries = Object.entries(item.wrong_options_analysis);
  return {
    ...toWrongBookListItem(item),
    options: question.options,
    answer: question.answer || "",
    myAnswer: item.last_user_answer,
    analysis: question.analysis || "暂无解析",
    confusion: confusionEntries.map(([option, text]) => `${option}：${text}`).join("\n")
  };
}
function toRelatedQuestion(item) {
  return {
    id: item.id,
    stem: item.stem_text,
    typeLabel: constants_exam.QUESTION_TYPE_MAP[item.question_type] || item.question_type,
    diffLabel: constants_exam.DIFFICULTY_MAP[item.difficulty] || item.difficulty,
    difficulty: item.difficulty
  };
}
function formatSeconds(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remaining).padStart(2, "0")}`;
}
exports.toDashboardData = toDashboardData;
exports.toExamResultSummary = toExamResultSummary;
exports.toHistoryPaper = toHistoryPaper;
exports.toQuestion = toQuestion;
exports.toRelatedQuestion = toRelatedQuestion;
exports.toResultReviewQuestions = toResultReviewQuestions;
exports.toResultWrongQuestions = toResultWrongQuestions;
exports.toUserProfile = toUserProfile;
exports.toWrongBookDetail = toWrongBookDetail;
exports.toWrongBookListItem = toWrongBookListItem;
