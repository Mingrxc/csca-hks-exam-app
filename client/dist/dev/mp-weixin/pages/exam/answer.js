"use strict";
const common_vendor = require("../../common/vendor.js");
const constants_exam = require("../../constants/exam.js");
const api_index = require("../../api/index.js");
const stores_exam = require("../../stores/exam.js");
if (!Array) {
  const _easycom_c_countdown_bar2 = common_vendor.resolveComponent("c-countdown-bar");
  const _easycom_c_question_item2 = common_vendor.resolveComponent("c-question-item");
  const _easycom_c_answer_card2 = common_vendor.resolveComponent("c-answer-card");
  (_easycom_c_countdown_bar2 + _easycom_c_question_item2 + _easycom_c_answer_card2)();
}
const _easycom_c_countdown_bar = () => "../../components/CountdownBar/index.js";
const _easycom_c_question_item = () => "../../components/QuestionItem/index.js";
const _easycom_c_answer_card = () => "../../components/AnswerCard/index.js";
if (!Math) {
  (_easycom_c_countdown_bar + _easycom_c_question_item + _easycom_c_answer_card)();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "answer",
  setup(__props) {
    const examStore = stores_exam.useExamStore();
    const mode = common_vendor.computed(() => examStore.config.mode);
    const currentIndex = common_vendor.computed(() => examStore.currentIndex);
    const answers = common_vendor.computed(() => examStore.answers);
    const showResult = common_vendor.ref({});
    const answerCorrectness = common_vendor.ref({});
    const selectedReason = common_vendor.ref("");
    const showSheet = common_vendor.ref(false);
    const isSubmitting = common_vendor.ref(false);
    const questionStartedAt = common_vendor.ref(Date.now());
    const questionElapsedSeconds = common_vendor.ref({});
    const questions = common_vendor.computed(() => examStore.questions);
    const remainingSeconds = common_vendor.computed(() => examStore.config.timeLimit * 60);
    const currentQuestion = common_vendor.computed(() => examStore.currentQuestion);
    const progressPercent = common_vendor.computed(() => examStore.progressPercent);
    const answeredCount = common_vendor.computed(() => examStore.answeredCount);
    const currentCorrect = common_vendor.computed(() => answerCorrectness.value[currentIndex.value] === true);
    const wrongReasons = constants_exam.WRONG_REASONS;
    const commitElapsedTime = () => {
      const index = currentIndex.value;
      const elapsed = Math.max(0, Math.floor((Date.now() - questionStartedAt.value) / 1e3));
      questionElapsedSeconds.value[index] = (questionElapsedSeconds.value[index] || 0) + elapsed;
      questionStartedAt.value = Date.now();
      return questionElapsedSeconds.value[index];
    };
    const selectOption = async (key) => {
      if (!currentQuestion.value || !examStore.paperId || isSubmitting.value)
        return;
      if (showResult.value[currentIndex.value] && mode.value === "practice")
        return;
      isSubmitting.value = true;
      const index = currentIndex.value;
      const previousAnswer = answers.value[index];
      examStore.setAnswer(index, key);
      try {
        const response = await api_index.examApi.submitAnswer({
          paperId: examStore.paperId,
          questionId: currentQuestion.value.id,
          userAnswer: key,
          timeSpent: commitElapsedTime(),
          wrongReason: selectedReason.value || void 0
        });
        if (typeof response.is_correct === "boolean") {
          answerCorrectness.value[index] = response.is_correct;
        }
        if (mode.value === "practice") {
          showResult.value[index] = true;
        }
      } catch {
        if (previousAnswer == null) {
          examStore.clearAnswer(index);
        } else {
          examStore.setAnswer(index, previousAnswer);
        }
      } finally {
        isSubmitting.value = false;
      }
    };
    const selectWrongReason = async (reason) => {
      selectedReason.value = reason;
      const answer = answers.value[currentIndex.value];
      if (!answer || !currentQuestion.value || !examStore.paperId || isSubmitting.value)
        return;
      isSubmitting.value = true;
      try {
        const response = await api_index.examApi.submitAnswer({
          paperId: examStore.paperId,
          questionId: currentQuestion.value.id,
          userAnswer: answer,
          timeSpent: commitElapsedTime(),
          wrongReason: reason
        });
        if (typeof response.is_correct === "boolean") {
          answerCorrectness.value[currentIndex.value] = response.is_correct;
        }
      } catch {
      } finally {
        isSubmitting.value = false;
      }
    };
    const moveTo = (index) => {
      if (index === currentIndex.value)
        return;
      commitElapsedTime();
      examStore.setCurrentIndex(index);
    };
    const prevQuestion = () => moveTo(currentIndex.value - 1);
    const nextQuestion = () => moveTo(currentIndex.value + 1);
    const jumpTo = (i) => moveTo(i);
    const jumpToAndClose = (i) => {
      jumpTo(i);
      showSheet.value = false;
    };
    const answerSheetItems = common_vendor.computed(
      () => questions.value.map((_, index) => ({
        index,
        answered: answers.value[index] != null,
        marked: !!showResult.value[index]
      }))
    );
    const confirmExit = () => {
      common_vendor.index.showModal({
        title: "确认退出",
        content: "退出后答题进度将不会保存，确定退出吗？",
        success: (res) => {
          if (res.confirm)
            common_vendor.index.navigateBack();
        }
      });
    };
    const completeExam = () => {
      if (!examStore.paperId) {
        common_vendor.index.showToast({ title: "试卷信息已失效，请重新组卷", icon: "none" });
        common_vendor.index.navigateBack();
        return;
      }
      commitElapsedTime();
      examStore.finish();
      common_vendor.index.redirectTo({ url: `/pages/exam/result?paperId=${examStore.paperId}` });
    };
    const submitExam = (forced = false) => {
      if (forced) {
        completeExam();
        return;
      }
      const answered = Object.keys(answers.value).length;
      common_vendor.index.showModal({
        title: "确认交卷",
        content: `还有 ${questions.value.length - answered} 题未作答，确定交卷吗？`,
        success: (res) => {
          if (res.confirm) {
            completeExam();
          }
        }
      });
    };
    if (!examStore.paperId || questions.value.length === 0) {
      common_vendor.index.showToast({ title: "请先完成组卷", icon: "none" });
      setTimeout(() => common_vendor.index.navigateBack(), 300);
    }
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(confirmExit, "38"),
        b: common_vendor.t(currentIndex.value + 1),
        c: common_vendor.t(questions.value.length),
        d: mode.value === "exam"
      }, mode.value === "exam" ? {
        e: common_vendor.o(($event) => submitExam(true), "fd"),
        f: common_vendor.p({
          seconds: remainingSeconds.value
        })
      } : {}, {
        g: common_vendor.t(mode.value === "exam" ? "考试模式" : "练习模式"),
        h: common_vendor.n(mode.value),
        i: progressPercent.value + "%",
        j: currentQuestion.value
      }, currentQuestion.value ? {
        k: common_vendor.o(selectOption, "e7"),
        l: common_vendor.p({
          question: currentQuestion.value,
          index: currentIndex.value,
          ["user-answer"]: answers.value[currentIndex.value] || "",
          ["show-result"]: !!showResult.value[currentIndex.value]
        })
      } : {}, {
        m: showResult.value && !currentCorrect.value
      }, showResult.value && !currentCorrect.value ? {
        n: common_vendor.f(common_vendor.unref(wrongReasons), (r, k0, i0) => {
          return {
            a: common_vendor.t(r),
            b: selectedReason.value === r ? 1 : "",
            c: r,
            d: common_vendor.o(($event) => selectWrongReason(r), r)
          };
        })
      } : {}, {
        o: "q-" + currentIndex.value,
        p: "q-" + currentIndex.value,
        q: showSheet.value
      }, showSheet.value ? {
        r: common_vendor.o(jumpToAndClose, "a0"),
        s: common_vendor.p({
          items: answerSheetItems.value,
          total: questions.value.length,
          ["answered-count"]: answeredCount.value,
          current: currentIndex.value
        }),
        t: common_vendor.o(($event) => showSheet.value = false, "e9"),
        v: common_vendor.o(() => {
        }, "37"),
        w: common_vendor.o(($event) => showSheet.value = false, "8d")
      } : {}, {
        x: common_vendor.o(($event) => showSheet.value = true, "d2"),
        y: currentIndex.value === 0,
        z: common_vendor.o(prevQuestion, "28"),
        A: currentIndex.value < questions.value.length - 1
      }, currentIndex.value < questions.value.length - 1 ? {
        B: common_vendor.o(nextQuestion, "0f")
      } : {
        C: common_vendor.o(submitExam, "2f")
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-4ccad735"]]);
wx.createPage(MiniProgramPage);
