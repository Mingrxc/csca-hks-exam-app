"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
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
  __name: "detail",
  setup(__props) {
    const question = common_vendor.ref(null);
    const wrongBookId = common_vendor.ref(null);
    const relatedQuestions = common_vendor.ref([]);
    const domainLabel = common_vendor.computed(() => question.value ? constants_exam.getQuestionDomainLabel(question.value.examType) : "专项");
    const domainValue = common_vendor.computed(() => question.value ? constants_exam.getQuestionDomain(question.value) : "");
    const loadDetail = async (id, questionId) => {
      try {
        const payload = questionId ? await api_index.wrongBookApi.getDetailByQuestion(questionId) : await api_index.wrongBookApi.getDetail(id);
        question.value = api_contracts.toWrongBookDetail(payload);
        wrongBookId.value = payload.id;
        const related = await api_index.wrongBookApi.getRelated(payload.question_id);
        relatedQuestions.value = related.map(api_contracts.toRelatedQuestion);
      } catch {
      }
    };
    common_vendor.onLoad((query) => {
      const id = Number(query == null ? void 0 : query.id);
      const questionId = Number(query == null ? void 0 : query.questionId);
      if (Number.isInteger(questionId) && questionId > 0) {
        loadDetail(void 0, questionId);
        return;
      }
      if (Number.isInteger(id) && id > 0) {
        loadDetail(id);
        return;
      }
      common_vendor.index.showToast({ title: "未找到错题记录", icon: "none" });
      setTimeout(() => common_vendor.index.navigateBack(), 300);
    });
    const markMastered = async () => {
      if (!question.value || !wrongBookId.value)
        return;
      try {
        const payload = await api_index.wrongBookApi.markMastered(wrongBookId.value);
        question.value.mastered = payload.is_mastered;
        common_vendor.index.showToast({ title: payload.is_mastered ? "已标记为掌握" : "已取消标记", icon: "success" });
      } catch {
      }
    };
    const goRelated = () => {
      if (!question.value)
        return;
      const special = encodeURIComponent(domainValue.value);
      common_vendor.index.navigateTo({
        url: `/pages/exam/paper?strategy=knowledge&examType=${question.value.examType}&special=${special}`
      });
    };
    const goRedo = () => {
      if (!question.value)
        return;
      common_vendor.index.navigateTo({ url: `/pages/wrongbook/redo?examType=${question.value.examType}` });
    };
    const sendToAI = () => {
      if (!question.value)
        return;
      common_vendor.index.setStorageSync("ai_prefill", {
        content: question.value.stem,
        topic: `${question.value.examType} 错题咨询`,
        context: [
          `考试类型：${question.value.examType}`,
          `${domainLabel.value}：${domainValue.value}`,
          `我的答案：${question.value.myAnswer || "未作答"}`,
          `正确答案：${question.value.answer || "暂无"}`,
          question.value.analysis ? `解析：${question.value.analysis}` : "",
          question.value.confusion ? `易混选项：${question.value.confusion}` : ""
        ].filter(Boolean).join("\n"),
        examType: question.value.examType
      });
      common_vendor.index.switchTab({ url: "/pages/ai/index" });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: question.value
      }, question.value ? common_vendor.e({
        b: common_vendor.t(question.value.typeLabel),
        c: common_vendor.p({
          theme: "primary",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        d: common_vendor.t(question.value.diffLabel),
        e: common_vendor.n(question.value.difficulty),
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
        j: common_vendor.t(question.value.wrongCount),
        k: common_vendor.p({
          theme: "danger",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        l: common_vendor.t(question.value.stem),
        m: common_vendor.f(question.value.options, (opt, k0, i0) => {
          return common_vendor.e({
            a: common_vendor.t(opt.key),
            b: common_vendor.t(opt.text),
            c: opt.key === question.value.answer
          }, opt.key === question.value.answer ? {} : opt.key === question.value.myAnswer ? {} : {}, {
            d: opt.key === question.value.myAnswer,
            e: opt.key === question.value.answer ? 1 : "",
            f: opt.key === question.value.myAnswer ? 1 : "",
            g: opt.key === question.value.myAnswer && opt.key !== question.value.answer ? 1 : "",
            h: opt.key
          });
        }),
        n: common_vendor.t(question.value.analysis),
        o: question.value.confusion
      }, question.value.confusion ? {
        p: common_vendor.t(question.value.confusion)
      } : {}, {
        q: common_vendor.t(domainLabel.value),
        r: common_vendor.t(domainValue.value),
        s: common_vendor.f(relatedQuestions.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.diffLabel),
            b: "98530eac-4-" + i0,
            c: common_vendor.t(item.typeLabel),
            d: "98530eac-5-" + i0,
            e: common_vendor.t(item.stem),
            f: item.id,
            g: common_vendor.o(goRelated, item.id)
          };
        }),
        t: common_vendor.p({
          theme: "primary",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        v: common_vendor.p({
          theme: "default",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        w: common_vendor.t(question.value.mastered ? "已掌握" : "标记为已掌握"),
        x: common_vendor.o(markMastered, "bf"),
        y: common_vendor.p({
          theme: "primary",
          block: true,
          shape: "round"
        }),
        z: common_vendor.o(sendToAI, "9d"),
        A: common_vendor.p({
          theme: "default",
          variant: "outline",
          block: true,
          shape: "round"
        }),
        B: common_vendor.o(goRedo, "59"),
        C: common_vendor.p({
          theme: "default",
          variant: "outline",
          block: true,
          shape: "round"
        })
      }) : {});
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-98530eac"]]);
wx.createPage(MiniProgramPage);
