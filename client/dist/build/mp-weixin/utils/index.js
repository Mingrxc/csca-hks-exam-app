"use strict";require("../constants/exam.js"),exports.formatTime=function(t){const r=Math.floor(t/60),a=t%60;return`${String(r).padStart(2,"0")}:${String(a).padStart(2,"0")}`};
