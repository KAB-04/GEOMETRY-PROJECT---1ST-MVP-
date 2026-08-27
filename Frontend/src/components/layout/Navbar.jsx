export function Navbar({ onNewProblem }) {
  return (
    <header className="topbar">
      <a className="brand" href="/" aria-label="Geometry home">
        <span className="brand-symbol" aria-hidden="true">∠</span>
        <span>GEOMETRY</span>
      </a>
      <div className="topbar-actions">
        <span className="status-dot"><i /> Engine online</span>
        <button className="new-problem-button" type="button" onClick={onNewProblem}>+ New problem</button>
      </div>
    </header>
  );
}
