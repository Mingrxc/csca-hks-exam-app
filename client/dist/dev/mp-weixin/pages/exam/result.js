"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const stores_exam = require("../../stores/exam.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "result",
  setup(__props) {
    const examStore = stores_exam.useExamStore();
    const result = common_vendor.ref({
      score: 0,
      correctCount: 0,
      totalCount: 0,
      correctRate: 0,
      timeUsed: "00:00"
    });
    const knowledgeAnalysis = common_vendor.ref({});
    const isLoading = common_vendor.ref(false);
    const passed = common_vendor.computed(() => result.value.correctRate >= 60);
    const wrongQuestions = common_vendor.ref([]);
    const knowledgeItems = common_vendor.computed(
      () => Object.entries(knowledgeAnalysis.value).map(([name, value]) => ({
        name,
        correctRate: value.correct_rate
      }))
    );
    const timeUsagePercent = common_vendor.computed(() => {
      const [minutes, seconds] = result.value.timeUsed.split(":").map(Number);
      const usedSeconds = minutes * 60 + seconds;
      const configuredSeconds = examStore.config.timeLimit * 60;
      if (!configuredSeconds)
        return 100;
      return Math.min(100, Math.max(6, Math.round(usedSeconds / configuredSeconds * 100)));
    });
    const loadResult = async (paperId) => {
      if (isLoading.value)
        return;
      isLoading.value = true;
      try {
        const payload = await api_index.examApi.getResult(paperId);
        result.value = api_contracts.toExamResultSummary(payload);
        wrongQuestions.value = api_contracts.toResultWrongQuestions(payload);
        knowledgeAnalysis.value = payload.knowledge_analysis;
      } catch {
      } finally {
        isLoading.value = false;
      }
    };
    common_vendor.onLoad((query) => {
      const paperId = Number((query == null ? void 0 : query.paperId) || examStore.paperId);
      if (!Number.isInteger(paperId) || paperId <= 0) {
        common_vendor.index.showToast({ title: "未找到试卷结果", icon: "none" });
        setTimeout(() => common_vendor.index.navigateBack(), 300);
        return;
      }
      loadResult(paperId);
    });
    const goDetail = (id) => {
      common_vendor.index.navigateTo({ url: `/pages/wrongbook/detail?questionId=${id}` });
    };
    const reviewAll = () => console.log("查看全部解析");
    const goHome = () => common_vendor.index.switchTab({ url: "/pages/index/index" });
    const retryWrong = () => common_vendor.index.navigateTo({ url: "/pages/wrongbook/redo" });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(passed.value ? "恭喜通过！" : "继续加油"),
        b: common_vendor.t(result.value.score),
        c: common_vendor.t(result.value.correctCount),
        d: common_vendor.t(result.value.totalCount),
        e: common_vendor.t(result.value.correctRate),
        f: common_vendor.t(result.value.timeUsed),
        g: common_vendor.n(passed.value ? "passed" : "failed"),
        h: knowledgeItems.value.length
      }, knowledgeItems.value.length ? {
        i: common_vendor.f(knowledgeItems.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.name),
            b: item.correctRate + "%",
            c: common_vendor.t(item.correctRate),
            d: item.name
          };
        })
      } : {}, {
        j: timeUsagePercent.value + "%",
        k: common_vendor.t(result.value.timeUsed),
        l: wrongQuestions.value.length > 0
      }, wrongQuestions.value.length > 0 ? {
        m: common_vendor.t(wrongQuestions.value.length),
        n: common_vendor.f(wrongQuestions.value, (q, k0, i0) => {
          return {
            a: common_vendor.t(q.stem),
            b: common_vendor.t(q.typeLabel),
            c: common_vendor.t(q.yourAnswer),
            d: common_vendor.t(q.correctAnswer),
            e: q.id,
            f: common_vendor.o(($event) => goDetail(q.id), q.id)
          };
        })
      } : {}, {
        o: common_vendor.o(reviewAll, "8c"),
        p: common_vendor.o(goHome, "6e"),
        q: common_vendor.o(retryWrong, "d8")
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-419be219"]]);
wx.createPage(MiniProgramPage);
