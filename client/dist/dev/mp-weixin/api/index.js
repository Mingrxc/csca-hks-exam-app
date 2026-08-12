"use strict";
const common_vendor = require("../common/vendor.js");
var define_import_meta_env_default = {};
const DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1";
const BASE_URL = (define_import_meta_env_default.VITE_API_BASE_URL || DEFAULT_BASE_URL).replace(/\/$/, "");
function request(options) {
  const token = common_vendor.index.getStorageSync("token");
  const header = {
    "Content-Type": "application/json",
    ...options.header
  };
  if (token) {
    header.Authorization = `Bearer ${token}`;
  }
  return new Promise((resolve, reject) => {
    if (options.showLoading !== false) {
      common_vendor.index.showLoading({ title: "加载中...", mask: true });
    }
    common_vendor.index.request({
      url: BASE_URL + options.url,
      method: options.method || "GET",
      data: options.data,
      header,
      success: (res) => {
        const { statusCode, data } = res;
        if (statusCode === 200 && data.code === 0) {
          resolve(data.data);
        } else if (statusCode === 401) {
          common_vendor.index.removeStorageSync("token");
          common_vendor.index.showToast({ title: "请先登录", icon: "none" });
          reject(data);
        } else {
          common_vendor.index.showToast({ title: (data == null ? void 0 : data.message) || (data == null ? void 0 : data.detail) || "请求失败", icon: "none" });
          reject(data);
        }
      },
      fail: (err) => {
        common_vendor.index.showToast({ title: "网络异常", icon: "none" });
        reject(err);
      },
      complete: () => {
        if (options.showLoading !== false) {
          common_vendor.index.hideLoading();
        }
      }
    });
  });
}
const questionApi = {
  getPapers: (params) => request({ url: "/question/papers", data: params }),
  generatePaper: (config) => request({
    url: "/question/generate-paper",
    method: "POST",
    data: config
  }),
  getQuestionDetail: (id) => request({ url: `/question/${id}` })
};
const examApi = {
  submitAnswer: (data) => request({
    url: "/exam/submit",
    method: "POST",
    data,
    showLoading: false
  }),
  getResult: (paperId) => request({ url: `/exam/result/${paperId}` })
};
const wrongBookApi = {
  getList: (params) => request({ url: "/wrongbook/list", data: params }),
  getDetail: (id) => request({ url: `/wrongbook/${id}` }),
  getDetailByQuestion: (questionId) => request({ url: `/wrongbook/question/${questionId}` }),
  markMastered: (id) => request({
    url: `/wrongbook/${id}/master`,
    method: "PUT"
  }),
  getRelated: (questionId) => request({
    url: `/wrongbook/related/${questionId}`
  }),
  exportPdf: (params) => request({
    url: "/wrongbook/export-pdf",
    method: "POST",
    data: params
  })
};
exports.examApi = examApi;
exports.questionApi = questionApi;
exports.wrongBookApi = wrongBookApi;
