"use strict";
const common_vendor = require("../../common/vendor.js");
const constants_exam = require("../../constants/exam.js");
const mock_dashboard = require("../../mock/dashboard.js");
const utils_index = require("../../utils/index.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const strategies = constants_exam.PAPER_STRATEGIES;
    const userName = common_vendor.ref(mock_dashboard.mockDashboard.userName);
    const targetExam = common_vendor.ref(mock_dashboard.mockDashboard.targetExam);
    const greetingText = common_vendor.computed(() => utils_index.getGreeting());
    const countdown = common_vendor.ref(mock_dashboard.mockDashboard.countdown);
    const todayStats = common_vendor.ref(mock_dashboard.mockDashboard.todayStats);
    const pendingWrongCount = common_vendor.ref(mock_dashboard.mockDashboard.pendingWrongCount);
    const recentPapers = common_vendor.ref(mock_dashboard.mockDashboard.recentPapers);
    const goExam = (strategy) => {
      common_vendor.index.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}` });
    };
    const goWrongBook = () => {
      common_vendor.index.switchTab({ url: "/pages/wrongbook/index" });
    };
    const goPaper = (id) => {
      common_vendor.index.navigateTo({ url: `/pages/exam/result?id=${id}` });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(greetingText.value),
        b: common_vendor.t(userName.value),
        c: targetExam.value
      }, targetExam.value ? {
        d: common_vendor.t(targetExam.value),
        e: common_vendor.t(countdown.value.days),
        f: common_vendor.t(countdown.value.hours),
        g: common_vendor.t(countdown.value.minutes)
      } : {}, {
        h: common_vendor.t(todayStats.value.questionCount),
        i: common_vendor.t(todayStats.value.correctRate),
        j: common_vendor.t(todayStats.value.wrongCount),
        k: common_vendor.f(common_vendor.unref(strategies), (item, index, i0) => {
          return {
            a: common_vendor.t(item.icon),
            b: common_vendor.t(item.title),
            c: common_vendor.t(item.shortDesc),
            d: index === 0 ? 1 : "",
            e: item.key,
            f: common_vendor.o(($event) => goExam(item.key), item.key)
          };
        }),
        l: pendingWrongCount.value > 0
      }, pendingWrongCount.value > 0 ? {
        m: common_vendor.t(pendingWrongCount.value),
        n: common_vendor.o(goWrongBook, "80")
      } : {}, {
        o: recentPapers.value.length > 0
      }, recentPapers.value.length > 0 ? {
        p: common_vendor.f(recentPapers.value, (paper, k0, i0) => {
          return {
            a: common_vendor.t(paper.title),
            b: common_vendor.t(paper.questionCount),
            c: common_vendor.t(paper.score),
            d: common_vendor.t(paper.date),
            e: paper.id,
            f: common_vendor.o(($event) => goPaper(paper.id), paper.id)
          };
        })
      } : {});
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-83a5a03c"]]);
wx.createPage(MiniProgramPage);
