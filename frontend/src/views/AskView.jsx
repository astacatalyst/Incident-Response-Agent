import { useState } from "react";
import { askIncidents } from "../lib/api";
import { formatDate } from "../lib/format";

const EXAMPLES = [
  "What usually causes payment API timeouts?",
  "Which Redis incidents happened and how were they fixed?",
  "What lessons did we learn from database outages?",
];

function AskView() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(q = question) {
    if (q.trim().length < 3) return;
    setQuestion(q);
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await askIncidents(q.trim()));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const byId = Object.fromEntries((result?.sources || []).map((s) => [s.id, s]));

  return (
    <>
      <div className="card">
        <h2>Ask about past incidents</h2>
        <p className="muted">Ask in plain language. The answer cites the incident records it used.</p>
        <form onSubmit={(e) => { e.preventDefault(); ask(); }} className="ask-form">
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="e.g. Why do checkout deploys keep failing?" maxLength={500} />
          <button type="submit" disabled={loading || question.trim().length < 3}>{loading ? "Thinking…" : "Ask"}</button>
        </form>
        <div className="export-bar">
          {EXAMPLES.map((x) => <button key={x} type="button" className="chip-btn" onClick={() => ask(x)} disabled={loading}>{x}</button>)}
        </div>
      </div>
      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Searching incident records and memory…</div>}
      {result && (
        <div className="card memory-glow">
          <div className="row">
            <strong>Answer</strong>
            <span className="badge">{result.confidence} confidence</span>
            <span className="muted right">{result.sources.length} records searched · {result.memories_used || 0} memories</span>
          </div>
          <p>{result.answer}</p>
          {result.follow_up && <p className="muted">Next question to consider: {result.follow_up}</p>}
          {result.evidence?.length > 0 && <h3>Evidence</h3>}
          {result.evidence?.map((e, n) => {
            const s = byId[e.incident_id];
            return (
              <div key={n} className="memory-card">
                <div className="row">
                  <strong>#{e.incident_id}{s ? ` · ${s.service}` : ""}</strong>
                  {s && <span className={`badge sev-${s.severity}`}>{s.severity}</span>}
                  {s && <span className="muted right">{formatDate(s.created_at)}</span>}
                </div>
                <blockquote>“{e.quote}”</blockquote>
                <p className="muted">{e.why}</p>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}

export default AskView;
