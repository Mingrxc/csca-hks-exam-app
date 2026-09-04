"use strict";
const common_vendor = require("../../common/vendor.js");
const constants_exam = require("../../constants/exam.js");
const api_index = require("../../api/index.js");
const stores_exam = require("../../stores/exam.js");
if (!Array) {
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  const _easycom_c_countdown_bar2 = common_vendor.resolveComponent("c-countdown-bar");
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_c_question_item2 = common_vendor.resolveComponent("c-question-item");
  const _easycom_c_answer_card2 = common_vendor.resolveComponent("c-answer-card");
  (_easycom_t_button2 + _easycom_c_countdown_bar2 + _easycom_t_tag2 + _easycom_c_question_item2 + _easycom_c_answer_card2)();
}
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
const _easycom_c_countdown_bar = () => "../../components/CountdownBar/index.js";
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_c_question_item = () => "../../components/QuestionItem/index.js";
const _easycom_c_answer_card = () => "../../components/AnswerCard/index.js";
if (!Math) {
  (_easycom_t_button + _easycom_c_countdown_bar + _easycom_t_tag + _easycom_c_question_item + _easycom_c_answer_card)();
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
    const selectedReasons = common_vendor.ref({});
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
    const currentSelectedReason = common_vendor.computed(() => selectedReasons.value[currentIndex.value] || "");
    const wrongReasons = constants_exam.WRONG_REASONS;
    const toggleFavorite = async () => {
      if (!currentQuestion.value)
        return;
      try {
        const status = await api_index.favoriteApi.toggle(currentQuestion.value.id);
        currentQuestion.value.isFavorite = status.is_favorite;
        common_vendor.index.showToast({ title: status.is_favorite ? "已收藏" : "已取消收藏", icon: "none" });
      } catch {
      }
    };
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
          wrongReason: currentSelectedReason.value || void 0
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
      const index = currentIndex.value;
      const previousReason = selectedReasons.value[index];
      selectedReasons.value[index] = reason;
      const answer = answers.value[index];
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
          answerCorrectness.value[index] = response.is_correct;
        }
      } catch {
        if (previousReason == null) {
          delete selectedReasons.value[index];
        } else {
          selectedReasons.value[index] = previousReason;
        }
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
      var _a;
      return common_vendor.e({
        a: common_vendor.o(confirmExit, "f1"),
        b: common_vendor.p({
          theme: "default",
          variant: "text",
          size: "small",
          shape: "round"
        }),
        c: common_vendor.t(currentIndex.value + 1),
        d: common_vendor.t(questions.value.length),
        e: mode.value === "exam"
      }, mode.value === "exam" ? {
        f: common_vendor.o(($event) => submitExam(true), "97"),
        g: common_vendor.p({
          seconds: remainingSeconds.value
        })
      } : {}, {
        h: common_vendor.t(mode.value === "exam" ? "考试模式" : "练习模式"),
        i: common_vendor.p({
          theme: mode.value === "exam" ? "danger" : "success",
          variant: "light",
          shape: "round"
        }),
        j: progressPercent.value + "%",
        k: currentQuestion.value
      }, currentQuestion.value ? {
        l: common_vendor.o(selectOption, "03"),
        m: common_vendor.o(toggleFavorite, "60"),
        n: common_vendor.p({
          question: currentQuestion.value,
          index: currentIndex.value,
          ["user-answer"]: answers.value[currentIndex.value] || "",
          ["show-result"]: !!showResult.value[currentIndex.value],
          ["is-favorite"]: (_a = currentQuestion.value) == null ? void 0 : _a.isFavorite
        })
      } : {}, {
        o: showResult.value[currentIndex.value] && !currentCorrect.value
      }, showResult.value[currentIndex.value] && !currentCorrect.value ? {
        p: common_vendor.f(common_vendor.unref(wrongReasons), (r, k0, i0) => {
          return {
            a: common_vendor.t(r),
            b: currentSelectedReason.value === r ? 1 : "",
            c: r,
            d: common_vendor.o(($event) => selectWrongReason(r), r)
          };
        })
      } : {}, {
        q: "q-" + currentIndex.value,
        r: "q-" + currentIndex.value,
        s: showSheet.value
      }, showSheet.value ? {
        t: common_vendor.o(jumpToAndClose, "3b"),
        v: common_vendor.p({
          items: answerSheetItems.value,
          total: questions.value.length,
          ["answered-count"]: answeredCount.value,
          current: currentIndex.value
        }),
        w: common_vendor.o(($event) => showSheet.value = false, "8f"),
        x: common_vendor.p({
          block: true,
          theme: "default",
          variant: "outline",
          shape: "round"
        }),
        y: common_vendor.o(() => {
        }, "59"),
        z: common_vendor.o(($event) => showSheet.value = false, "99")
      } : {}, {
        A: common_vendor.o(($event) => showSheet.value = true, "5b"),
        B: common_vendor.p({
          theme: "default",
          variant: "outline",
          shape: "round"
        }),
        C: common_vendor.o(prevQuestion, "ad"),
        D: common_vendor.p({
          theme: "default",
          variant: "outline",
          shape: "round",
          disabled: currentIndex.value === 0
        }),
        E: currentIndex.value < questions.value.length - 1
      }, currentIndex.value < questions.value.length - 1 ? {
        F: common_vendor.o(nextQuestion, "3b"),
        G: common_vendor.p({
          theme: "primary",
          shape: "round"
        })
      } : {
        H: common_vendor.o(($event) => submitExam(), "a8"),
        I: common_vendor.p({
          theme: "primary",
          shape: "round"
        })
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-4ccad735"]]);
wx.createPage(MiniProgramPage);
