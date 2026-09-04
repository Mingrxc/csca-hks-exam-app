"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const stores_user = require("../../stores/user.js");
if (!Array) {
  const _easycom_t_icon2 = common_vendor.resolveComponent("t-icon");
  const _easycom_t_empty2 = common_vendor.resolveComponent("t-empty");
  (_easycom_t_icon2 + _easycom_t_empty2)();
}
const _easycom_t_icon = () => "../../node-modules/@tdesign/uniapp/dist/icon/icon.js";
const _easycom_t_empty = () => "../../node-modules/@tdesign/uniapp/dist/empty/empty.js";
if (!Math) {
  (_easycom_t_icon + _easycom_t_empty)();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const userStore = stores_user.useUserStore();
    const recentPapers = common_vendor.ref([]);
    const contents = common_vendor.ref([]);
    const clubAds = [
      { title: "本周活动招募", desc: "报名入口和时间放在这里。" },
      { title: "学习资料合作位", desc: "适合放推荐和活动宣传。" }
    ];
    const loadRecentPapers = async () => {
      if (!userStore.isLogin) {
        recentPapers.value = [];
        return;
      }
      try {
        const data = api_contracts.toDashboardData(await api_index.userApi.getDashboard());
        recentPapers.value = data.recentPapers;
      } catch {
      }
    };
    const loadContents = async () => {
      try {
        contents.value = (await api_index.contentApi.listHome()).slice(0, 5);
      } catch {
      }
    };
    const goPaper = (id) => {
      common_vendor.index.navigateTo({ url: `/pages/exam/result?id=${id}` });
    };
    const openContent = (item) => {
      if (item.link_url) {
        common_vendor.index.navigateTo({ url: item.link_url });
        return;
      }
      common_vendor.index.showModal({ title: item.title, content: item.body, showCancel: false });
    };
    common_vendor.onShow(() => {
      loadRecentPapers();
      loadContents();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: contents.value.length
      }, contents.value.length ? {
        b: common_vendor.f(contents.value, (item, k0, i0) => {
          var _a;
          return {
            a: common_vendor.t(((_a = item.created_at) == null ? void 0 : _a.slice(0, 10)) || ""),
            b: common_vendor.t(item.title),
            c: common_vendor.t(item.summary),
            d: "83a5a03c-0-" + i0,
            e: item.id,
            f: common_vendor.o(($event) => openContent(item), item.id)
          };
        }),
        c: common_vendor.p({
          name: "chevron-right",
          size: "28rpx",
          color: "#9d8f84"
        })
      } : {
        d: common_vendor.p({
          description: "暂无资讯内容"
        })
      }, {
        e: common_vendor.f(clubAds, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.title),
            b: common_vendor.t(item.desc),
            c: "83a5a03c-2-" + i0,
            d: item.title
          };
        }),
        f: common_vendor.p({
          name: "arrow-right",
          size: "26rpx",
          color: "#c77f5e"
        }),
        g: recentPapers.value.length
      }, recentPapers.value.length ? {
        h: common_vendor.f(recentPapers.value, (paper, k0, i0) => {
          return {
            a: common_vendor.t(paper.title),
            b: common_vendor.t(paper.questionCount),
            c: common_vendor.t(paper.score),
            d: common_vendor.t(paper.date),
            e: "83a5a03c-3-" + i0,
            f: paper.id,
            g: common_vendor.o(($event) => goPaper(paper.id), paper.id)
          };
        }),
        i: common_vendor.p({
          name: "chevron-right",
          size: "26rpx",
          color: "#9d8f84"
        })
      } : {
        j: common_vendor.p({
          description: "还没有学习记录"
        })
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-83a5a03c"]]);
wx.createPage(MiniProgramPage);
