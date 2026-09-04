import type { Difficulty, ExamType, OptionItem } from './exam'

export interface WrongBookListItem {
  id: number
  examType: ExamType
  subject: string
  typeLabel: string
  diffLabel: string
  difficulty: Difficulty
  knowledgePoint: string
  wrongCount: number
  mastered: boolean
  stem: string
  lastWrongAt: string
}

export interface WrongBookDetail {
  id: number
  examType: ExamType
  subject: string
  typeLabel: string
  diffLabel: string
  difficulty: Difficulty
  knowledgePoint: string
  wrongCount: number
  mastered: boolean
  stem: string
  options: OptionItem[]
  answer: string
  myAnswer: string
  analysis: string
  confusion?: string
}

export interface RelatedQuestion {
  id: number
  stem: string
  typeLabel: string
  diffLabel: string
  difficulty: Difficulty
}
