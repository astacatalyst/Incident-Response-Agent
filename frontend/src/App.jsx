import "./states.css";
import { useEffect, useState } from "react";
import RespondView from "./views/RespondView";
import CompareView from "./views/CompareView";
import HistoryView from "./views/HistoryView";
import DashboardView from "./views/DashboardView";
import { getHealth } from "./lib/api";

const TABS = [
  ["compare", "Before / After demo"],
  ["respond", "Respond to incident"],
  ["history", "Incident history"],
  ["memory", "Memory dashboard"],
];

function App() {
  const [tab, setTab] = useState("compare");
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: "offline" }));
  }, []);

  return (
    <div className="app">
      <h1>Incident Response Agent</h1>
      <p className="subtitle">An on-call assistant that remembers every past incident.</p>
      {health && (
        <p className={`status status-${health.status}`}>
          Backend: {health.status}
          {health.hindsight && ` · Memory: ${health.hindsight} · LLM: ${health.llm}`}
        </p>
      )}
      <nav className="tabs">
        {TABS.map(([id, label]) => (
          <button key={id} className={tab === id ? "tab active" : "tab"} onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </nav>
      {tab === "compare" && <CompareView />}
      {tab === "respond" && <RespondView />}
      {tab === "history" && <HistoryView />}
      {tab === "memory" && <DashboardView />}
    </div>
  );
}

export default App;
