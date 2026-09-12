import { useState } from "react";

import { solveGeometryProblem } from "../services/geometryApi";

export function useGeometrySolver() {
  const [inputQuestion, setInputQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function solveProblem(nextQuestion = inputQuestion) {
    const trimmedQuestion = nextQuestion.trim();
    if (!trimmedQuestion || loading) return;

    setSubmittedQuestion(trimmedQuestion);
    setInputQuestion("");
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await solveGeometryProblem(trimmedQuestion);
      setResult(response);
    } catch (requestError) {
      console.error("Geometry solve request failed", requestError);
      setInputQuestion(trimmedQuestion);
      setError(requestError.message || "I couldn't solve that problem. Try again.");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setInputQuestion("");
    setSubmittedQuestion("");
    setResult(null);
    setError("");
  }

  function restoreSolution(response) {
    setInputQuestion("");
    setSubmittedQuestion(response.question || "");
    setResult(response);
    setError("");
    setLoading(false);
  }

  return {
    question: submittedQuestion,
    inputQuestion,
    setQuestion: setInputQuestion,
    result,
    loading,
    error,
    solveProblem,
    restoreSolution,
    reset,
  };
}
