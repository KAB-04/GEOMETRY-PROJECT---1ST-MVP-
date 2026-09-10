const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 70000;

function getErrorMessage(data, status) {
  if (data?.error?.message) return data.error.message;
  if (typeof data?.error === "string") return data.error;
  if (data?.message) return data.message;
  if (status >= 500) return "The Geometry server encountered an error.";
  return "I couldn't solve that problem. Try rephrasing the question.";
}

export async function solveGeometryProblem(question) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_URL}/api/solve/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question.trim() }),
      signal: controller.signal,
    });

    const data = await response.json().catch(() => null);
    if (!response.ok || data?.success === false) {
      throw new Error(getErrorMessage(data, response.status));
    }

    if (!data || !Object.prototype.hasOwnProperty.call(data, "result")) {
      throw new Error("The Geometry server returned an invalid response.");
    }

    return {
      question: data.question || question,
      operation: data.operation || "geometry operation",
      operationLabel: data.operation_label || data.operation || "Geometry operation",
      result: data.result,
      explanation: data.explanation || "The Geometry engine returned a result without an explanation.",
      visualization: data.visualization || null,
    };
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The request took too long. Please try again.");
    }
    if (error instanceof TypeError) {
      throw new Error("The Geometry server could not be reached.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}
