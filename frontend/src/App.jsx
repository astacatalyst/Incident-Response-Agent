import "./states.css";
import { useEffect, useState } from "react";
import IncidentInput from "./components/IncidentInput";
import AgentResponse from "./components/AgentResponse";
import ResolveForm from "./components/ResolveForm";
import { analyzeIncident, getHealth } from "./lib/api";

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: "offline" }));
  }, []);

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
    <div className="app">
      <h1>Incident Response Agent</h1>
      <p className="subtitle">An on-call assistant that remembers every past incident.</p>
      {health && (
        <p className={`status status-${health.status}`}>
          Backend: {health.status}
          {health.hindsight && ` · Memory: ${health.hindsight} · LLM: ${health.llm}`}
        </p>
      )}

      <IncidentInput onSubmit={handleSubmit} isLoading={isLoading} />

      {isLoading && <div className="loading">Searching memory for similar incidents...</div>}
      {error && <div className="error">{error}</div>}

      {result && (
        <>
          <AgentResponse result={result} />
          <ResolveForm incident={result.incident} />
        </>
      )}
    </div>
  );
}

export default App;
