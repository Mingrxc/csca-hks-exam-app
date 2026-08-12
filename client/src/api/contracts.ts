import type {
  Difficulty,
  ExamResultSummary,
  HistoryPaper,
  Question,
  ResultWrongQuestion,
} from '@/types/exam'
import type { RelatedQuestion, WrongBookDetail, WrongBookListItem } from '@/types/wrongbook'
import { DIFFICULTY_MAP, QUESTION_TYPE_MAP } from '@/constants/exam'

export interface ApiQuestion {
  id: number
  exam_type: string
  subject: string
  knowledge_point: string
  difficulty: Question['difficulty']
  question_type: Question['type']
  stem_text: string
  options: Question['options']
  answer?: string
  analysis?: string
}

export interface ApiPaper {
  id: number
  title: string
  exam_type: string
  strategy: string
  question_ids: number[]
  total_score: number
  time_limit: number
  mode: string
  difficulty: string
  questions: ApiQuestion[]
}

export interface ApiSubmitAnswerResult {
  paper_id: number
  question_id: number
  is_correct?: boolean
  correct_answer?: string
  user_answer: string
  recorded_new: boolean
  time_spent: number
}

export interface ApiExamResult {
  score: number
  correct_count: number
  total_count: number
  correct_rate: number
  time_used: number
  knowledge_analysis: Record<string, { total: number; correct: number; correct_rate: number }>
  wrong_questions: Array<{
    id: number
    stem: string
    type_label: string
    your_answer: string
    correct_answer: string
  }>
}

export interface ApiWrongBookItem {
  id: number
  question_id: number
  stem: string
  type: Question['type']
  difficulty: Difficulty
  knowledge_point: string
  wrong_count: number
  correct_count: number
  is_mastered: boolean
  last_wrong_at: string
}

export interface ApiWrongBookDetail extends ApiWrongBookItem {
  question: ApiQuestion
  last_user_answer: string
  wrong_options_analysis: Record<string, string>
}

export interface ApiRelatedQuestion extends ApiQuestion {
  similarity_score: number
}

export function toQuestion(item: ApiQuestion): Question {
  return {
    id: item.id,
    type: item.question_type,
    difficulty: item.difficulty,
    knowledgePoint: item.knowledge_point,
    stem: item.stem_text,
    options: item.options,
    answer: item.answer,
    analysis: item.analysis,
  }
}

export function toHistoryPaper(item: ApiPaper): HistoryPaper {
  return {
    id: item.id,
    title: item.title,
    correctRate: 0,
    timeUsed: '--:--',
    date: '',
    passed: false,
  }
}

export function toExamResultSummary(item: ApiExamResult): ExamResultSummary {
  return {
    score: item.score,
    correctCount: item.correct_count,
    totalCount: item.total_count,
    correctRate: item.correct_rate,
    timeUsed: formatSeconds(item.time_used),
  }
}

export function toResultWrongQuestions(item: ApiExamResult): ResultWrongQuestion[] {
  return item.wrong_questions.map((question) => ({
    id: question.id,
    stem: question.stem,
    typeLabel: question.type_label,
    yourAnswer: question.your_answer,
    correctAnswer: question.correct_answer,
  }))
}

export function toWrongBookListItem(item: ApiWrongBookItem): WrongBookListItem {
  return {
    id: item.id,
    typeLabel: QUESTION_TYPE_MAP[item.type] || item.type,
    diffLabel: DIFFICULTY_MAP[item.difficulty] || item.difficulty,
    difficulty: item.difficulty,
    knowledgePoint: item.knowledge_point,
    wrongCount: item.wrong_count,
    mastered: item.is_mastered,
    stem: item.stem,
    lastWrongAt: item.last_wrong_at?.slice(0, 10) || '',
  }
}

export function toWrongBookDetail(item: ApiWrongBookDetail): WrongBookDetail {
  const question = toQuestion(item.question)
  const confusionEntries = Object.entries(item.wrong_options_analysis)
  return {
    ...toWrongBookListItem(item),
    options: question.options,
    answer: question.answer || '',
    myAnswer: item.last_user_answer,
    analysis: question.analysis || '暂无解析',
    confusion: confusionEntries
      .map(([option, text]) => `${option}：${text}`)
      .join('\n'),
  }
}

export function toRelatedQuestion(item: ApiRelatedQuestion): RelatedQuestion {
  return {
    id: item.id,
    stem: item.stem_text,
    typeLabel: QUESTION_TYPE_MAP[item.question_type] || item.question_type,
    diffLabel: DIFFICULTY_MAP[item.difficulty] || item.difficulty,
    difficulty: item.difficulty,
  }
}

export function formatSeconds(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remaining = seconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(remaining).padStart(2, '0')}`
}
