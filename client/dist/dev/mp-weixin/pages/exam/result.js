"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const stores_exam = require("../../stores/exam.js");
if (!Array) {
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_c_ring_chart2 = common_vendor.resolveComponent("c-ring-chart");
  const _easycom_t_empty2 = common_vendor.resolveComponent("t-empty");
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  (_easycom_t_tag2 + _easycom_c_ring_chart2 + _easycom_t_empty2 + _easycom_t_button2)();
}
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_c_ring_chart = () => "../../components/RingChart/index.js";
const _easycom_t_empty = () => "../../node-modules/@tdesign/uniapp/dist/empty/empty.js";
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
if (!Math) {
  (_easycom_t_tag + _easycom_c_ring_chart + _easycom_t_empty + _easycom_t_button)();
}
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
    const isLoading = common_vendor.ref(false);
    const showReview = common_vendor.ref(false);
    const paperExamType = common_vendor.ref(examStore.config.examType);
    const paperQuestions = common_vendor.ref([]);
    const questionResultMap = common_vendor.ref({});
    const passed = common_vendor.computed(() => result.value.correctRate >= 60);
    const wrongQuestions = common_vendor.ref([]);
    const reviewQuestions = common_vendor.ref([]);
    const analysisTitle = common_vendor.computed(() => paperExamType.value === "CSCA" ? "科目分析" : "知识点分析");
    const analysisSubtitle = common_vendor.computed(
      () => paperExamType.value === "CSCA" ? "CSCA 按科目回看表现，方便定位哪一门最需要补。" : "HSK 按知识点回看表现，便于找到该补的细分项。"
    );
    const analysisEmptyText = common_vendor.computed(
      () => paperExamType.value === "CSCA" ? "暂无科目统计" : "暂无知识点统计"
    );
    const analysisItems = common_vendor.computed(() => {
      const map = /* @__PURE__ */ new Map();
      const questions = paperQuestions.value;
      questions.forEach((question) => {
        const name = paperExamType.value === "CSCA" ? question.subject : question.knowledge_point;
        if (!name)
          return;
        const bucket = map.get(name) || { total: 0, correct: 0 };
        bucket.total += 1;
        bucket.correct += questionResultMap.value[question.id] ? 1 : 0;
        map.set(name, bucket);
      });
      return Array.from(map.entries()).map(([name, value]) => ({
        name,
        total: value.total,
        correct: value.correct,
        correctRate: value.total ? Math.round(value.correct / value.total * 100) : 0
      }));
    });
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
        reviewQuestions.value = api_contracts.toResultReviewQuestions(payload);
        paperQuestions.value = payload.paper.questions;
        paperExamType.value = payload.paper.exam_type;
        questionResultMap.value = Object.fromEntries(
          payload.review_questions.map((question) => [question.id, question.is_correct])
        );
      } catch {
      } finally {
        isLoading.value = false;
      }
    };
    common_vendor.onLoad((query) => {
      const paperId = Number((query == null ? void 0 : query.paperId) || (query == null ? void 0 : query.id) || examStore.paperId);
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
    const reviewAll = async () => {
      showReview.value = !showReview.value;
      if (showReview.value) {
        await common_vendor.nextTick$1();
        common_vendor.index.pageScrollTo({ selector: "#all-review", duration: 250 });
      }
    };
    const goHome = () => common_vendor.index.switchTab({ url: "/pages/index/index" });
    const retryWrong = () => {
      common_vendor.index.navigateTo({ url: `/pages/wrongbook/redo?examType=${paperExamType.value}` });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(passed.value ? "通过" : "继续加油"),
        b: common_vendor.p({
          theme: passed.value ? "success" : "warning",
          variant: "light",
          shape: "round"
        }),
        c: common_vendor.t(passed.value ? "恭喜通过！" : "这次已经比上次更接近了"),
        d: common_vendor.p({
          percent: result.value.correctRate,
          size: 180,
          ["line-width"]: 14,
          label: "正确率"
        }),
        e: common_vendor.t(result.value.correctCount),
        f: common_vendor.t(result.value.totalCount),
        g: common_vendor.t(result.value.correctRate),
        h: common_vendor.t(result.value.timeUsed),
        i: common_vendor.n(passed.value ? "passed" : "failed"),
        j: common_vendor.t(analysisTitle.value),
        k: common_vendor.t(analysisSubtitle.value),
        l: common_vendor.t(paperExamType.value),
        m: common_vendor.p({
          theme: "primary",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        n: analysisItems.value.length
      }, analysisItems.value.length ? {
        o: common_vendor.f(analysisItems.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.name),
            b: common_vendor.t(item.correctRate),
            c: item.correctRate + "%",
            d: common_vendor.t(item.correct),
            e: common_vendor.t(item.total),
            f: item.name
          };
        })
      } : {
        p: common_vendor.p({
          description: analysisEmptyText.value
        })
      }, {
        q: timeUsagePercent.value + "%",
        r: common_vendor.t(result.value.timeUsed),
        s: wrongQuestions.value.length > 0
      }, wrongQuestions.value.length > 0 ? {
        t: common_vendor.t(wrongQuestions.value.length),
        v: common_vendor.f(wrongQuestions.value, (q, k0, i0) => {
          return {
            a: common_vendor.t(q.stem),
            b: common_vendor.t(q.typeLabel),
            c: "419be219-4-" + i0,
            d: common_vendor.t(q.yourAnswer),
            e: common_vendor.t(q.correctAnswer),
            f: q.id,
            g: common_vendor.o(($event) => goDetail(q.id), q.id)
          };
        }),
        w: common_vendor.p({
          theme: "default",
          variant: "light",
          shape: "round",
          size: "small"
        })
      } : {}, {
        x: showReview.value
      }, showReview.value ? {
        y: common_vendor.t(reviewQuestions.value.length),
        z: common_vendor.f(reviewQuestions.value, (question, index, i0) => {
          return common_vendor.e({
            a: common_vendor.t(index + 1),
            b: common_vendor.t(question.typeLabel),
            c: common_vendor.t(question.correct ? "正确" : "错误"),
            d: "419be219-5-" + i0,
            e: common_vendor.p({
              theme: question.correct ? "success" : "danger",
              variant: "light",
              shape: "round",
              size: "small"
            }),
            f: common_vendor.t(question.stem),
            g: question.options.length
          }, question.options.length ? {
            h: common_vendor.f(question.options, (option, k1, i1) => {
              return {
                a: common_vendor.t(option.key),
                b: common_vendor.t(option.text),
                c: option.key
              };
            })
          } : {}, {
            i: common_vendor.t(question.userAnswer || "未作答"),
            j: common_vendor.t(question.correctAnswer),
            k: common_vendor.t(question.analysis),
            l: question.id
          });
        })
      } : {}, {
        A: common_vendor.t(showReview.value ? "收起全部解析" : "查看全部解析"),
        B: common_vendor.o(reviewAll, "ea"),
        C: common_vendor.p({
          theme: "default",
          variant: "outline",
          block: true,
          shape: "round"
        }),
        D: common_vendor.o(goHome, "15"),
        E: common_vendor.p({
          theme: "primary",
          block: true,
          shape: "round"
        }),
        F: common_vendor.o(retryWrong, "ad"),
        G: common_vendor.p({
          theme: "default",
          variant: "outline",
          block: true,
          shape: "round"
        })
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-419be219"]]);
wx.createPage(MiniProgramPage);
