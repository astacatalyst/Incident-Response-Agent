import { useState } from "react";

const initial = {
  service: "",
  severity: "high",
  symptoms: "",
  deployment_version: "",
  logs: "",
  description: "",
};

export const EXAMPLE = {
  service: "payments-service",
  severity: "critical",
  symptoms: "checkout 5xx errors, p99 latency above 4s, DB connection timeouts",
  deployment_version: "v3.2.0",
  logs: "ERROR [payments-service] psycopg2.OperationalError: could not obtain connection from pool (timeout=30s)\nWARN pool size 20/20 in use, 148 waiting\nERROR POST /api/checkout 503 Service Unavailable",
  description: "Checkout failing for most users right after the v3.2.0 deploy during peak traffic.",
};

function IncidentInput({ onSubmit, isLoading, submitLabel = "Analyze incident", prefill = false }) {
  const [form, setForm] = useState(prefill ? EXAMPLE : initial);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const symptoms = form.symptoms.split(/[,\n]/).map((s) => s.trim()).filter(Boolean);
  const valid = form.service.trim() && form.logs.trim() && symptoms.length > 0;

  function submit() {
    onSubmit({
      service: form.service.trim(),
      severity: form.severity,
      symptoms,
      logs: form.logs,
      metrics: {},
      deployment_version: form.deployment_version.trim() || "unknown",
      description: form.description.trim() || symptoms.join("; "),
    });
  }

  return (
    <div className="card">
      <h2>New incident</h2>
      <div className="grid">
        <label>Service<input value={form.service} onChange={set("service")} placeholder="payments-service" /></label>
        <label>Severity
          <select value={form.severity} onChange={set("severity")}>
            <option value="low">low</option><option value="medium">medium</option>
            <option value="high">high</option><option value="critical">critical</option>
          </select>
        </label>
        <label>Deployment version<input value={form.deployment_version} onChange={set("deployment_version")} placeholder="v2.4.1" /></label>
        <label>Symptoms (comma separated)<input value={form.symptoms} onChange={set("symptoms")} placeholder="high latency, 5xx errors" /></label>
      </div>
      <label>Alert or error log
        <textarea rows={8} value={form.logs} onChange={set("logs")} placeholder="ERROR: connection timeout on payments-service..." />
      </label>
      <label>Description (optional)
        <textarea rows={2} value={form.description} onChange={set("description")} />
      </label>
      <button className="secondary" type="button" onClick={() => setForm(EXAMPLE)} disabled={isLoading}>
        Load example
      </button>{" "}
      <button onClick={submit} disabled={isLoading || !valid}>
        {isLoading ? "Analyzing..." : submitLabel}
      </button>
    </div>
  );
}

export default IncidentInput;
