"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  props: {
    items: {},
    total: {},
    answeredCount: {},
    current: {}
  },
  emits: ["jump"],
  setup(__props) {
    return (_ctx, _cache) => {
      return {
        a: common_vendor.t(_ctx.answeredCount),
        b: common_vendor.t(_ctx.total),
        c: common_vendor.f(_ctx.items, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.index + 1),
            b: item.answered ? 1 : "",
            c: item.index === _ctx.current ? 1 : "",
            d: item.marked ? 1 : "",
            e: item.index,
            f: common_vendor.o(($event) => _ctx.$emit("jump", item.index), item.index)
          };
        })
      };
    };
  }
});
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-b4deaa03"]]);
wx.createComponent(Component);
