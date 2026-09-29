import { useEffect, useState } from "react";
import { getMemoryDashboard } from "../lib/api";
import { formatDate } from "../lib/format";

function Stat({ label, value }) {
  return <div className="stat"><div className="stat-value">{value}</div><div className="muted">{label}</div></div>;
}

function DashboardView() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  function load() {
    setError("");
    getMemoryDashboard().then(setData).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  if (error) return <div className="error">{error} <button onClick={load}>Retry</button></div>;
  if (!data) return <div className="loading">Loading memory dashboard...</div>;

  const stats = data.hindsight_stats || {};
  const maxCount = Math.max(1, ...data.recurring_root_causes.map((r) => r.count));

  return (
    <>
      <div className="stats">
        <Stat label="Incidents" value={data.incident_count} />
        <Stat label="Resolved" value={data.resolved_incident_count} />
        <Stat label="Fixes that worked" value={data.successful_resolutions} />
        <Stat label="Fixes that failed" value={data.unsuccessful_resolutions} />
      </div>

      <div className="card">
        <h2>Memory bank <span className="badge">{data.hindsight_status}</span></h2>
        {Object.keys(stats).length === 0 ? (
          <p className="muted">No memory-bank statistics available.</p>
        ) : (
          <div className="stats">
            {Object.entries(stats)
              .filter(([, v]) => typeof v !== "object" || v === null)
              .map(([k, v]) => <Stat key={k} label={k.replace(/_/g, " ")} value={String(v)} />)}
          </div>
        )}
        {Object.entries(stats).filter(([, v]) => v && typeof v === "object").map(([k, v]) => (
          <details key={k}><summary>{k.replace(/_/g, " ")}</summary><pre className="logs">{JSON.stringify(v, null, 2)}</pre></details>
        ))}
      </div>

      <div className="card">
        <h2>Recurring root causes</h2>
        {data.recurring_root_causes.length === 0 && <p className="muted">None yet.</p>}
        {data.recurring_root_causes.map((r) => (
          <div key={r.root_cause} className="bar-row">
            <div className="bar-label">{r.root_cause}</div>
            <div className="bar"><div className="bar-fill" style={{ width: `${(r.count / maxCount) * 100}%` }} /></div>
            <div className="muted">{r.count}×</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h2>Recently learned</h2>
        {data.recent_resolved.map((i) => (
          <div key={i.id} className="memory-card">
            <strong>#{i.id} · {i.service}</strong>{" "}
            <span className="badge">{i.successful ? "fix worked" : "fix failed"}</span>
            <span className="muted"> {formatDate(i.resolved_at)}</span>
            <p>Root cause: {i.root_cause}</p>
            <p>Lesson: {i.lessons_learned}</p>
          </div>
        ))}
        <p className="muted">Services covered: {data.services.join(", ") || "none"}</p>
      </div>
    </>
  );
}

export default DashboardView;
