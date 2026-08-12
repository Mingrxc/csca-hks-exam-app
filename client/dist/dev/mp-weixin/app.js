"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const common_vendor = require("./common/vendor.js");
if (!Math) {
  "./pages/index/index.js";
  "./pages/exam/index.js";
  "./pages/exam/paper.js";
  "./pages/exam/answer.js";
  "./pages/exam/result.js";
  "./pages/wrongbook/index.js";
  "./pages/wrongbook/detail.js";
  "./pages/wrongbook/redo.js";
  "./pages/profile/index.js";
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "App",
  setup(__props) {
    common_vendor.onLaunch(() => {
      console.log("留学考霸 App Launch");
      const token = common_vendor.index.getStorageSync("token");
      if (!token) {
        console.log("未登录，后续将跳转登录页");
      }
    });
    common_vendor.onShow(() => {
      console.log("App Show");
    });
    common_vendor.onHide(() => {
      console.log("App Hide");
    });
    return () => {
    };
  }
});
function createApp() {
  const app = common_vendor.createSSRApp(_sfc_main);
  app.use(common_vendor.createPinia());
  return { app };
}
createApp().app.mount("#app");
exports.createApp = createApp;
