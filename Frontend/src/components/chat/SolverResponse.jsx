import { GeometryVisualizer } from "./GeometryVisualizer";
import { MathBlock, MathInline } from "./MathText";
import { formatResult } from "../../utils/formatNumber";

function operationLabel(operation) {
  return operation.replaceAll("_", " ");
}

function Explanation({ explanation }) {
  if (!explanation || typeof explanation !== "object") {
    return <p>{explanation}</p>;
  }

  return (
    <div className="solution-steps">
      {explanation.concept && <p>{explanation.concept}</p>}
      {explanation.formula && <MathBlock value={explanation.formula} />}
      {Array.isArray(explanation.steps) && explanation.steps.length > 0 && (
        <ol>
          {explanation.steps.map((step, index) => (
            <li key={`${step}-${index}`}><MathBlock value={step} /></li>
          ))}
        </ol>
      )}
      {explanation.conclusion && <p>{explanation.conclusion}</p>}
    </div>
  );
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
        <span className="operation-chip">{response.operationLabel || operationLabel(response.operation)}</span>
      </div>

      <div className="answer-block">
        <span className="answer-label">Result</span>
        <strong>{formatResult(response.result)}</strong>
      </div>

      <div className="explanation-block">
        <span className="answer-label">Explanation</span>
        <Explanation explanation={response.explanation} />
      </div>

      {response.visualization && (
        <GeometryVisualizer visualization={response.visualization} />
      )}
    </article>
  );
}
