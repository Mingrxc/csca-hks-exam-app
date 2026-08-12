"use strict";
const common_vendor = require("../../common/vendor.js");
const constants_exam = require("../../constants/exam.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  props: {
    question: {},
    index: {},
    userAnswer: {},
    showResult: { type: Boolean }
  },
  emits: ["select"],
  setup(__props) {
    const props = __props;
    const typeLabel = common_vendor.computed(() => constants_exam.QUESTION_TYPE_MAP[props.question.type] || props.question.type);
    const diffLabel = common_vendor.computed(() => constants_exam.DIFFICULTY_MAP[props.question.difficulty] || props.question.difficulty);
    function getOptionClass(key) {
      return {
        selected: props.userAnswer === key && !props.showResult,
        correct: props.showResult && key === props.question.answer,
        wrong: props.showResult && props.userAnswer === key && key !== props.question.answer
      };
    }
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(_ctx.index + 1),
        b: common_vendor.t(typeLabel.value),
        c: common_vendor.n(_ctx.question.type),
        d: common_vendor.t(diffLabel.value),
        e: common_vendor.n(_ctx.question.difficulty),
        f: _ctx.question.stem,
        g: common_vendor.f(_ctx.question.options, (opt, k0, i0) => {
          return common_vendor.e({
            a: common_vendor.t(opt.key),
            b: common_vendor.t(opt.text),
            c: _ctx.showResult && opt.key === _ctx.question.answer
          }, _ctx.showResult && opt.key === _ctx.question.answer ? {} : _ctx.showResult && _ctx.userAnswer === opt.key ? {} : {}, {
            d: _ctx.showResult && _ctx.userAnswer === opt.key,
            e: common_vendor.n(getOptionClass(opt.key)),
            f: opt.key,
            g: common_vendor.o(($event) => _ctx.$emit("select", opt.key), opt.key)
          });
        }),
        h: _ctx.showResult && _ctx.question.analysis
      }, _ctx.showResult && _ctx.question.analysis ? {
        i: common_vendor.t(_ctx.question.analysis)
      } : {});
    };
  }
});
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-7211204f"]]);
wx.createComponent(Component);
