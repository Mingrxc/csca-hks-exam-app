import type {
  Difficulty,
  ExamType,
  ExamResultSummary,
  HistoryPaper,
  Question,
  ResultReviewQuestion,
  ResultWrongQuestion,
} from '@/types/exam'
import type { DashboardData, ExamTargetDates, UserProfile } from '@/types/user'
import type { RelatedQuestion, WrongBookDetail, WrongBookListItem } from '@/types/wrongbook'
import { DIFFICULTY_MAP, QUESTION_TYPE_MAP } from '@/constants/exam'

export interface ApiQuestion {
  id: number
  exam_type: ExamType
  subject: string
  knowledge_point: string
  difficulty: Question['difficulty']
  question_type: Question['type']
  stem_text: string
  options: Question['options']
  answer?: string
  analysis?: string
  is_favorite?: boolean
}

export interface ApiPaper {
  id: number
  title: string
  exam_type: ExamType
  strategy: string
  question_ids: number[]
  total_score: number
  time_limit: number
  mode: string
  difficulty: string
  questions: ApiQuestion[]
}

export interface ApiSpecialOption {
  value: string
  label: string
  count: number
}

export interface ApiHistoryPaper {
  id: number
  title: string
  exam_type: string
  question_count: number
  score: number
  correct_rate: number
  time_used: number
  passed: boolean
  finished_at: string
}

export interface ApiUser {
  id: number
  nickname: string
  avatar_url?: string
  target_exam: 'CSCA' | 'HKS'
  target_date?: string
  target_dates?: Partial<Record<ExamType, string>>
  total_questions: number
  total_correct: number
  correct_rate: number
  streak_days: number
  favorite_count: number
}

export interface ApiDashboard {
  user_name: string
  target_exam: 'CSCA' | 'HKS'
  target_date?: string
  target_dates?: Partial<Record<ExamType, string>>
  today_stats: {
    question_count: number
    correct_rate: number
    wrong_count: number
  }
  pending_wrong_count: number
  favorite_count: number
  recent_papers: ApiHistoryPaper[]
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
  paper: ApiPaper
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
  review_questions: Array<{
    id: number
    stem: string
    type_label: string
    options: Question['options']
    user_answer: string
    correct_answer: string
    analysis: string
    is_correct: boolean
  }>
}

export interface ApiWrongBookItem {
  id: number
  question_id: number
  exam_type: ExamType
  subject: string
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

export interface ApiFavoriteStatus {
  question_id: number
  is_favorite: boolean
  favorite_count: number
}

export interface ApiFavoriteItem {
  id: number
  question_id: number
  question: ApiQuestion
  note?: string
  created_at: string
}

export interface ApiContentItem {
  id: number
  category: 'consulting' | 'club' | 'ad' | 'notice'
  title: string
  summary: string
  body: string
  cover_image?: string
  link_url?: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ApiAIReply {
  reply: string
  model: string
  usage: Record<string, number>
}

export function toQuestion(item: ApiQuestion): Question {
  return {
    id: item.id,
    examType: item.exam_type,
    subject: item.subject,
    type: item.question_type,
    difficulty: item.difficulty,
    knowledgePoint: item.knowledge_point,
    stem: item.stem_text,
    options: item.options,
    answer: item.answer,
    analysis: item.analysis,
    isFavorite: item.is_favorite,
  }
}

export function toHistoryPaper(item: ApiHistoryPaper): HistoryPaper {
  return {
    id: item.id,
    title: item.title,
    correctRate: item.correct_rate,
    timeUsed: formatSeconds(item.time_used),
    date: item.finished_at?.slice(0, 10) || '',
    passed: item.passed,
  }
}

export function toDashboardData(item: ApiDashboard): DashboardData {
  return {
    userName: item.user_name,
    targetExam: item.target_exam,
    targetDate: item.target_date || '',
    targetDates: normalizeTargetDates(item.target_dates, item.target_exam, item.target_date),
    countdown: calculateCountdown(item.target_date),
    todayStats: {
      questionCount: item.today_stats.question_count,
      correctRate: item.today_stats.correct_rate,
      wrongCount: item.today_stats.wrong_count,
    },
    pendingWrongCount: item.pending_wrong_count,
    favoriteCount: item.favorite_count,
    recentPapers: item.recent_papers.map((paper) => ({
      id: paper.id,
      title: paper.title,
      questionCount: paper.question_count,
      score: paper.score,
      date: paper.finished_at?.slice(0, 10) || '',
    })),
  }
}

export function toUserProfile(item: ApiUser): UserProfile {
  return {
    nickname: item.nickname,
    avatarUrl: item.avatar_url || '',
    targetExam: item.target_exam,
    targetDate: item.target_date || '',
    targetDates: normalizeTargetDates(item.target_dates, item.target_exam, item.target_date),
    totalQuestions: item.total_questions,
    correctRate: item.correct_rate,
    streakDays: item.streak_days,
    favoriteCount: item.favorite_count,
  }
}

function normalizeTargetDates(
  targetDates: ApiUser['target_dates'],
  targetExam?: ExamType,
  targetDate?: string,
): ExamTargetDates {
  const normalized: ExamTargetDates = {}
  if (targetDates?.CSCA) normalized.CSCA = targetDates.CSCA
  if (targetDates?.HKS) normalized.HKS = targetDates.HKS
  if (!Object.keys(normalized).length && targetExam && targetDate) {
    normalized[targetExam] = targetDate
  }
  return normalized
}

function calculateCountdown(targetDate?: string) {
  if (!targetDate) return { days: '0', hours: '00', minutes: '00' }
  const [year, month, day] = targetDate.split('-').map(Number)
  const target = new Date(year, month - 1, day, 23, 59, 59).getTime()
  const remaining = Math.max(target - Date.now(), 0)
  const days = Math.floor(remaining / 86400000)
  const hours = Math.floor((remaining % 86400000) / 3600000)
  const minutes = Math.floor((remaining % 3600000) / 60000)
  return {
    days: String(days),
    hours: String(hours).padStart(2, '0'),
    minutes: String(minutes).padStart(2, '0'),
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

export function toResultReviewQuestions(item: ApiExamResult): ResultReviewQuestion[] {
  return item.review_questions.map((question) => ({
    id: question.id,
    stem: question.stem,
    typeLabel: QUESTION_TYPE_MAP[question.type_label as Question['type']] || question.type_label,
    options: question.options,
    userAnswer: question.user_answer,
    correctAnswer: question.correct_answer,
    analysis: question.analysis,
    correct: question.is_correct,
  }))
}

export function toWrongBookListItem(item: ApiWrongBookItem): WrongBookListItem {
  return {
    id: item.id,
    examType: item.exam_type,
    subject: item.subject,
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
