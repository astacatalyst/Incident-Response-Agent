import { useState } from "react";
import IncidentInput from "../components/IncidentInput";
import AgentResponse from "../components/AgentResponse";
import { analyzeIncident, analyzeWithoutMemory } from "../lib/api";

function CompareView() {
  const [state, setState] = useState({ loading: false, error: "", before: null, after: null });

  async function run(payload) {
    setState({ loading: true, error: "", before: null, after: null });
    const [before, after] = await Promise.allSettled([
      analyzeWithoutMemory(payload),
      analyzeIncident(payload),
    ]);
    setState({
      loading: false,
      error: [before, after].filter((r) => r.status === "rejected").map((r) => r.reason.message).join(" · "),
      before: before.value || null,
      after: after.value || null,
    });
  }

  return (
    <>
      <div className="card intro">
        <h2>Same incident, two answers</h2>
        <p className="muted">
          One incident goes to the agent twice: once with memory switched off, and once with experience
          recalled from Hindsight. A payments outage resembling past incidents is already filled in — press “Compare answers”.
        </p>
      </div>
      <IncidentInput onSubmit={run} isLoading={state.loading} submitLabel="Compare answers" prefill />
      {state.loading && <div className="loading">Running both analyses...</div>}
      {state.error && <div className="error">{state.error}</div>}
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
