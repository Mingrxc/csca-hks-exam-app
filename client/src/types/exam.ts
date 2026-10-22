export type ExamType = 'CSCA' | 'HKS'
export type QuestionType = 'single' | 'multi' | 'judge' | 'fill'
export type Difficulty = 'easy' | 'medium' | 'hard'
export type DifficultyFilter = 'all' | Difficulty
export type PaperStrategy = 'random' | 'knowledge' | 'progressive' | 'real'
export type ExamMode = 'exam' | 'practice'

export interface OptionItem {
  key: string
  text: string
  image?: string
}

export interface Question {
  id: number
  examType: ExamType
  subject: string
  type: QuestionType
  difficulty: Difficulty
  knowledgePoint?: string
  stem: string
  options: OptionItem[]
  answer?: string
  analysis?: string
  wrongCount?: number
  isFavorite?: boolean
  bankId?: string
  examVersion?: string
  level?: string
  knowledgeModule?: string
  materialId?: string
  responseMode?: string
  scoringMode?: string
  nativeTask?: string
  sourceType?: string
  sourceLanguage?: string
  targetLanguage?: string
  stimulusNote?: string
  termNotes?: Record<string, string>
  stemImage?: string
  stemAudio?: string
  transcript?: string
  maxScore?: number
  minimumCharacters?: number
  responseSeconds?: number
  gradingKeyPoints?: string[]
  gradingRubric?: Array<{ dimension: string; max_score: number; criteria: string }>
  acceptedAnswers?: string[]
  evaluationStatus?: string
  selfScore?: number | null
}

export interface ExamConfig {
  examType: ExamType
  questionCount: number
  difficulty: DifficultyFilter
  strategy: PaperStrategy
  knowledgePoints: string[]
  mode: ExamMode
  timeLimit: number
  examVersion?: string
  level?: string
  subjects?: string[]
  knowledgeModules?: string[]
}

export interface PaperStrategyItem {
  key: PaperStrategy
  icon: string
  title: string
  desc: string
  shortDesc?: string
}

export interface HistoryPaper {
  objectiveCount?: number
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
  objectiveCount?: number
  subjectiveCount?: number
  pendingSelfReview?: number
  selfScore?: number
  selfMaxScore?: number
  subjectiveAnsweredCount?: number
  unansweredCount?: number
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
  correct: boolean | null
  question?: Question
  evaluationStatus?: string
  selfScore?: number | null
}
