export function Sidebar({ activeView, onNavigate, onNewProblem }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-intro">
        <span className="section-kicker">Workspace</span>
        <p>Turn a geometry question into a clear, engine-backed solution.</p>
      </div>
      <nav aria-label="Main navigation">
        <button className={`nav-item ${activeView === "solver" ? "active" : ""}`} type="button" onClick={onNewProblem}>
          <span aria-hidden="true">+</span> New problem
        </button>
        <button className={`nav-item ${activeView === "history" ? "active" : ""}`} type="button" onClick={() => onNavigate("history")}>
          <span aria-hidden="true">H</span> History
        </button>
        <button className={`nav-item ${activeView === "topics" ? "active" : ""}`} type="button" onClick={() => onNavigate("topics")}>
          <span aria-hidden="true">T</span> Topics
        </button>
      </nav>
      <div className="sidebar-note">
        <span className="note-mark">i</span>
        <p>Gemini interprets your words. Geometry does the math.</p>
      </div>
    </aside>
  );
}
