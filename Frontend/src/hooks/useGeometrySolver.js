import { useState } from "react";

import { solveGeometryProblem } from "../services/geometryApi";

export function useGeometrySolver() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function solveProblem(nextQuestion = question) {
    const trimmedQuestion = nextQuestion.trim();
    if (!trimmedQuestion || loading) return;

    setQuestion(nextQuestion);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await solveGeometryProblem(trimmedQuestion);
      setResult(response);
    } catch (requestError) {
      console.error("Geometry solve request failed", requestError);
      setError(requestError.message || "I couldn't solve that problem. Try again.");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setQuestion("");
    setResult(null);
    setError("");
  }

  return { question, setQuestion, result, loading, error, solveProblem, reset };
}
