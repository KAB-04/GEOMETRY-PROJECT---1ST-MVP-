export function Sidebar({ onNewProblem }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-intro">
        <span className="section-kicker">Workspace</span>
        <p>Turn a geometry question into a clear, engine-backed solution.</p>
      </div>
      <nav aria-label="Main navigation">
        <button className="nav-item active" type="button" onClick={onNewProblem}>
          <span aria-hidden="true">＋</span> New problem
        </button>
        <div className="nav-item muted"><span aria-hidden="true">◷</span> History <small>soon</small></div>
        <div className="nav-item muted"><span aria-hidden="true">⌁</span> Topics <small>soon</small></div>
      </nav>
      <div className="sidebar-note">
        <span className="note-mark">i</span>
        <p>Gemini interprets your words. Geometry does the math.</p>
      </div>
    </aside>
  );
}
