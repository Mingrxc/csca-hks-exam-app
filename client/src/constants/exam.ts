import type {
  Difficulty,
  DifficultyFilter,
  PaperStrategy,
  PaperStrategyItem,
  QuestionType,
} from '@/types/exam'

export const QUESTION_TYPE_MAP: Record<QuestionType, string> = {
  single: '单选',
  multi: '多选',
  judge: '判断',
  fill: '填空',
}

export const DIFFICULTY_MAP: Record<Difficulty, string> = {
  easy: '简单',
  medium: '中等',
  hard: '困难',
}

export const PAPER_STRATEGIES: PaperStrategyItem[] = [
  {
    key: 'random',
    icon: '🎲',
    title: '随机组卷',
    desc: '从题库随机抽取，全面检测',
    shortDesc: '从题库随机抽取题目',
  },
  {
    key: 'knowledge',
    icon: '📚',
    title: '知识点专项',
    desc: '针对性练习薄弱知识点',
    shortDesc: '针对薄弱环节强化',
  },
  {
    key: 'progressive',
    icon: '📈',
    title: '难度递进',
    desc: '从易到难，逐步提升',
    shortDesc: '逐步提升题目难度',
  },
  {
    key: 'real',
    icon: '🎯',
    title: '模拟真题',
    desc: '按历年真题比例组卷',
    shortDesc: '按真题比例组卷',
  },
]

export const PAPER_STRATEGY_MAP = PAPER_STRATEGIES.reduce(
  (map, item) => {
    map[item.key] = item
    return map
  },
  {} as Record<PaperStrategy, PaperStrategyItem>,
)

export const DIFFICULTY_OPTIONS: Array<{ label: string; value: DifficultyFilter }> = [
  { label: '全部', value: 'all' },
  { label: '简单', value: 'easy' },
  { label: '中等', value: 'medium' },
  { label: '困难', value: 'hard' },
]

export const QUESTION_COUNT_OPTIONS = [10, 20, 30, 50]
export const TIME_LIMIT_OPTIONS = [30, 45, 60, 90, 120]

export const KNOWLEDGE_POINTS = [
  '词汇语法',
  '阅读理解',
  '听力理解',
  '文化常识',
  '逻辑推理',
  '写作表达',
]

export const WRONG_BOOK_KNOWLEDGE_POINTS = [
  '词汇语法',
  '阅读理解',
  '文化常识',
  '逻辑推理',
]

export const WRONG_REASONS = [
  '知识点不会',
  '粗心大意',
  '审题错误',
  '时间不够',
  '选项混淆',
  '其他',
]
