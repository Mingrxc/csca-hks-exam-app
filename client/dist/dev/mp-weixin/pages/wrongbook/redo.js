"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const stores_exam = require("../../stores/exam.js");
if (!Array) {
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_c_question_item2 = common_vendor.resolveComponent("c-question-item");
  (_easycom_t_button2 + _easycom_t_tag2 + _easycom_c_question_item2)();
}
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_c_question_item = () => "../../components/QuestionItem/index.js";
if (!Math) {
  (_easycom_t_button + _easycom_t_tag + _easycom_c_question_item)();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "redo",
  setup(__props) {
    const examStore = stores_exam.useExamStore();
    const currentIndex = common_vendor.ref(0);
    const answers = common_vendor.ref({});
    const showResult = common_vendor.ref({});
    const questions = common_vendor.ref([]);
    const paperId = common_vendor.ref(null);
    const isLoading = common_vendor.ref(false);
    const isSubmitting = common_vendor.ref(false);
    const questionStartedAt = common_vendor.ref(Date.now());
    const elapsedSeconds = common_vendor.ref({});
    const currentQuestion = common_vendor.computed(() => questions.value[currentIndex.value] || null);
    const progressPercent = common_vendor.computed(() => {
      if (!questions.value.length)
        return 0;
      const answered = Object.keys(answers.value).length;
      return Math.round(answered / questions.value.length * 100);
    });
    const commitElapsedTime = () => {
      const index = currentIndex.value;
      const elapsed = Math.max(0, Math.floor((Date.now() - questionStartedAt.value) / 1e3));
      elapsedSeconds.value[index] = (elapsedSeconds.value[index] || 0) + elapsed;
      questionStartedAt.value = Date.now();
      return elapsedSeconds.value[index];
    };
    const loadRedoPaper = async (examType) => {
      if (isLoading.value)
        return;
      isLoading.value = true;
      try {
        const paper = await api_index.wrongBookApi.generateRedoPaper({ examType, limit: 20 });
        const mappedQuestions = paper.questions.map(api_contracts.toQuestion);
        paperId.value = paper.id;
        questions.value = mappedQuestions;
        currentIndex.value = 0;
        answers.value = {};
        showResult.value = {};
        elapsedSeconds.value = {};
        examStore.setConfig({
          examType,
          questionCount: mappedQuestions.length,
          difficulty: "all",
          strategy: "knowledge",
          knowledgePoints: [],
          mode: "practice",
          timeLimit: 0
        });
        examStore.setPaper(paper.id, mappedQuestions);
        examStore.start();
        questionStartedAt.value = Date.now();
      } catch {
        questions.value = [];
      } finally {
        isLoading.value = false;
      }
    };
    const selectOption = async (key) => {
      if (!currentQuestion.value || !paperId.value || isSubmitting.value)
        return;
      if (showResult.value[currentIndex.value])
        return;
      const index = currentIndex.value;
      answers.value[index] = key;
      examStore.setAnswer(index, key);
      isSubmitting.value = true;
      try {
        await api_index.examApi.submitAnswer({
          paperId: paperId.value,
          questionId: currentQuestion.value.id,
          userAnswer: key,
          timeSpent: commitElapsedTime()
        });
        showResult.value[index] = true;
      } catch {
        delete answers.value[index];
        examStore.clearAnswer(index);
      } finally {
        isSubmitting.value = false;
      }
    };
    const moveTo = (index) => {
      if (index < 0 || index >= questions.value.length || index === currentIndex.value)
        return;
      commitElapsedTime();
      currentIndex.value = index;
      examStore.setCurrentIndex(index);
    };
    const prevQuestion = () => moveTo(currentIndex.value - 1);
    const nextQuestion = () => moveTo(currentIndex.value + 1);
    const confirmExit = () => {
      common_vendor.index.showModal({
        title: "确认退出",
        content: "退出后当前重做进度将不会继续提交，确定退出吗？",
        success: (res) => {
          if (res.confirm)
            common_vendor.index.navigateBack();
        }
      });
    };
    const finishRedo = () => {
      if (!paperId.value) {
        common_vendor.index.navigateBack();
        return;
      }
      commitElapsedTime();
      examStore.finish();
      common_vendor.index.redirectTo({ url: `/pages/exam/result?paperId=${paperId.value}` });
    };
    const chooseExamType = () => {
      common_vendor.index.showActionSheet({
        itemList: ["CSCA 错题", "HKS 错题"],
        success: ({ tapIndex }) => loadRedoPaper(tapIndex === 0 ? "CSCA" : "HKS"),
        fail: () => common_vendor.index.navigateBack()
      });
    };
    common_vendor.onLoad((query) => {
      if ((query == null ? void 0 : query.examType) === "CSCA" || (query == null ? void 0 : query.examType) === "HKS") {
        loadRedoPaper(query.examType);
        return;
      }
      chooseExamType();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(confirmExit, "f1"),
        b: common_vendor.p({
          theme: "default",
          variant: "text",
          size: "small",
          shape: "round"
        }),
        c: common_vendor.t(questions.value.length ? currentIndex.value + 1 : 0),
        d: common_vendor.t(questions.value.length),
        e: common_vendor.p({
          theme: "danger",
          variant: "light",
          shape: "round"
        }),
        f: progressPercent.value + "%",
        g: currentQuestion.value
      }, currentQuestion.value ? {
        h: common_vendor.o(selectOption, "86"),
        i: common_vendor.p({
          question: currentQuestion.value,
          index: currentIndex.value,
          ["user-answer"]: answers.value[currentIndex.value] || "",
          ["show-result"]: !!showResult.value[currentIndex.value]
        })
      } : {
        j: common_vendor.t(isLoading.value ? "加载错题中..." : "暂无可重做错题")
      }, {
        k: common_vendor.o(prevQuestion, "e6"),
        l: common_vendor.p({
          theme: "default",
          variant: "outline",
          shape: "round",
          disabled: currentIndex.value === 0 || isLoading.value
        }),
        m: currentIndex.value < questions.value.length - 1
      }, currentIndex.value < questions.value.length - 1 ? {
        n: common_vendor.o(nextQuestion, "80"),
        o: common_vendor.p({
          theme: "primary",
          shape: "round",
          disabled: isLoading.value
        })
      } : {}, {
        p: common_vendor.o(finishRedo, "72"),
        q: common_vendor.p({
          theme: "primary",
          shape: "round",
          disabled: isLoading.value || !questions.value.length
        })
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-931ddee6"]]);
wx.createPage(MiniProgramPage);
