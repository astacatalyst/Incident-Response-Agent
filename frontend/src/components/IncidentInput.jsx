import { useState } from "react";

function IncidentInput({ onSubmit, isLoading }) {
  const [log, setLog] = useState("");

  return (
    <div className="card">
      <h2>Paste your alert or error log</h2>
      <textarea
        rows={8}
        placeholder="e.g. ERROR: connection timeout on payments-service..."
        value={log}
        onChange={(e) => setLog(e.target.value)}
      />
      <br />
      <button
        onClick={() => onSubmit(log)}
        disabled={isLoading || log.trim() === ""}
      >
        {isLoading ? "Analyzing..." : "Get Suggestion"}
      </button>
    </div>
  );
}

export default IncidentInput;