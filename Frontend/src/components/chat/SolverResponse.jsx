function formatResult(result) {
  if (result === null || result === undefined) return "No result returned";
  if (typeof result === "object") return JSON.stringify(result, null, 2);
  return String(result);
}

function operationLabel(operation) {
  return operation.replaceAll("_", " ");
}

export function SolverResponse({ response }) {
  return (
    <article className="solution-card">
      <div className="solution-heading">
        <div className="assistant-mark" aria-hidden="true">G</div>
        <div>
          <p className="eyebrow">Geometry solution</p>
          <h2>Your answer</h2>
        </div>
        <span className="operation-chip">{operationLabel(response.operation)}</span>
      </div>

      <div className="answer-block">
        <span className="answer-label">Result</span>
        <strong>{formatResult(response.result)}</strong>
      </div>

      <div className="explanation-block">
        <span className="answer-label">Explanation</span>
        <p>{response.explanation}</p>
      </div>

      {response.visualization && (
        <div className="visualization-placeholder">
          <span className="placeholder-icon" aria-hidden="true">◇</span>
          <div>
            <strong>Geometry view ready</strong>
            <p>Interactive visualization will appear in Phase 2.</p>
          </div>
        </div>
      )}
    </article>
  );
}
