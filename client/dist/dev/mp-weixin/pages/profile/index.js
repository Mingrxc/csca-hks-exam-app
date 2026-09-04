"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const stores_user = require("../../stores/user.js");
if (!Array) {
  const _easycom_t_avatar2 = common_vendor.resolveComponent("t-avatar");
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  const _easycom_c_ring_chart2 = common_vendor.resolveComponent("c-ring-chart");
  const _easycom_t_icon2 = common_vendor.resolveComponent("t-icon");
  (_easycom_t_avatar2 + _easycom_t_tag2 + _easycom_t_button2 + _easycom_c_ring_chart2 + _easycom_t_icon2)();
}
const _easycom_t_avatar = () => "../../node-modules/@tdesign/uniapp/dist/avatar/avatar.js";
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
const _easycom_c_ring_chart = () => "../../components/RingChart/index.js";
const _easycom_t_icon = () => "../../node-modules/@tdesign/uniapp/dist/icon/icon.js";
if (!Math) {
  (_easycom_t_avatar + _easycom_t_tag + _easycom_t_button + _easycom_c_ring_chart + _easycom_t_icon)();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const userStore = stores_user.useUserStore();
    const userInfo = common_vendor.ref({
      nickname: "留学同学",
      avatarUrl: "",
      targetExam: "CSCA",
      targetDate: "",
      totalQuestions: 0,
      correctRate: 0,
      streakDays: 0,
      favoriteCount: 0
    });
    const dashboard = common_vendor.reactive({
      userName: "留学同学",
      targetExam: "CSCA",
      targetDate: "",
      countdown: { days: "0", hours: "00", minutes: "00" },
      todayStats: { questionCount: 0, correctRate: 0, wrongCount: 0 },
      pendingWrongCount: 0,
      favoriteCount: 0,
      recentPapers: []
    });
    const loadError = common_vendor.ref(false);
    const targetDraftExams = common_vendor.ref([]);
    const targetDraftDate = common_vendor.ref("");
    const savingTarget = common_vendor.ref(false);
    const now = /* @__PURE__ */ new Date();
    const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
    const selectedExamLabels = common_vendor.computed(
      () => targetDraftExams.value.map((exam) => ({
        value: exam,
        label: exam,
        theme: exam === "CSCA" ? "primary" : "warning"
      }))
    );
    const loadProfile = async () => {
      loadError.value = false;
      try {
        userInfo.value = api_contracts.toUserProfile(await api_index.userApi.getUserInfo());
        targetDraftDate.value = userInfo.value.targetDate;
        targetDraftExams.value = [...userStore.selectedExams];
      } catch {
        loadError.value = true;
      }
    };
    const loadDashboard = async () => {
      try {
        Object.assign(dashboard, api_contracts.toDashboardData(await api_index.userApi.getDashboard()));
      } catch {
      }
    };
    const loadAll = async () => {
      await Promise.all([loadProfile(), loadDashboard()]);
    };
    const selectTargetDate = (event) => {
      targetDraftDate.value = event.detail.value;
    };
    const toggleDraftExam = (exam) => {
      const index = targetDraftExams.value.indexOf(exam);
      if (index >= 0) {
        targetDraftExams.value.splice(index, 1);
      } else if (targetDraftExams.value.length < 2) {
        targetDraftExams.value.push(exam);
      }
      if (targetDraftExams.value.length === 0) {
        userStore.setBrowseMode();
      } else {
        userStore.setSelectedExams(targetDraftExams.value);
      }
    };
    const setBrowseMode = () => {
      targetDraftExams.value = [];
      userStore.setBrowseMode();
    };
    const saveTarget = async () => {
      if (!targetDraftDate.value && targetDraftExams.value.length > 0) {
        common_vendor.index.showToast({ title: "请选择考试日期", icon: "none" });
        return;
      }
      savingTarget.value = true;
      try {
        const primaryExam = targetDraftExams.value[0] || userInfo.value.targetExam;
        const payload = {
          target_exam: primaryExam
        };
        if (targetDraftDate.value)
          payload.target_date = targetDraftDate.value;
        const updated = await api_index.userApi.updateProfile(payload);
        userInfo.value = api_contracts.toUserProfile(updated);
        dashboard.targetExam = updated.target_exam;
        dashboard.targetDate = updated.target_date || "";
        common_vendor.index.showToast({ title: "目标已更新", icon: "success" });
      } catch {
      } finally {
        savingTarget.value = false;
      }
    };
    const chooseAvatar = async (event) => {
      var _a;
      const avatarUrl = (_a = event.detail) == null ? void 0 : _a.avatarUrl;
      if (!avatarUrl)
        return;
      try {
        const updated = await api_index.userApi.updateProfile({ avatar_url: avatarUrl });
        userInfo.value = api_contracts.toUserProfile(updated);
        common_vendor.index.showToast({ title: "头像已更新", icon: "success" });
      } catch {
      }
    };
    const editNickname = () => {
      common_vendor.index.showModal({
        title: "修改昵称",
        editable: true,
        placeholderText: "输入昵称",
        content: userInfo.value.nickname,
        success: async (result) => {
          const nickname = String(result.content || "").trim();
          if (!result.confirm || !nickname || nickname === userInfo.value.nickname)
            return;
          try {
            const updated = await api_index.userApi.updateProfile({ nickname });
            userInfo.value = api_contracts.toUserProfile(updated);
          } catch {
          }
        }
      });
    };
    const showAbout = () => {
      common_vendor.index.showModal({
        title: "关于",
        content: "老外1点通",
        showCancel: false
      });
    };
    const goPage = (url) => {
      if (url === "/pages/exam/index") {
        common_vendor.index.switchTab({ url });
      } else {
        common_vendor.index.navigateTo({ url });
      }
    };
    const goRedo = () => {
      const examType = targetDraftExams.value[0] || userInfo.value.targetExam;
      common_vendor.index.navigateTo({ url: `/pages/wrongbook/redo?examType=${examType}` });
    };
    const handleLogout = () => {
      common_vendor.index.showModal({
        title: "确认退出",
        content: "退出后需要重新登录，确定退出吗？",
        success: (res) => {
          if (res.confirm) {
            userStore.logout();
            userInfo.value = {
              nickname: "留学同学",
              avatarUrl: "",
              targetExam: "CSCA",
              targetDate: "",
              totalQuestions: 0,
              correctRate: 0,
              streakDays: 0,
              favoriteCount: 0
            };
            targetDraftExams.value = [];
            loadError.value = false;
            common_vendor.index.showToast({ title: "已退出登录", icon: "success" });
          }
        }
      });
    };
    common_vendor.onShow(async () => {
      await loadAll();
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: userInfo.value.avatarUrl
      }, userInfo.value.avatarUrl ? {
        b: common_vendor.p({
          image: userInfo.value.avatarUrl,
          size: "112rpx",
          shape: "circle"
        })
      } : {
        c: common_vendor.t(userInfo.value.nickname.slice(0, 1))
      }, {
        d: common_vendor.t(userInfo.value.nickname),
        e: common_vendor.f(selectedExamLabels.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.label),
            b: item.value,
            c: "f97f9319-1-" + i0,
            d: common_vendor.p({
              theme: item.theme,
              variant: "light",
              shape: "round",
              size: "small"
            })
          };
        }),
        f: !selectedExamLabels.value.length
      }, !selectedExamLabels.value.length ? {
        g: common_vendor.p({
          theme: "default",
          variant: "light",
          shape: "round",
          size: "small"
        })
      } : {}, {
        h: userInfo.value.targetDate
      }, userInfo.value.targetDate ? {
        i: common_vendor.t(userInfo.value.targetDate),
        j: common_vendor.p({
          theme: "warning",
          variant: "light",
          shape: "round",
          size: "small"
        })
      } : {}, {
        k: common_vendor.o(chooseAvatar, "ea"),
        l: common_vendor.p({
          theme: "primary",
          variant: "outline",
          size: "small",
          shape: "round",
          ["open-type"]: "chooseAvatar"
        }),
        m: common_vendor.o(editNickname, "4d"),
        n: common_vendor.p({
          theme: "default",
          variant: "outline",
          size: "small",
          shape: "round"
        }),
        o: loadError.value
      }, loadError.value ? {
        p: common_vendor.o(loadProfile, "0d")
      } : {}, {
        q: common_vendor.t(userInfo.value.totalQuestions),
        r: common_vendor.t(userInfo.value.correctRate),
        s: common_vendor.t(userInfo.value.streakDays),
        t: common_vendor.t(_ctx.pendingWrongCount),
        v: common_vendor.p({
          percent: userInfo.value.correctRate,
          size: 170,
          ["line-width"]: 14,
          label: "正确率"
        }),
        w: common_vendor.t(dashboard.todayStats.questionCount),
        x: common_vendor.t(dashboard.todayStats.correctRate),
        y: common_vendor.t(dashboard.pendingWrongCount),
        z: targetDraftExams.value.length === 0 ? 1 : "",
        A: common_vendor.o(setBrowseMode, "c9"),
        B: targetDraftExams.value.includes("CSCA") ? 1 : "",
        C: common_vendor.o(($event) => toggleDraftExam("CSCA"), "ba"),
        D: targetDraftExams.value.includes("HKS") ? 1 : "",
        E: common_vendor.o(($event) => toggleDraftExam("HKS"), "b8"),
        F: common_vendor.t(targetDraftDate.value || "选择考试日期"),
        G: targetDraftDate.value,
        H: today,
        I: common_vendor.o(selectTargetDate, "0b"),
        J: common_vendor.o(saveTarget, "4a"),
        K: common_vendor.p({
          theme: "primary",
          block: true,
          shape: "round",
          loading: savingTarget.value
        }),
        L: common_vendor.p({
          name: "book",
          size: "28rpx"
        }),
        M: common_vendor.o(($event) => goPage("/pages/exam/index"), "68"),
        N: common_vendor.p({
          name: "star",
          size: "28rpx"
        }),
        O: common_vendor.o(($event) => goPage("/pages/favorite/index"), "b8"),
        P: common_vendor.p({
          name: "edit",
          size: "28rpx"
        }),
        Q: common_vendor.o(($event) => goPage("/pages/wrongbook/index"), "8a"),
        R: common_vendor.p({
          name: "refresh",
          size: "28rpx"
        }),
        S: common_vendor.o(goRedo, "88"),
        T: common_vendor.p({
          name: "info-circle",
          size: "28rpx"
        }),
        U: common_vendor.o(showAbout, "dd"),
        V: common_vendor.p({
          name: "poweroff",
          size: "28rpx"
        }),
        W: common_vendor.o(handleLogout, "05")
      });
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-f97f9319"]]);
wx.createPage(MiniProgramPage);
