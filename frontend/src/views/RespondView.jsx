import { useState } from "react";
import IncidentInput from "../components/IncidentInput";
import AgentResponse from "../components/AgentResponse";
import ResolveForm from "../components/ResolveForm";
import { analyzeIncident } from "../lib/api";

function RespondView() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(payload) {
    setResult(null);
    setError("");
    setIsLoading(true);
    try {
      setResult(await analyzeIncident(payload));
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <IncidentInput onSubmit={handleSubmit} isLoading={isLoading} />
      {isLoading && <div className="loading">Searching memory for similar incidents...</div>}
      {error && <div className="error">{error}</div>}
      {result && (
        <>
          <AgentResponse result={result} />
          <ResolveForm key={result.incident.id} incident={result.incident} />
        </>
      )}
    </>
  );
}

export default RespondView;
