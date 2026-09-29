import "./states.css";
import "./polish.css";
import { useEffect, useState } from "react";
import RespondView from "./views/RespondView";
import CompareView from "./views/CompareView";
import HistoryView from "./views/HistoryView";
import DashboardView from "./views/DashboardView";
import AskView from "./views/AskView";
import { getHealth, getMemoryDashboard } from "./lib/api";

const TABS = [
  ["compare", "Before / After demo"],
  ["respond", "Respond to incident"],
  ["history", "Incident history"],
  ["memory", "Memory dashboard"],
  ["ask", "Ask past incidents"],
];

function App() {
  const [tab, setTab] = useState("compare");
  const [health, setHealth] = useState(null);

  const [summary, setSummary] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: "offline" }));
    getMemoryDashboard().then(setSummary).catch(() => {});
  }, []);

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1 className="brand"><span className="brand-mark">◆</span>IncidentIQ</h1>
          <p className="subtitle">The on-call agent that remembers how your team fixed every past incident.</p>
        </div>
        {health && (
          <span className="pill">
            <span className={`dot ${health.status === "ok" ? "ok" : health.status === "offline" ? "bad" : ""}`} />
            {health.status === "offline" ? "Backend offline" : `API ${health.status} · memory ${health.hindsight} · LLM ${health.llm}`}
          </span>
        )}
      </header>
      {summary && (
        <div className="strip">
          <div className="stat"><div className="stat-value">{summary.incident_count}</div><div className="muted">incidents on record</div></div>
          <div className="stat"><div className="stat-value">{summary.resolved_incident_count}</div><div className="muted">resolutions learned</div></div>
          <div className="stat"><div className="stat-value">{summary.services.length}</div><div className="muted">services covered</div></div>
          <div className="stat"><div className="stat-value">{summary.recurring_root_causes[0]?.count ?? 0}×</div><div className="muted">top recurring cause</div></div>
        </div>
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
      {tab === "ask" && <AskView />}
    </div>
  );
}

export default App;
