"use strict";
const common_vendor = require("../common/vendor.js");
const BASE_URL = "https://bigger-carrying-cheers-close.trycloudflare.com/api/v1".replace(/\/$/, "");
const FALLBACK_BASE_URL = "http://127.0.0.1:8000/api/v1".replace(/\/$/, "");
const API_BASE_URLS = Array.from(new Set([BASE_URL, FALLBACK_BASE_URL].filter(Boolean)));
function formatNetworkErrorMessage(err) {
  const raw = typeof (err == null ? void 0 : err.errMsg) === "string" ? err.errMsg : "";
  if (!raw)
    return "网络异常";
  if (raw.includes("url not in domain list"))
    return "域名未配置";
  if (raw.includes("SSL") || raw.includes("TLS"))
    return "证书校验失败";
  if (raw.includes("timeout"))
    return "请求超时";
  if (raw.includes("fail"))
    return raw.replace(/^fail\s*/i, "").slice(0, 30);
  return raw.slice(0, 30);
}
let loginPromise = null;
function wxLoginWithBaseUrl(baseUrl, code) {
  return new Promise((resolve, reject) => {
    common_vendor.index.request({
      url: baseUrl + "/user/wx-login",
      method: "POST",
      data: { code },
      header: { "Content-Type": "application/json" },
      success: (response) => {
        const payload = response.data;
        if (response.statusCode === 200 && (payload == null ? void 0 : payload.code) === 0) {
          common_vendor.index.setStorageSync("token", payload.data.token);
          resolve(payload.data);
        } else {
          reject(payload || new Error("登录失败"));
        }
      },
      fail: reject
    });
  });
}
function ensureLogin(force = false) {
  const storedToken = common_vendor.index.getStorageSync("token");
  if (storedToken && !force) {
    return Promise.resolve({ token: storedToken, openid: "" });
  }
  if (loginPromise)
    return loginPromise;
  loginPromise = new Promise((resolve, reject) => {
    common_vendor.index.login({
      success: (loginResult) => {
        if (!loginResult.code) {
          reject(new Error("微信登录未返回临时凭证"));
          return;
        }
        const tryLogin = (baseIndex) => {
          wxLoginWithBaseUrl(API_BASE_URLS[baseIndex], loginResult.code).then(resolve).catch((error) => {
            if (baseIndex + 1 < API_BASE_URLS.length) {
              tryLogin(baseIndex + 1);
              return;
            }
            reject(error);
          });
        };
        tryLogin(0);
      },
      fail: reject
    });
  }).finally(() => {
    loginPromise = null;
  });
  return loginPromise;
}
function request(options) {
  const finishLoading = () => {
    if (options.showLoading !== false)
      common_vendor.index.hideLoading();
  };
  return new Promise((resolve, reject) => {
    if (options.showLoading !== false) {
      common_vendor.index.showLoading({ title: "加载中...", mask: true });
    }
    const send = (token, allowRetry, baseIndex = 0) => {
      const header = {
        "Content-Type": "application/json",
        ...options.header
      };
      if (token)
        header.Authorization = `Bearer ${token}`;
      common_vendor.index.request({
        url: API_BASE_URLS[baseIndex] + options.url,
        method: options.method || "GET",
        data: options.data,
        header,
        success: async (res) => {
          const { statusCode, data } = res;
          if (statusCode === 200 && data.code === 0) {
            finishLoading();
            resolve(data.data);
            return;
          }
          if (statusCode === 401 && allowRetry && options.url !== "/user/wx-login") {
            common_vendor.index.removeStorageSync("token");
            try {
              const login = await ensureLogin(true);
              send(login.token, false);
              return;
            } catch {
            }
          }
          finishLoading();
          if (statusCode === 401) {
            common_vendor.index.removeStorageSync("token");
            common_vendor.index.showToast({ title: "登录已失效，请重试", icon: "none" });
          } else {
            common_vendor.index.showToast({ title: (data == null ? void 0 : data.message) || (data == null ? void 0 : data.detail) || "请求失败", icon: "none" });
          }
          reject(data);
        },
        fail: (err) => {
          if (baseIndex + 1 < API_BASE_URLS.length) {
            send(token, allowRetry, baseIndex + 1);
            return;
          }
          finishLoading();
          const message = formatNetworkErrorMessage(err);
          console.error("[request fail]", options.url, err);
          common_vendor.index.showToast({ title: message, icon: "none" });
          reject(err);
        }
      });
    };
    const storedToken = common_vendor.index.getStorageSync("token");
    const requiresAuth = options.requireAuth !== false;
    if (!requiresAuth) {
      send(storedToken, true);
      return;
    }
    if (storedToken || options.url === "/user/wx-login") {
      send(storedToken, true);
      return;
    }
    ensureLogin().then((login) => send(login.token, true)).catch(() => send("", true));
  });
}
async function download(url) {
  let token = common_vendor.index.getStorageSync("token");
  if (!token) {
    try {
      token = (await ensureLogin()).token;
    } catch {
    }
  }
  const downloadWithBaseUrl = (baseIndex) => new Promise((resolve, reject) => {
    common_vendor.index.downloadFile({
      url: API_BASE_URLS[baseIndex] + url,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (response) => {
        if (response.statusCode === 200) {
          resolve(response.tempFilePath);
        } else {
          reject(new Error(`PDF download failed with status ${response.statusCode}`));
        }
      },
      fail: (error) => {
        if (baseIndex + 1 < API_BASE_URLS.length) {
          downloadWithBaseUrl(baseIndex + 1).then(resolve).catch(reject);
          return;
        }
        reject(error);
      }
    });
  });
  return downloadWithBaseUrl(0);
}
const userApi = {
  wxLogin: (code) => request({
    url: "/user/wx-login",
    method: "POST",
    data: { code },
    requireAuth: false
  }),
  getDashboard: () => request({ url: "/user/dashboard" }),
  getUserInfo: () => request({ url: "/user/info" }),
  updateProfile: (data) => request({ url: "/user/profile", method: "PUT", data })
};
const contentApi = {
  listHome: () => request({ url: "/content/home", showLoading: false, requireAuth: false }),
  get: (id) => request({ url: `/content/${id}`, requireAuth: false }),
  listAdmin: () => request({ url: "/content/list" }),
  create: (data) => request({ url: "/content", method: "POST", data }),
  update: (id, data) => request({ url: `/content/${id}`, method: "PUT", data }),
  remove: (id) => request({ url: `/content/${id}`, method: "DELETE" })
};
const questionApi = {
  getPapers: (params) => request({ url: "/question/papers", data: params }),
  getSpecialOptions: (examType, limit = 100) => request({
    url: `/question/special-options?examType=${examType}&limit=${limit}`,
    showLoading: false
  }),
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
  generateRedoPaper: (params) => request({
    url: `/wrongbook/redo-paper?examType=${params.examType}&limit=${params.limit || 20}`,
    method: "POST"
  }),
  exportPdf: (params) => {
    const query = Object.entries(params).map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join("&");
    return download(`/wrongbook/export-pdf?${query}`);
  }
};
const favoriteApi = {
  list: (limit = 50) => request({ url: `/favorite/list?limit=${limit}` }),
  status: (questionId) => request({ url: `/favorite/status/${questionId}`, showLoading: false }),
  toggle: (questionId) => request({
    url: "/favorite/toggle",
    method: "POST",
    data: { questionId },
    showLoading: false
  })
};
const aiApi = {
  chat: (data) => request({ url: "/ai/chat", method: "POST", data })
};
exports.aiApi = aiApi;
exports.contentApi = contentApi;
exports.ensureLogin = ensureLogin;
exports.examApi = examApi;
exports.favoriteApi = favoriteApi;
exports.questionApi = questionApi;
exports.userApi = userApi;
exports.wrongBookApi = wrongBookApi;
