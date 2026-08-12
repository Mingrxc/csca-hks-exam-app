"use strict";
require("../constants/exam.js");
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}
function getGreeting() {
  const hour = (/* @__PURE__ */ new Date()).getHours();
  if (hour < 6)
    return "夜深了，";
  if (hour < 12)
    return "早上好，";
  if (hour < 14)
    return "中午好，";
  if (hour < 18)
    return "下午好，";
  return "晚上好，";
}
exports.formatTime = formatTime;
exports.getGreeting = getGreeting;
