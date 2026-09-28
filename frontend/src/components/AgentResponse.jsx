import MemoryTimeline from "./MemoryTimeline";

function AgentResponse({ response }) {
  return (
    <div>
      <h2>Suggested Fix</h2>
      <p>{response.suggestion}</p>

      <h3>Steps</h3>
      <ol>
        {response.steps.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ol>

      <MemoryTimeline incidents={response.recalledIncidents} />
    </div>
  );
}

export default AgentResponse;