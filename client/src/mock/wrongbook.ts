import type { RelatedQuestion, WrongBookDetail, WrongBookListItem } from '@/types/wrongbook'

export const mockWrongBookList: WrongBookListItem[] = [
  {
    id: 1,
    examType: 'CSCA',
    typeLabel: '单选',
    diffLabel: '中等',
    difficulty: 'medium',
    knowledgePoint: '文化常识',
    wrongCount: 3,
    mastered: false,
    stem: '在中国传统文化中，"五行"指的是哪五种元素？',
    lastWrongAt: '2026-07-08',
  },
  {
    id: 2,
    examType: 'HKS',
    typeLabel: '多选',
    diffLabel: '困难',
    difficulty: 'hard',
    knowledgePoint: '阅读理解',
    wrongCount: 2,
    mastered: false,
    stem: '关于"一带一路"倡议，以下说法正确的有哪些？',
    lastWrongAt: '2026-07-07',
  },
  {
    id: 3,
    examType: 'CSCA',
    typeLabel: '判断',
    diffLabel: '简单',
    difficulty: 'easy',
    knowledgePoint: '词汇语法',
    wrongCount: 1,
    mastered: true,
    stem: '"不仅...而且..."表示递进关系，对吗？',
    lastWrongAt: '2026-07-05',
  },
]

export const mockWrongBookDetail: WrongBookDetail = {
  id: 1,
  examType: 'CSCA',
  typeLabel: '单选',
  diffLabel: '中等',
  difficulty: 'medium',
  knowledgePoint: '文化常识',
  wrongCount: 3,
  mastered: false,
  stem: '在中国传统文化中，"五行"指的是哪五种元素？',
  options: [
    { key: 'A', text: '金、木、水、火、土' },
    { key: 'B', text: '金、木、水、火、风' },
    { key: 'C', text: '天、地、人、和、气' },
    { key: 'D', text: '东、西、南、北、中' },
  ],
  answer: 'A',
  myAnswer: 'B',
  analysis: '"五行"是中国古代哲学的基本概念，指金、木、水、火、土五种基本物质及其运动变化。这一概念最早见于《尚书·洪范》。古人认为宇宙万物都由这五种基本物质的运行和变化构成。',
  confusion: 'B选项中的"风"并非"五行"之一，"五行"固定为金木水火土，不含风。C选项为干扰项，与"三才"（天地人）概念混淆。D选项将"五行"与"五方"混淆。',
}

export const mockRelatedQuestions: RelatedQuestion[] = [
  { id: 101, stem: '以下哪项不属于中国古代的"四书"...', typeLabel: '单选', diffLabel: '中等', difficulty: 'medium' },
  { id: 102, stem: '"阴阳"学说最早系统记载于哪部著作...', typeLabel: '单选', diffLabel: '困难', difficulty: 'hard' },
  { id: 103, stem: '中国的"八卦"体系共有多少卦象...', typeLabel: '单选', diffLabel: '简单', difficulty: 'easy' },
]
