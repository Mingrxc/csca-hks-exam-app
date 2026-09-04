"use strict";
const common_vendor = require("../../common/vendor.js");
const api_index = require("../../api/index.js");
const api_contracts = require("../../api/contracts.js");
const constants_exam = require("../../constants/exam.js");
if (!Array) {
  const _easycom_t_tag2 = common_vendor.resolveComponent("t-tag");
  const _easycom_t_button2 = common_vendor.resolveComponent("t-button");
  const _easycom_t_empty2 = common_vendor.resolveComponent("t-empty");
  (_easycom_t_tag2 + _easycom_t_button2 + _easycom_t_empty2)();
}
const _easycom_t_tag = () => "../../node-modules/@tdesign/uniapp/dist/tag/tag.js";
const _easycom_t_button = () => "../../node-modules/@tdesign/uniapp/dist/button/button.js";
const _easycom_t_empty = () => "../../node-modules/@tdesign/uniapp/dist/empty/empty.js";
if (!Math) {
  (_easycom_t_tag + _easycom_t_button + _easycom_t_empty)();
}
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
    const filters = common_vendor.reactive({
      examType: "all",
      knowledge: "all",
      wrongCount: "all"
    });
    const specialFetched = common_vendor.reactive({
      CSCA: false,
      HKS: false
    });
    const specialOptionsByExam = common_vendor.reactive({
      CSCA: [...constants_exam.CSCA_SUBJECT_OPTIONS],
      HKS: [...constants_exam.HSK_KNOWLEDGE_OPTIONS]
    });
    const specialLabel = common_vendor.computed(() => {
      if (filters.examType === "CSCA")
        return constants_exam.getSpecialLabel("CSCA");
      if (filters.examType === "HKS")
        return constants_exam.getSpecialLabel("HKS");
      return "专项";
    });
    const specialOptions = common_vendor.computed(() => {
      if (filters.examType === "CSCA")
        return specialOptionsByExam.CSCA;
      if (filters.examType === "HKS")
        return specialOptionsByExam.HKS;
      return Array.from(/* @__PURE__ */ new Set([...specialOptionsByExam.CSCA, ...specialOptionsByExam.HKS]));
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
    const domainLabel = (item) => constants_exam.getQuestionDomainLabel(item.examType);
    const domainValue = (item) => constants_exam.getQuestionDomain(item);
    const loadSpecialOptions = async (examType) => {
      if (specialFetched[examType])
        return;
      try {
        const options = await api_index.questionApi.getSpecialOptions(examType);
        specialOptionsByExam[examType] = options.map((item) => item.label || item.value).filter(Boolean);
      } catch {
        specialOptionsByExam[examType] = examType === "CSCA" ? [...constants_exam.CSCA_SUBJECT_OPTIONS] : [...constants_exam.HSK_KNOWLEDGE_OPTIONS];
      } finally {
        specialFetched[examType] = true;
      }
    };
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
    const setExamTypeFilter = (tab) => {
      if (filters.examType === tab) {
        activeTab.value = tab;
        return;
      }
      activeTab.value = tab;
      filters.examType = tab;
      filters.knowledge = "all";
      loadWrongList();
    };
    const selectTab = (tab) => {
      setExamTypeFilter(tab);
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
      if (filters.examType === "CSCA" || filters.examType === "HKS") {
        openRedo(filters.examType);
        return;
      }
      common_vendor.index.showActionSheet({
        itemList: ["CSCA 错题", "HKS 错题"],
        success: ({ tapIndex }) => openRedo(tapIndex === 0 ? "CSCA" : "HKS")
      });
    };
    const openRedo = (examType) => {
      common_vendor.index.navigateTo({ url: `/pages/wrongbook/redo?examType=${examType}` });
    };
    const exportPdf = async () => {
      common_vendor.index.showLoading({ title: "正在生成...", mask: true });
      try {
        const filePath = await api_index.wrongBookApi.exportPdf({
          examType: filters.examType,
          knowledge: filters.knowledge,
          wrongCount: filters.wrongCount
        });
        await new Promise((resolve, reject) => {
          common_vendor.index.openDocument({
            filePath,
            fileType: "pdf",
            showMenu: true,
            success: () => resolve(),
            fail: reject
          });
        });
      } catch {
        common_vendor.index.showToast({ title: "PDF 导出失败", icon: "none" });
      } finally {
        common_vendor.index.hideLoading();
      }
    };
    void loadSpecialOptions("CSCA");
    void loadSpecialOptions("HKS");
    common_vendor.onShow(loadWrongList);
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(wrongList.value.length),
        b: common_vendor.p({
          theme: "danger",
          variant: "light",
          shape: "round"
        }),
        c: common_vendor.f(tabs, (t, k0, i0) => {
          return {
            a: common_vendor.t(t.label),
            b: activeTab.value === t.key ? 1 : "",
            c: t.key,
            d: common_vendor.o(($event) => selectTab(t.key), t.key)
          };
        }),
        d: common_vendor.t(activeFilterLabel.value),
        e: common_vendor.o(($event) => showFilters.value = true, "14"),
        f: common_vendor.p({
          theme: "default",
          variant: "text",
          size: "small",
          shape: "round"
        }),
        g: showFilters.value
      }, showFilters.value ? {
        h: filters.examType === "all" ? 1 : "",
        i: common_vendor.o(($event) => setExamTypeFilter("all"), "46"),
        j: filters.examType === "CSCA" ? 1 : "",
        k: common_vendor.o(($event) => setExamTypeFilter("CSCA"), "01"),
        l: filters.examType === "HKS" ? 1 : "",
        m: common_vendor.o(($event) => setExamTypeFilter("HKS"), "09"),
        n: common_vendor.t(specialLabel.value),
        o: filters.knowledge === "all" ? 1 : "",
        p: common_vendor.o(($event) => {
          filters.knowledge = "all";
          applyFilters();
        }, "d9"),
        q: common_vendor.f(specialOptions.value, (k, k0, i0) => {
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
        r: filters.wrongCount === "all" ? 1 : "",
        s: common_vendor.o(($event) => {
          filters.wrongCount = "all";
          applyFilters();
        }, "88"),
        t: filters.wrongCount === "1" ? 1 : "",
        v: common_vendor.o(($event) => {
          filters.wrongCount = "1";
          applyFilters();
        }, "9e"),
        w: filters.wrongCount === "2+" ? 1 : "",
        x: common_vendor.o(($event) => {
          filters.wrongCount = "2+";
          applyFilters();
        }, "36"),
        y: common_vendor.o(resetFilters, "aa"),
        z: common_vendor.p({
          theme: "default",
          variant: "outline",
          shape: "round"
        }),
        A: common_vendor.o(($event) => showFilters.value = false, "bd"),
        B: common_vendor.p({
          theme: "primary",
          shape: "round"
        })
      } : {}, {
        C: wrongList.value.length > 0
      }, wrongList.value.length > 0 ? {
        D: common_vendor.t(wrongList.value.length),
        E: common_vendor.t(masteredCount.value)
      } : {}, {
        F: common_vendor.f(wrongList.value, (item, k0, i0) => {
          return {
            a: common_vendor.t(item.examType),
            b: "168bbcdb-4-" + i0,
            c: common_vendor.t(domainLabel(item)),
            d: common_vendor.t(domainValue(item)),
            e: "168bbcdb-5-" + i0,
            f: common_vendor.t(item.typeLabel),
            g: "168bbcdb-6-" + i0,
            h: common_vendor.t(item.mastered ? "已掌握" : `错${item.wrongCount}次`),
            i: "168bbcdb-7-" + i0,
            j: common_vendor.p({
              theme: item.mastered ? "success" : "danger",
              variant: "light",
              shape: "round",
              size: "small"
            }),
            k: common_vendor.t(item.stem),
            l: common_vendor.t(item.lastWrongAt),
            m: item.id,
            n: common_vendor.o(($event) => goDetail(item.id), item.id)
          };
        }),
        G: common_vendor.p({
          theme: "primary",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        H: common_vendor.p({
          theme: "warning",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        I: common_vendor.p({
          theme: "default",
          variant: "light",
          shape: "round",
          size: "small"
        }),
        J: !isLoading.value && wrongList.value.length === 0
      }, !isLoading.value && wrongList.value.length === 0 ? {
        K: common_vendor.p({
          description: "太棒了！没有错题"
        })
      } : {}, {
        L: wrongList.value.length > 0
      }, wrongList.value.length > 0 ? {
        M: common_vendor.o(goRedo, "6f"),
        N: common_vendor.p({
          theme: "primary",
          block: true,
          shape: "round"
        }),
        O: common_vendor.o(exportPdf, "9f"),
        P: common_vendor.p({
          theme: "default",
          variant: "outline",
          block: true,
          shape: "round"
        })
      } : {});
    };
  }
});
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-168bbcdb"]]);
wx.createPage(MiniProgramPage);
