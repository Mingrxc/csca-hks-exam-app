"use strict";
const common_vendor = require("../../common/vendor.js");
const mock_user = require("../../mock/user.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const userInfo = common_vendor.ref(mock_user.mockUserProfile);
    const reminderOn = common_vendor.ref(true);
    const toggleReminder = (e) => {
      reminderOn.value = e.detail.value;
      common_vendor.index.showToast({ title: reminderOn.value ? "已开启提醒" : "已关闭提醒", icon: "none" });
    };
    const goPage = (url) => {
      if (url.startsWith("/pages/exam") || url.startsWith("/pages/wrongbook")) {
        common_vendor.index.navigateTo({ url });
      } else {
        common_vendor.index.switchTab({ url });
      }
    };
    const handleLogout = () => {
      common_vendor.index.showModal({
        title: "确认退出",
        content: "退出后需要重新登录，确定退出吗？",
        success: (res) => {
          if (res.confirm) {
            common_vendor.index.removeStorageSync("token");
            common_vendor.index.showToast({ title: "已退出登录", icon: "success" });
          }
        }
      });
    };
    return (_ctx, _cache) => {
      return {
        a: common_vendor.t(userInfo.value.nickname),
        b: common_vendor.t(userInfo.value.targetExam),
        c: common_vendor.t(userInfo.value.totalQuestions),
        d: common_vendor.t(userInfo.value.correctRate),
        e: common_vendor.t(userInfo.value.streakDays),
        f: common_vendor.o(($event) => goPage("/pages/exam/index"), "8b"),
        g: common_vendor.o(($event) => goPage("/pages/wrongbook/index"), "aa"),
        h: common_vendor.o(($event) => goPage("/pages/wrongbook/redo"), "e7"),
        i: reminderOn.value,
        j: common_vendor.o(toggleReminder, "82"),
        k: common_vendor.t(userInfo.value.targetExam),
        l: common_vendor.o(handleLogout, "d6")
      };
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-f97f9319"]]);
wx.createPage(MiniProgramPage);
