"use strict";
const QUESTION_TYPE_MAP = {
  single: "单选",
  multi: "多选",
  judge: "判断",
  fill: "填空"
};
const DIFFICULTY_MAP = {
  easy: "简单",
  medium: "中等",
  hard: "困难"
};
const PAPER_STRATEGIES = [
  {
    key: "random",
    icon: "随机",
    title: "随机组卷",
    desc: "从题库随机抽取，全面检测",
    shortDesc: "从题库随机抽取题目"
  },
  {
    key: "knowledge",
    icon: "专项",
    title: "专项训练",
    desc: "按科目或知识点做针对性训练",
    shortDesc: "按分类做针对性训练"
  },
  {
    key: "progressive",
    icon: "递进",
    title: "难度递进",
    desc: "从易到难，逐步提升",
    shortDesc: "逐步提升题目难度"
  },
  {
    key: "real",
    icon: "真题",
    title: "模拟真题",
    desc: "按历年真题比例组卷",
    shortDesc: "按真题比例组卷"
  }
];
const PAPER_STRATEGY_MAP = PAPER_STRATEGIES.reduce(
  (map, item) => {
    map[item.key] = item;
    return map;
  },
  {}
);
const DIFFICULTY_OPTIONS = [
  { label: "全部", value: "all" },
  { label: "简单", value: "easy" },
  { label: "中等", value: "medium" },
  { label: "困难", value: "hard" }
];
const QUESTION_COUNT_OPTIONS = [10, 20, 30, 50];
const TIME_LIMIT_OPTIONS = [30, 45, 60, 90, 120];
const CSCA_SUBJECT_OPTIONS = [
  "数学",
  "物理",
  "化学",
  "理科中文",
  "文科中文"
];
const HSK_KNOWLEDGE_OPTIONS = [
  "听力理解",
  "阅读理解",
  "口语表达",
  "书写表达",
  "翻译表达",
  "词汇语法"
];
const WRONG_REASONS = [
  "知识点不会",
  "粗心大意",
  "审题错误",
  "时间不够",
  "选项混淆",
  "其他"
];
function getSpecialLabel(examType) {
  return examType === "CSCA" ? "科目" : "知识点";
}
function getQuestionDomain(question) {
  return question.examType === "CSCA" ? question.subject || "" : question.knowledgePoint || "";
}
function getQuestionDomainLabel(examType) {
  return examType === "CSCA" ? "科目" : "知识点";
}
exports.CSCA_SUBJECT_OPTIONS = CSCA_SUBJECT_OPTIONS;
exports.DIFFICULTY_MAP = DIFFICULTY_MAP;
exports.DIFFICULTY_OPTIONS = DIFFICULTY_OPTIONS;
exports.HSK_KNOWLEDGE_OPTIONS = HSK_KNOWLEDGE_OPTIONS;
exports.PAPER_STRATEGY_MAP = PAPER_STRATEGY_MAP;
exports.QUESTION_COUNT_OPTIONS = QUESTION_COUNT_OPTIONS;
exports.QUESTION_TYPE_MAP = QUESTION_TYPE_MAP;
exports.TIME_LIMIT_OPTIONS = TIME_LIMIT_OPTIONS;
exports.WRONG_REASONS = WRONG_REASONS;
exports.getQuestionDomain = getQuestionDomain;
exports.getQuestionDomainLabel = getQuestionDomainLabel;
exports.getSpecialLabel = getSpecialLabel;
