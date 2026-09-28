import { useState } from "react";

function IncidentInput({ onSubmit }) {
  const [log, setLog] = useState("");

  function handleSubmit() {
    onSubmit(log);
  }

  return (
    <div>
      <h2>Paste your alert or error log</h2>
      <textarea
        rows={8}
        cols={60}
        placeholder="e.g. ERROR: connection timeout on payments-service..."
        value={log}
        onChange={(e) => setLog(e.target.value)}
      />
      <br />
      <button onClick={handleSubmit}>Get Suggestion</button>
    </div>
  );
}

export default IncidentInput;