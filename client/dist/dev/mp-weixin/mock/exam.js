"use strict";
const mockExamQuestions = [
  {
    id: 1,
    type: "single",
    difficulty: "medium",
    knowledgePoint: "文化常识",
    stem: '在中国传统文化中，"五行"指的是哪五种元素？',
    options: [
      { key: "A", text: "金、木、水、火、土" },
      { key: "B", text: "金、木、水、火、风" },
      { key: "C", text: "天、地、人、和、气" },
      { key: "D", text: "东、西、南、北、中" }
    ],
    answer: "A",
    analysis: '"五行"是中国古代哲学的基本概念，指金、木、水、火、土五种基本物质及其运动变化。这一概念最早见于《尚书·洪范》。'
  },
  {
    id: 2,
    type: "single",
    difficulty: "easy",
    knowledgePoint: "中国地理",
    stem: "中国的首都是哪个城市？",
    options: [
      { key: "A", text: "上海" },
      { key: "B", text: "北京" },
      { key: "C", text: "广州" },
      { key: "D", text: "深圳" }
    ],
    answer: "B",
    analysis: "北京是中华人民共和国的首都，也是政治、文化、国际交往和科技创新的中心。"
  }
];
const mockRedoQuestions = [
  {
    ...mockExamQuestions[0],
    wrongCount: 3,
    analysis: '"五行"指金、木、水、火、土五种基本物质及其运动变化，最早见于《尚书·洪范》。'
  }
];
const mockHistoryPapers = [];
exports.mockHistoryPapers = mockHistoryPapers;
exports.mockRedoQuestions = mockRedoQuestions;
