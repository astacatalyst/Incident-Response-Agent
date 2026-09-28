import { useState } from "react";
import IncidentInput from "./components/IncidentInput";
import AgentResponse from "./components/AgentResponse";
import { mockResponse } from "./mockdata";

function App() {
  const [response, setResponse] = useState(null);

  function handleSubmit(log) {
    console.log("Log received:", log);
    setResponse(mockResponse);
  }

  return (
    <div>
      <h1>Incident Response Agent</h1>
      <IncidentInput onSubmit={handleSubmit} />
      {response && <AgentResponse response={response} />}
    </div>
  );
}

export default App;