"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const constants_exam = require("../../constants/exam.js");
const stores_exam = require("../../stores/exam.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "paper",
  setup(__props) {
    const examStore = stores_exam.useExamStore();
    const strategyType = common_vendor.ref("random");
    const isGenerating = common_vendor.ref(false);
    const currentStrategy = common_vendor.computed(() => constants_exam.PAPER_STRATEGY_MAP[strategyType.value] || constants_exam.PAPER_STRATEGY_MAP.random);
    const difficulties = constants_exam.DIFFICULTY_OPTIONS;
    const knowledgePoints = constants_exam.KNOWLEDGE_POINTS;
    const questionCountOptions = constants_exam.QUESTION_COUNT_OPTIONS;
    const timeLimitOptions = constants_exam.TIME_LIMIT_OPTIONS;
    const form = common_vendor.reactive({
      examType: "CSCA",
      questionCount: 20,
      difficulty: "all",
      knowledgePoints: [],
      mode: "practice",
      timeLimit: 60
    });
    const toggleKnowledge = (k) => {
      const idx = form.knowledgePoints.indexOf(k);
      if (idx >= 0) {
        form.knowledgePoints.splice(idx, 1);
      } else {
        form.knowledgePoints.push(k);
      }
    };
    common_vendor.onLoad((query) => {
      const strategy = query == null ? void 0 : query.strategy;
      if (typeof strategy === "string" && strategy in constants_exam.PAPER_STRATEGY_MAP) {
        strategyType.value = strategy;
      }
      const knowledge = query == null ? void 0 : query.knowledge;
      if (typeof knowledge === "string" && constants_exam.KNOWLEDGE_POINTS.includes(knowledge)) {
        form.knowledgePoints = [knowledge];
      }
    });
    const startExam = async () => {
      if (strategyType.value === "knowledge" && form.knowledgePoints.length === 0) {
        common_vendor.index.showToast({ title: "请至少选择一个知识点", icon: "none" });
        return;
      }
      if (isGenerating.value)
        return;
      isGenerating.value = true;
      try {
        const paper = await api_index.questionApi.generatePaper({
          examType: form.examType,
          questionCount: form.questionCount,
          difficulty: form.difficulty,
          strategy: strategyType.value,
          knowledgePoints: form.knowledgePoints,
          mode: form.mode,
          timeLimit: form.mode === "exam" ? form.timeLimit : 0
        });
        examStore.setConfig({
          ...form,
          strategy: strategyType.value,
          timeLimit: paper.time_limit
        });
        examStore.setPaper(paper.id, paper.questions.map(api_contracts.toQuestion));
        examStore.start();
        common_vendor.index.navigateTo({ url: "/pages/exam/answer" });
      } catch {
      } finally {
        isGenerating.value = false;
      }
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(currentStrategy.value.icon),
        b: common_vendor.t(currentStrategy.value.title),
        c: common_vendor.t(currentStrategy.value.desc),
        d: form.examType === "CSCA" ? 1 : "",
        e: common_vendor.o(($event) => form.examType = "CSCA", "58"),
        f: form.examType === "HKS" ? 1 : "",
        g: common_vendor.o(($event) => form.examType = "HKS", "6b"),
        h: common_vendor.f(common_vendor.unref(questionCountOptions), (n, k0, i0) => {
          return {
            a: common_vendor.t(n),
            b: form.questionCount === n ? 1 : "",
            c: n,
            d: common_vendor.o(($event) => form.questionCount = n, n)
          };
        }),
        i: common_vendor.f(common_vendor.unref(difficulties), (d, k0, i0) => {
          return {
            a: common_vendor.t(d.label),
            b: form.difficulty === d.value ? 1 : "",
            c: d.value,
            d: common_vendor.o(($event) => form.difficulty = d.value, d.value)
          };
        }),
        j: strategyType.value === "knowledge"
      }, strategyType.value === "knowledge" ? {
        k: common_vendor.f(common_vendor.unref(knowledgePoints), (k, k0, i0) => {
          return {
            a: common_vendor.t(k),
            b: form.knowledgePoints.includes(k) ? 1 : "",
            c: k,
            d: common_vendor.o(($event) => toggleKnowledge(k), k)
          };
        })
      } : {}, {
        l: form.mode === "exam" ? 1 : "",
        m: common_vendor.o(($event) => form.mode = "exam", "53"),
        n: form.mode === "practice" ? 1 : "",
        o: common_vendor.o(($event) => form.mode = "practice", "1f"),
        p: form.mode === "exam"
      }, form.mode === "exam" ? {
        q: common_vendor.f(common_vendor.unref(timeLimitOptions), (t, k0, i0) => {
          return {
            a: common_vendor.t(t),
            b: form.timeLimit === t ? 1 : "",
            c: t,
            d: common_vendor.o(($event) => form.timeLimit = t, t)
          };
        })
      } : {}, {
        r: common_vendor.t(form.questionCount),
        s: common_vendor.t(form.mode === "exam" ? "考试模式" : "练习模式"),
        t: form.mode === "exam"
      }, form.mode === "exam" ? {
        v: common_vendor.t(form.timeLimit)
      } : {}, {
        w: common_vendor.o(startExam, "8e")
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-ecefe579"]]);
wx.createPage(MiniProgramPage);
