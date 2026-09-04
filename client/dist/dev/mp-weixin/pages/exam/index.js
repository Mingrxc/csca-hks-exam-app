"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const stores_user = require("../../stores/user.js");
if (!Array) {
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_t_icon2 = common_vendor.resolveComponent("t-icon");
  (_easycom_t_tag2 + _easycom_t_icon2)();
}
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_t_icon = () => "../../node-modules/@tdesign/uniapp/dist/icon/icon.js";
if (!Math) {
  (_easycom_t_tag + _easycom_t_icon)();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const userStore = stores_user.useUserStore();
    const dashboard = common_vendor.reactive({
      todayStats: { questionCount: 0, correctRate: 0, wrongCount: 0 },
      pendingWrongCount: 0,
      favoriteCount: 0
    });
    const strategyCards = common_vendor.computed(
      () => [
        {
          key: "random",
          icon: "star",
          iconColor: "#c77f5e",
          title: "随机组卷"
        },
        {
          key: "real",
          icon: "calendar",
          iconColor: "#c77f5e",
          title: "模拟考试"
        },
        {
          key: "knowledge",
          icon: "book",
          iconColor: "#c77f5e",
          title: "专项训练"
        },
        {
          key: "progressive",
          icon: "arrow-right",
          iconColor: "#c77f5e",
          title: "难度递进"
        }
      ]
    );
    const selectedExamLabels = common_vendor.computed(
      () => userStore.selectedExams.map((exam) => ({
        value: exam,
        label: exam,
        theme: exam === "CSCA" ? "primary" : "warning"
      }))
    );
    const defaultExamType = common_vendor.computed(() => userStore.primaryExam);
    const loadDashboard = async () => {
      try {
        const data = api_contracts.toDashboardData(await api_index.userApi.getDashboard());
        dashboard.todayStats = data.todayStats;
        dashboard.pendingWrongCount = data.pendingWrongCount;
        dashboard.favoriteCount = data.favoriteCount;
      } catch {
      }
    };
    const goPaper = (strategy) => {
      common_vendor.index.navigateTo({ url: `/pages/exam/paper?strategy=${strategy}&examType=${defaultExamType.value}` });
    };
    const goHistory = () => common_vendor.index.navigateTo({ url: "/pages/exam/history" });
    const goWrongBook = () => common_vendor.index.navigateTo({ url: "/pages/wrongbook/index" });
    const goFavorite = () => common_vendor.index.navigateTo({ url: "/pages/favorite/index" });
    const goRedo = () => common_vendor.index.navigateTo({ url: `/pages/wrongbook/redo?examType=${defaultExamType.value}` });
    common_vendor.onShow(() => {
      if (!userStore.isLogin)
        userStore.login().catch(() => {
        });
      loadDashboard();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: selectedExamLabels.value.length
      }, selectedExamLabels.value.length ? {
        b: common_vendor.f(selectedExamLabels.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.label),
            b: item.value,
            c: "b6604ac4-0-" + i0,
            d: common_vendor.p({
              theme: item.theme,
              variant: "light",
              shape: "round",
              size: "small"
            })
          };
        })
      } : {}, {
        c: common_vendor.t(dashboard.todayStats.questionCount),
        d: common_vendor.t(dashboard.todayStats.correctRate),
        e: common_vendor.t(dashboard.pendingWrongCount),
        f: common_vendor.t(dashboard.favoriteCount),
        g: common_vendor.f(strategyCards.value, (item, k0, i0) => {
          return {
            a: "b6604ac4-1-" + i0,
            b: common_vendor.p({
              name: item.icon,
              color: item.iconColor,
              size: "28rpx"
            }),
            c: common_vendor.t(item.title),
            d: item.key,
            e: common_vendor.o(($event) => goPaper(item.key), item.key)
          };
        }),
        h: common_vendor.p({
          name: "file-paste-filled",
          size: "28rpx",
          color: "#c77f5e"
        }),
        i: common_vendor.o(goHistory, "3b"),
        j: common_vendor.p({
          name: "book",
          size: "28rpx",
          color: "#c77f5e"
        }),
        k: common_vendor.o(goWrongBook, "50"),
        l: common_vendor.p({
          name: "star",
          size: "28rpx",
          color: "#c77f5e"
        }),
        m: common_vendor.o(goFavorite, "10"),
        n: common_vendor.p({
          name: "refresh",
          size: "28rpx",
          color: "#c77f5e"
        }),
        o: common_vendor.o(goRedo, "6e")
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b6604ac4"]]);
wx.createPage(MiniProgramPage);
