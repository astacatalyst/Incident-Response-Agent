import { useState } from "react";
import IncidentInput from "./components/IncidentInput";
import AgentResponse from "./components/AgentResponse";
import { mockResponse } from "./mockdata";

function App() {
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  function handleSubmit(log) {
    console.log("Log received:", log);
    setResponse(null);
    setIsLoading(true);

    // Fake a 1.5 second delay, like a real API call
    setTimeout(() => {
      setResponse(mockResponse);
      setIsLoading(false);
    }, 1500);
  }

  return (
    <div className="app">
      <h1>Incident Response Agent</h1>
      <p className="subtitle">
        An on-call assistant that remembers every past incident.
      </p>

      <IncidentInput onSubmit={handleSubmit} isLoading={isLoading} />

      {isLoading && (
        <div className="loading">Searching memory for similar incidents...</div>
      )}

      {response && <AgentResponse response={response} />}
    </div>
  );
}

export default App;