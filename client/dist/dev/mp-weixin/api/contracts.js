"use strict";
const constants_exam = require("../constants/exam.js");
function toQuestion(item) {
  return {
    id: item.id,
    type: item.question_type,
    difficulty: item.difficulty,
    knowledgePoint: item.knowledge_point,
    stem: item.stem_text,
    options: item.options,
    answer: item.answer,
    analysis: item.analysis
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
function toWrongBookListItem(item) {
  var _a;
  return {
    id: item.id,
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
exports.toExamResultSummary = toExamResultSummary;
exports.toQuestion = toQuestion;
exports.toRelatedQuestion = toRelatedQuestion;
exports.toResultWrongQuestions = toResultWrongQuestions;
exports.toWrongBookDetail = toWrongBookDetail;
exports.toWrongBookListItem = toWrongBookListItem;
