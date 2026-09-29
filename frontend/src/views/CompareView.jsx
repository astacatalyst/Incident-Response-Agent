import { useEffect, useState } from "react";
import IncidentInput from "../components/IncidentInput";
import AgentResponse from "../components/AgentResponse";
import { analyzeIncident, analyzeWithoutMemory, listIncidents } from "../lib/api";
import { scoreAnalysis } from "../lib/score";

function toPayload(i) {
  return {
    service: i.service,
    severity: i.severity,
    symptoms: i.symptoms?.length ? i.symptoms : [i.description],
    logs: i.logs || i.description,
    metrics: i.metrics || {},
    deployment_version: i.deployment_version || "unknown",
    description: i.description,
  };
}

function ScoreCard({ label, score, tone }) {
  return (
    <div className={`score-card ${tone}`}>
      <div className="muted">{label}</div>
      <div className="score-big">{score.total}<small>/100</small></div>
      {score.parts.map((p) => (
        <div key={p.label} className="score-row">
          <span>{p.label}</span>
          <div className="score-bar"><div style={{ width: `${(p.value / p.max) * 100}%` }} /></div>
          <span className="muted">{p.value}/{p.max}</span>
        </div>
      ))}
    </div>
  );
}

function CompareView() {
  const [mode, setMode] = useState("real");
  const [past, setPast] = useState([]);
  const [pickId, setPickId] = useState("");
  const [state, setState] = useState({ loading: false, error: "", before: null, after: null, source: null });

  useEffect(() => {
    listIncidents({ status: "resolved", page_size: 100 })
      .then((d) => {
        setPast(d.items);
        if (d.items[0]) setPickId(String(d.items[0].id));
      })
      .catch(() => setMode("custom"));
  }, []);

  async function run(payload, source = null) {
    setState({ loading: true, error: "", before: null, after: null, source });
    const [before, after] = await Promise.allSettled([
      analyzeWithoutMemory(payload),
      analyzeIncident(payload, source?.id),
    ]);
    setState({
      loading: false,
      source,
      error: [before, after].filter((r) => r.status === "rejected").map((r) => r.reason.message).join(" · "),
      before: before.value || null,
      after: after.value || null,
    });
  }

  const picked = past.find((i) => String(i.id) === pickId);
  const truth = state.source?.root_cause;
  const sBefore = state.before && scoreAnalysis(state.before, truth);
  const sAfter = state.after && scoreAnalysis(state.after, truth);
  const delta = sBefore && sAfter ? sAfter.total - sBefore.total : null;

  return (
    <>
      <div className="card intro">
        <h2>Same incident, two answers</h2>
        <p className="muted">
          Replay a real past incident through the agent twice, once with memory off and once with experience recalled
          from Hindsight, and see how much the score changes. That incident's own memory is hidden, so the agent can't just look up the answer.
        </p>
        <div className="export-bar">
          <button className={mode === "real" ? "tab active" : "tab"} onClick={() => setMode("real")} disabled={!past.length}>Replay a real incident</button>
          <button className={mode === "custom" ? "tab active" : "tab"} onClick={() => setMode("custom")}>Write your own</button>
        </div>
      </div>

      {mode === "real" && past.length > 0 && (
        <div className="card">
          <label>Past resolved incident
            <select value={pickId} onChange={(e) => setPickId(e.target.value)}>
              {past.map((i) => <option key={i.id} value={i.id}>#{i.id} · {i.service} · {i.severity} · {i.description.slice(0, 70)}</option>)}
            </select>
          </label>
          {picked && (
            <p className="muted">Symptoms: {picked.symptoms?.join(", ")} · The real root cause stays hidden from the agent and is only used for scoring.</p>
          )}
          <button disabled={!picked || state.loading} onClick={() => run(toPayload(picked), picked)}>
            {state.loading ? "Running both…" : "Compare answers"}
          </button>
        </div>
      )}
      {mode === "custom" && <IncidentInput onSubmit={(p) => run(p)} isLoading={state.loading} submitLabel="Compare answers" prefill />}

      {state.loading && <div className="loading">Running both analyses...</div>}
      {state.error && <div className="error">{state.error}</div>}

      {sBefore && sAfter && (
        <div className="card memory-glow">
          <div className="score-head">
            <h2>Score difference</h2>
            <div className={`score-delta ${delta > 0 ? "up" : delta < 0 ? "down" : ""}`}>
              {delta > 0 ? "+" : ""}{delta} points with memory
            </div>
          </div>
          {truth && <p className="muted"><strong>Real root cause:</strong> {truth}</p>}
          <div className="compare">
            <ScoreCard label="Without memory" score={sBefore} tone="before" />
            <ScoreCard label="With recalled experience" score={sAfter} tone="after" />
          </div>
          {truth && (
            <p className="muted">
              Match with the real root cause: {Math.round((sBefore.match || 0) * 100)}% without memory → {Math.round((sAfter.match || 0) * 100)}% with memory.
            </p>
          )}
        </div>
      )}

      {(state.before || state.after) && (
        <div className="compare">
          <div>
            <h2 className="col-title before">Without memory</h2>
            {state.before ? <AgentResponse result={state.before} hideMemory /> : <p className="muted">Failed</p>}
          </div>
          <div>
            <h2 className="col-title after">With recalled experience</h2>
            {state.after ? <AgentResponse result={state.after} /> : <p className="muted">Failed</p>}
          </div>
        </div>
      )}
    </>
  );
}

export default CompareView;
