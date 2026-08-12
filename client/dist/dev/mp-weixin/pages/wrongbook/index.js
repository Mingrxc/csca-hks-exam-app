"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const constants_exam = require("../../constants/exam.js");
const _sfc_main = /* @__PURE__ */ common_vendor.defineComponent({
  __name: "index",
  setup(__props) {
    const activeTab = common_vendor.ref("all");
    const showFilters = common_vendor.ref(false);
    const isLoading = common_vendor.ref(false);
    const tabs = [
      { key: "all", label: "全部" },
      { key: "CSCA", label: "CSCA" },
      { key: "HKS", label: "HKS" }
    ];
    const knowledgePoints = constants_exam.WRONG_BOOK_KNOWLEDGE_POINTS;
    const filters = common_vendor.reactive({
      examType: "all",
      knowledge: "all",
      wrongCount: "all"
    });
    const activeFilterLabel = common_vendor.computed(() => {
      const parts = [];
      if (filters.examType !== "all")
        parts.push(filters.examType);
      if (filters.knowledge !== "all")
        parts.push(filters.knowledge);
      if (filters.wrongCount !== "all")
        parts.push(filters.wrongCount === "1" ? "错1次" : "错2次+");
      return parts.length > 0 ? parts.join(" · ") : "筛选";
    });
    const wrongList = common_vendor.ref([]);
    const masteredCount = common_vendor.computed(() => wrongList.value.filter((w) => w.mastered).length);
    const loadWrongList = async () => {
      if (isLoading.value)
        return;
      isLoading.value = true;
      try {
        const items = await api_index.wrongBookApi.getList({
          examType: filters.examType,
          knowledge: filters.knowledge,
          wrongCount: filters.wrongCount
        });
        wrongList.value = items.map(api_contracts.toWrongBookListItem);
      } catch {
      } finally {
        isLoading.value = false;
      }
    };
    const selectTab = (tab) => {
      activeTab.value = tab;
      filters.examType = tab;
      loadWrongList();
    };
    const applyFilters = () => {
      loadWrongList();
    };
    const resetFilters = () => {
      filters.examType = "all";
      filters.knowledge = "all";
      filters.wrongCount = "all";
      activeTab.value = "all";
      showFilters.value = false;
      loadWrongList();
    };
    const goDetail = (id) => {
      common_vendor.index.navigateTo({ url: `/pages/wrongbook/detail?id=${id}` });
    };
    const goRedo = () => {
      common_vendor.index.navigateTo({ url: "/pages/wrongbook/redo" });
    };
    const exportPdf = async () => {
      try {
        await api_index.wrongBookApi.exportPdf({
          examType: filters.examType,
          knowledge: filters.knowledge,
          wrongCount: filters.wrongCount
        });
      } catch {
      }
    };
    common_vendor.onShow(loadWrongList);
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.f(tabs, (t, k0, i0) => {
          return {
            a: common_vendor.t(t.label),
            b: activeTab.value === t.key ? 1 : "",
            c: t.key,
            d: common_vendor.o(($event) => selectTab(t.key), t.key)
          };
        }),
        b: common_vendor.t(activeFilterLabel.value),
        c: common_vendor.o(($event) => showFilters.value = true, "c1"),
        d: showFilters.value
      }, showFilters.value ? {
        e: filters.examType === "all" ? 1 : "",
        f: common_vendor.o(($event) => {
          filters.examType = "all";
          applyFilters();
        }, "af"),
        g: filters.examType === "CSCA" ? 1 : "",
        h: common_vendor.o(($event) => {
          filters.examType = "CSCA";
          applyFilters();
        }, "fc"),
        i: filters.examType === "HKS" ? 1 : "",
        j: common_vendor.o(($event) => {
          filters.examType = "HKS";
          applyFilters();
        }, "b8"),
        k: filters.knowledge === "all" ? 1 : "",
        l: common_vendor.o(($event) => {
          filters.knowledge = "all";
          applyFilters();
        }, "eb"),
        m: common_vendor.f(common_vendor.unref(knowledgePoints), (k, k0, i0) => {
          return {
            a: common_vendor.t(k),
            b: filters.knowledge === k ? 1 : "",
            c: k,
            d: common_vendor.o(($event) => {
              filters.knowledge = k;
              applyFilters();
            }, k)
          };
        }),
        n: filters.wrongCount === "all" ? 1 : "",
        o: common_vendor.o(($event) => {
          filters.wrongCount = "all";
          applyFilters();
        }, "d6"),
        p: filters.wrongCount === "1" ? 1 : "",
        q: common_vendor.o(($event) => {
          filters.wrongCount = "1";
          applyFilters();
        }, "6b"),
        r: filters.wrongCount === "2+" ? 1 : "",
        s: common_vendor.o(($event) => {
          filters.wrongCount = "2+";
          applyFilters();
        }, "b5"),
        t: common_vendor.o(resetFilters, "cc"),
        v: common_vendor.o(($event) => showFilters.value = false, "14")
      } : {}, {
        w: wrongList.value.length > 0
      }, wrongList.value.length > 0 ? {
        x: common_vendor.t(wrongList.value.length),
        y: common_vendor.t(masteredCount.value)
      } : {}, {
        z: common_vendor.f(wrongList.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.typeLabel),
            b: common_vendor.t(item.diffLabel),
            c: common_vendor.n(item.difficulty),
            d: common_vendor.t(item.knowledgePoint),
            e: common_vendor.t(item.mastered ? "已掌握" : "错" + item.wrongCount + "次"),
            f: item.mastered ? 1 : "",
            g: common_vendor.t(item.stem),
            h: common_vendor.t(item.lastWrongAt),
            i: item.id,
            j: common_vendor.o(($event) => goDetail(item.id), item.id)
          };
        }),
        A: !isLoading.value && wrongList.value.length === 0
      }, !isLoading.value && wrongList.value.length === 0 ? {} : {}, {
        B: wrongList.value.length > 0
      }, wrongList.value.length > 0 ? {
        C: common_vendor.o(goRedo, "3d"),
        D: common_vendor.o(exportPdf, "f2")
      } : {});
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-168bbcdb"]]);
wx.createPage(MiniProgramPage);
