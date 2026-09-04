"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const common_vendor = require("./common/vendor.js");
if (!Math) {
  "./pages/index/index.js";
  "./pages/exam/index.js";
  "./pages/exam/history.js";
  "./pages/exam/paper.js";
  "./pages/exam/answer.js";
  "./pages/exam/result.js";
  "./pages/ai/index.js";
  "./pages/favorite/index.js";
  "./pages/content-admin/index.js";
  "./pages/profile/index.js";
  "./pages/wrongbook/index.js";
  "./pages/wrongbook/detail.js";
  "./pages/wrongbook/redo.js";
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "App",
  setup(__props) {
    common_vendor.onShow(() => {
    });
    common_vendor.onHide(() => {
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
