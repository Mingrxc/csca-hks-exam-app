"use strict";
const common_vendor = require("../../common/vendor.js");
const constants_exam = require("../../constants/exam.js");
const mock_exam = require("../../mock/exam.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const strategies = common_vendor.ref(constants_exam.PAPER_STRATEGIES);
    const historyPapers = common_vendor.ref(mock_exam.mockHistoryPapers);
    const goPaper = (strategy) => {
      common_vendor.index.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}` });
    };
    const goResult = (id) => {
      common_vendor.index.navigateTo({ url: `/pages/exam/result?id=${id}` });
    };
    const viewAll = () => {
      console.log("查看全部历史试卷");
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.f(strategies.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.icon),
            b: common_vendor.t(item.title),
            c: common_vendor.t(item.desc),
            d: item.key,
            e: common_vendor.o(($event) => goPaper(item.key), item.key)
          };
        }),
        b: common_vendor.o(viewAll, "be"),
        c: common_vendor.f(historyPapers.value, (paper, k0, i0) => {
          return {
            a: common_vendor.t(paper.title),
            b: common_vendor.t(paper.passed ? "通过" : "未通过"),
            c: common_vendor.n(paper.passed ? "pass" : "fail"),
            d: common_vendor.t(paper.correctRate),
            e: common_vendor.t(paper.timeUsed),
            f: common_vendor.t(paper.date),
            g: paper.id,
            h: common_vendor.o(($event) => goResult(paper.id), paper.id)
          };
        }),
        d: historyPapers.value.length === 0
      }, historyPapers.value.length === 0 ? {} : {});
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b6604ac4"]]);
wx.createPage(MiniProgramPage);
