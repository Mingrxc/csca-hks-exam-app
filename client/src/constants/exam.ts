import type {
  Difficulty,
  DifficultyFilter,
  ExamType,
  PaperStrategy,
  PaperStrategyItem,
  QuestionType,
} from '@/types/exam'

// Preserve the existing API/database identifier; show the correct exam name.
export function getExamLabel(examType: string): string {
  return examType === 'HKS' ? 'HSK' : examType
}

export function getPaperTitle(title: string): string {
  return title.replace(/\bHKS\b/g, 'HSK')
}

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
    icon: '随机',
    title: '随机练习',
    desc: '选择题量和难度，开始一组日常练习',
    shortDesc: '从题库随机抽取题目',
  },
  {
    key: 'knowledge',
    icon: '专项',
    title: '专项训练',
    desc: '按科目或知识点做针对性训练',
    shortDesc: '按分类做针对性训练',
  },
  {
    key: 'progressive',
    icon: '递进',
    title: '难度递进',
    desc: '从易到难，逐步提升',
    shortDesc: '逐步提升题目难度',
  },
  {
    key: 'real',
    icon: '模拟',
    title: '限时综合练习',
    desc: '按科目或等级完成限时练习，熟悉答题节奏',
    shortDesc: '限时练习，熟悉答题节奏',
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
export const TIME_LIMIT_OPTIONS = [30, 45, 60, 90, 105, 120]

// Available categories and timed profiles are provided by the backend bank.
export const CSCA_SUBJECT_OPTIONS = [
  '数学',
  '物理',
  '化学',
  '理科中文',
  '文科中文',
]

export const HSK_KNOWLEDGE_OPTIONS = [
  '听力理解',
  '阅读理解',
  '书写表达',
  '翻译表达',
  '词汇语法',
]

export const HSK_CATEGORY_OPTIONS = [
  '听力',
  '阅读',
  '书写',
  '写作',
  '翻译',
]

export const WRONG_BOOK_KNOWLEDGE_POINTS = [
  '听力理解',
  '阅读理解',
  '书写表达',
  '翻译表达',
  '词汇语法',
]

export const WRONG_REASONS = [
  '知识点不会',
  '粗心大意',
  '审题错误',
  '时间不够',
  '选项混淆',
  '其他',
]

export function getSpecialLabel(examType: ExamType): string {
  return examType === 'CSCA' ? '科目' : '知识点'
}

export function getSpecialOptions(examType: ExamType): string[] {
  return examType === 'CSCA' ? CSCA_SUBJECT_OPTIONS : HSK_KNOWLEDGE_OPTIONS
}

export function getQuestionDomain(question: { examType?: ExamType; subject?: string; knowledgePoint?: string }): string {
  return question.examType === 'CSCA' ? question.subject || '' : question.knowledgePoint || ''
}

export function getQuestionDomainLabel(examType: ExamType): string {
  return examType === 'CSCA' ? '科目' : '知识点'
}
