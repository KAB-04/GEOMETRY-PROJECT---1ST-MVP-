export function ProblemInput({ value, onChange, onSubmit, loading }) {
  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <form className="problem-input" onSubmit={(event) => { event.preventDefault(); onSubmit(); }}>
      <label className="sr-only" htmlFor="geometry-question">Geometry question</label>
      <textarea
        id="geometry-question"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a geometry question..."
        rows={3}
        disabled={loading}
      />
      <div className="input-footer">
        <span className="input-hint">Enter to solve · Shift + Enter for a new line</span>
        <button className="solve-button" type="submit" disabled={loading || !value.trim()}>
          <span>{loading ? "Solving" : "Solve"}</span>
          <span aria-hidden="true">{loading ? "..." : "↗"}</span>
        </button>
      </div>
    </form>
  );
}
