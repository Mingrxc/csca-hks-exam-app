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
    icon: "🎲",
    title: "随机组卷",
    desc: "从题库随机抽取，全面检测",
    shortDesc: "从题库随机抽取题目"
  },
  {
    key: "knowledge",
    icon: "📚",
    title: "知识点专项",
    desc: "针对性练习薄弱知识点",
    shortDesc: "针对薄弱环节强化"
  },
  {
    key: "progressive",
    icon: "📈",
    title: "难度递进",
    desc: "从易到难，逐步提升",
    shortDesc: "逐步提升题目难度"
  },
  {
    key: "real",
    icon: "🎯",
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
const KNOWLEDGE_POINTS = [
  "词汇语法",
  "阅读理解",
  "听力理解",
  "文化常识",
  "逻辑推理",
  "写作表达"
];
const WRONG_BOOK_KNOWLEDGE_POINTS = [
  "词汇语法",
  "阅读理解",
  "文化常识",
  "逻辑推理"
];
const WRONG_REASONS = [
  "知识点不会",
  "粗心大意",
  "审题错误",
  "时间不够",
  "选项混淆",
  "其他"
];
exports.DIFFICULTY_MAP = DIFFICULTY_MAP;
exports.DIFFICULTY_OPTIONS = DIFFICULTY_OPTIONS;
exports.KNOWLEDGE_POINTS = KNOWLEDGE_POINTS;
exports.PAPER_STRATEGIES = PAPER_STRATEGIES;
exports.PAPER_STRATEGY_MAP = PAPER_STRATEGY_MAP;
exports.QUESTION_COUNT_OPTIONS = QUESTION_COUNT_OPTIONS;
exports.QUESTION_TYPE_MAP = QUESTION_TYPE_MAP;
exports.TIME_LIMIT_OPTIONS = TIME_LIMIT_OPTIONS;
exports.WRONG_BOOK_KNOWLEDGE_POINTS = WRONG_BOOK_KNOWLEDGE_POINTS;
exports.WRONG_REASONS = WRONG_REASONS;
