import { useState } from "react";
import { resolveIncident } from "../lib/api";

function ResolveForm({ incident }) {
  const [form, setForm] = useState({
    root_cause: "",
    resolution: "",
    successful: true,
    resolution_time_minutes: 15,
    lessons_learned: "",
  });
  const [state, setState] = useState({ loading: false, error: "", result: null });
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const valid = form.root_cause.trim() && form.resolution.trim() && form.lessons_learned.trim();

  async function submit() {
    setState({ loading: true, error: "", result: null });
    try {
      const result = await resolveIncident(incident.id, {
        ...form,
        resolution_time_minutes: Number(form.resolution_time_minutes) || 0,
      });
      setState({ loading: false, error: "", result });
    } catch (e) {
      setState({ loading: false, error: e.message, result: null });
    }
  }

  const r = state.result;
  if (r) {
    return (
      <div className={r.memory_stored ? "card success" : "card error"}>
        <h2>Incident #{incident.id} resolved</h2>
        {r.memory_stored
          ? <p>Saved to Hindsight memory. The next similar incident will use this fix.</p>
          : <p>Saved locally, but storing it in memory failed ({r.memory_status}{r.memory_error ? `: ${r.memory_error}` : ""}).</p>}
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Resolve and teach the agent</h2>
      <label>Actual root cause<textarea rows={2} value={form.root_cause} onChange={set("root_cause")} /></label>
      <label>What fixed it<textarea rows={2} value={form.resolution} onChange={set("resolution")} /></label>
      <label>Lessons learned<textarea rows={2} value={form.lessons_learned} onChange={set("lessons_learned")} /></label>
      <div className="grid">
        <label>Minutes to resolve
          <input type="number" min="0" value={form.resolution_time_minutes} onChange={set("resolution_time_minutes")} />
        </label>
        <label>Did the fix work?
          <select value={form.successful ? "yes" : "no"} onChange={(e) => setForm({ ...form, successful: e.target.value === "yes" })}>
            <option value="yes">Yes</option><option value="no">No</option>
          </select>
        </label>
      </div>
      {state.error && <div className="error">{state.error}</div>}
      <button onClick={submit} disabled={state.loading || !valid}>
        {state.loading ? "Saving to memory..." : "Resolve incident"}
      </button>
    </div>
  );
}

export default ResolveForm;
