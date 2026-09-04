"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const constants_exam = require("../../constants/exam.js");
const stores_exam = require("../../stores/exam.js");
if (!Array) {
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  _easycom_t_button2();
}
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
if (!Math) {
  _easycom_t_button();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "paper",
  setup(__props) {
    const examStore = stores_exam.useExamStore();
    const strategyType = common_vendor.ref("random");
    const isGenerating = common_vendor.ref(false);
    const initialSpecial = common_vendor.ref("");
    const specialFetched = common_vendor.reactive({
      CSCA: false,
      HKS: false
    });
    const specialOptionsByExam = common_vendor.reactive({
      CSCA: [...constants_exam.CSCA_SUBJECT_OPTIONS],
      HKS: [...constants_exam.HSK_KNOWLEDGE_OPTIONS]
    });
    const currentStrategy = common_vendor.computed(
      () => constants_exam.PAPER_STRATEGY_MAP[strategyType.value] || constants_exam.PAPER_STRATEGY_MAP.random
    );
    const difficulties = constants_exam.DIFFICULTY_OPTIONS;
    const questionCountOptions = constants_exam.QUESTION_COUNT_OPTIONS;
    const timeLimitOptions = constants_exam.TIME_LIMIT_OPTIONS;
    const form = common_vendor.reactive({
      examType: "CSCA",
      questionCount: 20,
      difficulty: "all",
      specialValues: [],
      mode: "practice",
      timeLimit: 60
    });
    const specialLabel = common_vendor.computed(() => constants_exam.getSpecialLabel(form.examType));
    const specialOptions = common_vendor.computed(() => specialOptionsByExam[form.examType] || []);
    const selectedSpecials = common_vendor.computed(() => form.specialValues);
    const summaryText = common_vendor.computed(() => {
      var _a;
      const special = selectedSpecials.value.length ? `${selectedSpecials.value.join(" / ")}` : "分类不限";
      const modeText = form.mode === "exam" ? `考试 ${form.timeLimit} 分钟` : "练习模式";
      const difficultyText = form.difficulty === "all" ? "全部难度" : ((_a = difficulties.find((item) => item.value === form.difficulty)) == null ? void 0 : _a.label) || form.difficulty;
      return `${form.questionCount}题 · ${difficultyText} · ${special} · ${modeText}`;
    });
    const loadSpecialOptions = async (examType) => {
      if (specialFetched[examType])
        return;
      try {
        const options = await api_index.questionApi.getSpecialOptions(examType);
        specialOptionsByExam[examType] = options.map((item) => item.label || item.value).filter(Boolean);
      } catch {
        specialOptionsByExam[examType] = examType === "CSCA" ? [...constants_exam.CSCA_SUBJECT_OPTIONS] : [...constants_exam.HSK_KNOWLEDGE_OPTIONS];
      } finally {
        specialFetched[examType] = true;
      }
    };
    const toggleSpecial = (value) => {
      if (form.examType === "CSCA") {
        form.specialValues = selectedSpecials.value[0] === value ? [] : [value];
        return;
      }
      const index = form.specialValues.indexOf(value);
      if (index >= 0) {
        form.specialValues.splice(index, 1);
      } else {
        form.specialValues.push(value);
      }
    };
    const setExamType = async (value) => {
      if (form.examType === value)
        return;
      form.examType = value;
      form.specialValues = [];
      await loadSpecialOptions(value);
    };
    common_vendor.onLoad((query) => {
      const strategy = query == null ? void 0 : query.strategy;
      if (typeof strategy === "string" && strategy in constants_exam.PAPER_STRATEGY_MAP) {
        strategyType.value = strategy;
      }
      const examType = query == null ? void 0 : query.examType;
      if (examType === "CSCA" || examType === "HKS") {
        form.examType = examType;
      }
      const special = (query == null ? void 0 : query.special) || (query == null ? void 0 : query.knowledge) || (query == null ? void 0 : query.subject);
      initialSpecial.value = typeof special === "string" ? special : "";
      void Promise.all([loadSpecialOptions("CSCA"), loadSpecialOptions("HKS")]).then(() => {
        if (initialSpecial.value && specialOptions.value.includes(initialSpecial.value)) {
          form.specialValues = [initialSpecial.value];
        }
      });
    });
    const startExam = async () => {
      if (strategyType.value === "knowledge" && form.specialValues.length === 0) {
        common_vendor.index.showToast({ title: `请至少选择一个${specialLabel.value}`, icon: "none" });
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
          knowledgePoints: form.specialValues,
          mode: form.mode,
          timeLimit: form.mode === "exam" ? form.timeLimit : 0
        });
        examStore.setConfig({
          examType: form.examType,
          questionCount: form.questionCount,
          difficulty: form.difficulty,
          strategy: strategyType.value,
          knowledgePoints: form.specialValues,
          mode: form.mode,
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
        a: common_vendor.t(currentStrategy.value.title),
        b: common_vendor.t(currentStrategy.value.desc),
        c: common_vendor.t(form.examType),
        d: common_vendor.t(form.questionCount),
        e: common_vendor.t(form.mode === "exam" ? form.timeLimit : "练习"),
        f: common_vendor.t(form.mode === "exam" ? "限时分钟" : "练习模式"),
        g: form.examType === "CSCA" ? 1 : "",
        h: common_vendor.o(($event) => setExamType("CSCA"), "ab"),
        i: form.examType === "HKS" ? 1 : "",
        j: common_vendor.o(($event) => setExamType("HKS"), "15"),
        k: common_vendor.f(common_vendor.unref(questionCountOptions), (item, k0, i0) => {
          return {
            a: common_vendor.t(item),
            b: form.questionCount === item ? 1 : "",
            c: item,
            d: common_vendor.o(($event) => form.questionCount = item, item)
          };
        }),
        l: common_vendor.f(common_vendor.unref(difficulties), (item, k0, i0) => {
          return {
            a: common_vendor.t(item.label),
            b: form.difficulty === item.value ? 1 : "",
            c: item.value,
            d: common_vendor.o(($event) => form.difficulty = item.value, item.value)
          };
        }),
        m: strategyType.value === "knowledge"
      }, strategyType.value === "knowledge" ? {
        n: common_vendor.t(specialLabel.value),
        o: common_vendor.f(specialOptions.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item),
            b: selectedSpecials.value.includes(item) ? 1 : "",
            c: item,
            d: common_vendor.o(($event) => toggleSpecial(item), item)
          };
        })
      } : {}, {
        p: form.mode === "exam" ? 1 : "",
        q: common_vendor.o(($event) => form.mode = "exam", "07"),
        r: form.mode === "practice" ? 1 : "",
        s: common_vendor.o(($event) => form.mode = "practice", "04"),
        t: form.mode === "exam"
      }, form.mode === "exam" ? {
        v: common_vendor.f(common_vendor.unref(timeLimitOptions), (item, k0, i0) => {
          return {
            a: common_vendor.t(item),
            b: form.timeLimit === item ? 1 : "",
            c: item,
            d: common_vendor.o(($event) => form.timeLimit = item, item)
          };
        })
      } : {}, {
        w: common_vendor.t(form.examType),
        x: common_vendor.t(summaryText.value),
        y: common_vendor.o(startExam, "0e"),
        z: common_vendor.p({
          theme: "primary",
          block: true,
          size: "large",
          shape: "round",
          loading: isGenerating.value
        })
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-ecefe579"]]);
wx.createPage(MiniProgramPage);
