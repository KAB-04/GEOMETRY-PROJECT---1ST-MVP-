import { useState } from "react";

import { LoadingMessage } from "./components/chat/LoadingMessage";
import { ProblemInput } from "./components/chat/ProblemInput";
import { SolverResponse } from "./components/chat/SolverResponse";
import { HistoryPanel } from "./components/history/HistoryPanel";
import { Navbar } from "./components/layout/Navbar";
import { Sidebar } from "./components/layout/Sidebar";
import { TopicsPanel } from "./components/topics/TopicsPanel";
import { useGeometrySolver } from "./hooks/useGeometrySolver";

const examples = [
  "Find the distance between the points (0,0) and (3,4).",
  "Find the area of a circle with radius 7.",
  "Find the hypotenuse of a right triangle with sides 3 and 4.",
];

function App() {
  const solver = useGeometrySolver();
  const [activeView, setActiveView] = useState("solver");

  function handleNewProblem() {
    solver.reset();
    setActiveView("solver");
  }

  function handleRestore(response) {
    solver.restoreSolution(response);
    setActiveView("solver");
  }

  function handleUseExample(example) {
    solver.setQuestion(example);
    setActiveView("solver");
  }

  return (
    <div className="app-shell">
      <Navbar onNewProblem={handleNewProblem} />
      <div className="app-body">
        <Sidebar activeView={activeView} onNavigate={setActiveView} onNewProblem={handleNewProblem} />
        <main className="solver-main">
          {activeView === "solver" && <div className="solver-content">
            <section className="welcome-block">
              <p className="eyebrow">A calmer way to solve</p>
              <h1>Make geometry<br /><em>click.</em></h1>
              <p className="welcome-copy">Bring a problem. Get a precise answer, a useful explanation, and a little more confidence for the next one.</p>
            </section>

            <section className="conversation" aria-live="polite">
              {solver.question && (
                <div className="question-message">
                  <span className="message-label">You asked</span>
                  <p>{solver.question}</p>
                </div>
              )}
              {solver.loading && <LoadingMessage />}
              {solver.error && (
                <div className="error-message" role="alert">
                  <span aria-hidden="true">!</span>
                  <p>{solver.error}</p>
                </div>
              )}
              {solver.result && <SolverResponse response={solver.result} />}
            </section>

            {!solver.question && (
              <section className="example-section">
                <div className="section-heading"><span>Start with an example</span><span className="rule" /></div>
                <div className="example-list">
                  {examples.map((example) => (
                    <button key={example} type="button" onClick={() => solver.setQuestion(example)}>{example}<span aria-hidden="true">↗</span></button>
                  ))}
                </div>
              </section>
            )}

            <ProblemInput
              value={solver.inputQuestion}
              onChange={solver.setQuestion}
              onSubmit={() => solver.solveProblem()}
              loading={solver.loading}
            />
            <p className="privacy-note">Your question is sent securely to the Geometry engine. Gemini is never called from the browser.</p>
          </div>}
          {activeView === "history" && <HistoryPanel onRestore={handleRestore} />}
          {activeView === "topics" && <TopicsPanel onUseExample={handleUseExample} />}
        </main>
      </div>
    </div>
  );
}

export default App;
