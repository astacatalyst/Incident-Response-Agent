import { useState } from "react";

const initial = {
  service: "",
  severity: "high",
  symptoms: "",
  deployment_version: "",
  logs: "",
  description: "",
};

function IncidentInput({ onSubmit, isLoading }) {
  const [form, setForm] = useState(initial);
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
      <button onClick={submit} disabled={isLoading || !valid}>
        {isLoading ? "Analyzing..." : "Analyze incident"}
      </button>
    </div>
  );
}

export default IncidentInput;
