"use strict";
const common_vendor = require("../../common/vendor.js");
const mock_exam = require("../../mock/exam.js");
if (!Array) {
  const _easycom_c_question_item2 = common_vendor.resolveComponent("c-question-item");
  _easycom_c_question_item2();
}
const _easycom_c_question_item = () => "../../components/QuestionItem/index.js";
if (!Math) {
  _easycom_c_question_item();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "redo",
  setup(__props) {
    const currentIndex = common_vendor.ref(0);
    const answers = common_vendor.ref({});
    const showResult = common_vendor.ref({});
    const questions = common_vendor.ref(mock_exam.mockRedoQuestions);
    const currentQuestion = common_vendor.computed(() => questions.value[currentIndex.value]);
    const progressPercent = common_vendor.computed(() => {
      const answered = Object.keys(answers.value).length;
      return Math.round(answered / questions.value.length * 100);
    });
    const selectOption = (key) => {
      if (showResult.value[currentIndex.value])
        return;
      answers.value[currentIndex.value] = key;
      showResult.value[currentIndex.value] = true;
    };
    const prevQuestion = () => {
      if (currentIndex.value > 0)
        currentIndex.value--;
    };
    const nextQuestion = () => {
      if (currentIndex.value < questions.value.length - 1)
        currentIndex.value++;
    };
    const confirmExit = () => {
      common_vendor.index.showModal({
        title: "确认退出",
        content: "退出后进度将不会保存，确定退出吗？",
        success: (res) => {
          if (res.confirm)
            common_vendor.index.navigateBack();
        }
      });
    };
    const finishRedo = () => {
      common_vendor.index.showToast({ title: "错题重做完成！", icon: "success" });
      setTimeout(() => common_vendor.index.navigateBack(), 1500);
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(confirmExit, "cf"),
        b: common_vendor.t(currentIndex.value + 1),
        c: common_vendor.t(questions.value.length),
        d: progressPercent.value + "%",
        e: common_vendor.o(selectOption, "2a"),
        f: common_vendor.p({
          question: currentQuestion.value,
          index: currentIndex.value,
          ["user-answer"]: answers.value[currentIndex.value] || "",
          ["show-result"]: !!showResult.value[currentIndex.value]
        }),
        g: currentIndex.value === 0,
        h: common_vendor.o(prevQuestion, "3b"),
        i: currentIndex.value < questions.value.length - 1
      }, currentIndex.value < questions.value.length - 1 ? {
        j: common_vendor.o(nextQuestion, "ad")
      } : {
        k: common_vendor.o(finishRedo, "40")
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-931ddee6"]]);
wx.createPage(MiniProgramPage);
