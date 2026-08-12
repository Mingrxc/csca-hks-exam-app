"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "detail",
  setup(__props) {
    const question = common_vendor.ref(null);
    const wrongBookId = common_vendor.ref(null);
    const relatedQuestions = common_vendor.ref([]);
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
      common_vendor.index.navigateTo({
        url: `/pages/exam/paper?strategy=knowledge&knowledge=${encodeURIComponent(question.value.knowledgePoint)}`
      });
    };
    const goRedo = () => {
      common_vendor.index.navigateTo({ url: "/pages/wrongbook/redo" });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: question.value
      }, question.value ? common_vendor.e({
        b: common_vendor.t(question.value.typeLabel),
        c: common_vendor.t(question.value.diffLabel),
        d: common_vendor.n(question.value.difficulty),
        e: common_vendor.t(question.value.knowledgePoint),
        f: common_vendor.t(question.value.wrongCount),
        g: common_vendor.t(question.value.stem),
        h: common_vendor.f(question.value.options, (opt, k0, i0) => {
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
        i: common_vendor.t(question.value.analysis),
        j: question.value.confusion
      }, question.value.confusion ? {
        k: common_vendor.t(question.value.confusion)
      } : {}, {
        l: common_vendor.t(question.value.knowledgePoint),
        m: common_vendor.f(relatedQuestions.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.diffLabel),
            b: common_vendor.n(item.difficulty),
            c: common_vendor.t(item.typeLabel),
            d: common_vendor.t(item.stem),
            e: item.id,
            f: common_vendor.o(goRelated, item.id)
          };
        }),
        n: common_vendor.t(question.value.mastered ? "✓ 已掌握" : "标记为已掌握"),
        o: common_vendor.o(markMastered, "87"),
        p: common_vendor.o(goRedo, "08")
      }) : {});
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-98530eac"]]);
wx.createPage(MiniProgramPage);
