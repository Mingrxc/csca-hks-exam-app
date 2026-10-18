import { getExamLabel } from '@/constants/exam'
import { useUserStore } from '@/stores/user'
import type { ExamType, PaperStrategy } from '@/types/exam'

export function useExamNavigation() {
  const userStore = useUserStore()

  function chooseExam(action: string, open: (exam: ExamType) => void) {
    if (userStore.selectedExams.length === 1) {
      open(userStore.selectedExams[0])
      return
    }

    // A paper has one exam type; choosing this session does not change study goals.
    const exams: ExamType[] = ['HKS', 'CSCA']
    uni.showActionSheet({
      itemList: exams.map((exam) => `${getExamLabel(exam)} ${action}`),
      success: ({ tapIndex }) => {
        const exam = exams[tapIndex]
        if (exam) open(exam)
      },
    })
  }

  const goPractice = (strategy: PaperStrategy) => chooseExam('练习', (exam) => {
    uni.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}&examType=${exam}` })
  })
  const goWrongRedo = () => chooseExam('错题重做', (exam) => {
    uni.navigateTo({ url: `/pages/wrongbook/redo?examType=${exam}` })
  })

  return { goPractice, goWrongRedo }
}
