"use strict";
const common_vendor = require("../../common/vendor.js");
const constants_exam = require("../../constants/exam.js");
if (!Array) {
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  (_easycom_t_tag2 + _easycom_t_button2)();
}
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
if (!Math) {
  (_easycom_t_tag + _easycom_t_button)();
}
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  props: {
    question: {},
    index: {},
    userAnswer: {},
    showResult: { type: Boolean },
    isFavorite: { type: Boolean }
  },
  emits: ["select", "favorite"],
  setup(__props) {
    const props = __props;
    const typeLabel = common_vendor.computed(() => constants_exam.QUESTION_TYPE_MAP[props.question.type] || props.question.type);
    const diffLabel = common_vendor.computed(() => constants_exam.DIFFICULTY_MAP[props.question.difficulty] || props.question.difficulty);
    const domainLabel = common_vendor.computed(() => constants_exam.getQuestionDomainLabel(props.question.examType));
    const domainValue = common_vendor.computed(() => constants_exam.getQuestionDomain(props.question));
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
        b: common_vendor.t(_ctx.question.examType),
        c: common_vendor.t(typeLabel.value),
        d: common_vendor.p({
          theme: "primary",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        e: common_vendor.t(diffLabel.value),
        f: common_vendor.p({
          theme: "default",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        g: common_vendor.t(domainLabel.value),
        h: common_vendor.t(domainValue.value),
        i: common_vendor.p({
          theme: "warning",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        j: common_vendor.t(_ctx.isFavorite ? "已收藏" : "收藏"),
        k: common_vendor.o(($event) => _ctx.$emit("favorite"), "95"),
        l: common_vendor.p({
          theme: "default",
          variant: _ctx.isFavorite ? "outline" : "text",
          size: "small",
          shape: "round"
        }),
        m: _ctx.question.stem,
        n: common_vendor.f(_ctx.question.options, (opt, k0, i0) => {
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
        o: _ctx.showResult && _ctx.question.analysis
      }, _ctx.showResult && _ctx.question.analysis ? {
        p: common_vendor.t(_ctx.question.analysis)
      } : {});
    };
  }
});
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-7211204f"]]);
wx.createComponent(Component);
