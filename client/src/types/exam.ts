export type ExamType = 'CSCA' | 'HKS'
export type QuestionType = 'single' | 'multi' | 'judge' | 'fill'
export type Difficulty = 'easy' | 'medium' | 'hard'
export type DifficultyFilter = 'all' | Difficulty
export type PaperStrategy = 'random' | 'knowledge' | 'progressive' | 'real'
export type ExamMode = 'exam' | 'practice'

export interface OptionItem {
  key: string
  text: string
}

export interface Question {
  id: number
  type: QuestionType
  difficulty: Difficulty
  knowledgePoint?: string
  stem: string
  options: OptionItem[]
  answer?: string
  analysis?: string
  wrongCount?: number
}

export interface ExamConfig {
  examType: ExamType
  questionCount: number
  difficulty: DifficultyFilter
  strategy: PaperStrategy
  knowledgePoints: string[]
  mode: ExamMode
  timeLimit: number
}

export interface PaperStrategyItem {
  key: PaperStrategy
  icon: string
  title: string
  desc: string
  shortDesc?: string
}

export interface HistoryPaper {
  id: number
  title: string
  correctRate: number
  timeUsed: string
  date: string
  passed: boolean
}

export interface ExamResultSummary {
  score: number
  correctCount: number
  totalCount: number
  correctRate: number
  timeUsed: string
}

export interface ResultWrongQuestion {
  id: number
  stem: string
  typeLabel: string
  yourAnswer: string
  correctAnswer: string
}

export interface ResultReviewQuestion {
  id: number
  stem: string
  typeLabel: string
  options: OptionItem[]
  userAnswer: string
  correctAnswer: string
  analysis: string
  correct: boolean
}
