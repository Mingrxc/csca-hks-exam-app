"use strict";
const common_vendor = require("../../common/vendor.js");
const utils_index = require("../../utils/index.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  props: {
    seconds: {}
  },
  emits: ["timeout"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const remaining = common_vendor.ref(props.seconds);
    let timer = null;
    const displayText = common_vendor.computed(() => utils_index.formatTime(remaining.value));
    common_vendor.onMounted(() => {
      timer = setInterval(() => {
        if (remaining.value > 0) {
          remaining.value--;
        } else {
          clearInterval(timer);
          emit("timeout");
        }
      }, 1e3);
    });
    common_vendor.onUnmounted(() => {
      if (timer)
        clearInterval(timer);
    });
    return (_ctx, _cache) => {
      return {
        a: common_vendor.t(displayText.value),
        b: remaining.value <= 300 ? 1 : "",
        c: remaining.value <= 60 ? 1 : ""
      };
    };
  }
});
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-d75bb204"]]);
wx.createComponent(Component);
