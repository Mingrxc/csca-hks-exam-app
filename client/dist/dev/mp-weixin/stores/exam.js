"use strict";
const common_vendor = require("../common/vendor.js");
const useExamStore = common_vendor.defineStore("exam", () => {
  const config = common_vendor.ref({
    examType: "CSCA",
    questionCount: 20,
    difficulty: "all",
    strategy: "random",
    knowledgePoints: [],
    mode: "practice",
    timeLimit: 60
  });
  const paperId = common_vendor.ref(null);
  const questions = common_vendor.ref([]);
  const currentIndex = common_vendor.ref(0);
  const answers = common_vendor.ref({});
  const startTime = common_vendor.ref(0);
  const endTime = common_vendor.ref(0);
  const currentQuestion = common_vendor.computed(() => questions.value[currentIndex.value] || null);
  const totalCount = common_vendor.computed(() => questions.value.length);
  const answeredCount = common_vendor.computed(() => Object.keys(answers.value).length);
  const progressPercent = common_vendor.computed(
    () => totalCount.value ? Math.round(answeredCount.value / totalCount.value * 100) : 0
  );
  const timeUsed = common_vendor.computed(() => {
    const end = endTime.value || Date.now();
    return Math.floor((end - startTime.value) / 1e3);
  });
  const correctCount = common_vendor.computed(() => {
    let count = 0;
    questions.value.forEach((q, i) => {
      if (answers.value[i] === q.answer)
        count++;
    });
    return count;
  });
  function setConfig(c) {
    Object.assign(config.value, c);
  }
  function setQuestions(qs) {
    questions.value = qs;
  }
  function setPaper(id, qs) {
    paperId.value = id;
    setQuestions(qs);
  }
  function setCurrentIndex(index) {
    if (index >= 0 && index < questions.value.length) {
      currentIndex.value = index;
    }
  }
  function setAnswer(index, answer) {
    answers.value[index] = answer;
  }
  function clearAnswer(index) {
    delete answers.value[index];
  }
  function start() {
    currentIndex.value = 0;
    answers.value = {};
    startTime.value = Date.now();
    endTime.value = 0;
  }
  function finish() {
    endTime.value = Date.now();
  }
  function reset() {
    config.value = {
      examType: "CSCA",
      questionCount: 20,
      difficulty: "all",
      strategy: "random",
      knowledgePoints: [],
      mode: "practice",
      timeLimit: 60
    };
    questions.value = [];
    paperId.value = null;
    currentIndex.value = 0;
    answers.value = {};
    startTime.value = 0;
    endTime.value = 0;
  }
  return {
    config,
    paperId,
    questions,
    currentIndex,
    answers,
    startTime,
    endTime,
    currentQuestion,
    totalCount,
    answeredCount,
    progressPercent,
    timeUsed,
    correctCount,
    setConfig,
    setPaper,
    setQuestions,
    setCurrentIndex,
    setAnswer,
    clearAnswer,
    start,
    finish,
    reset
  };
});
exports.useExamStore = useExamStore;
