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

      <p>Based on {response.recalledCount} similar past incidents.</p>
    </div>
  );
}

export default AgentResponse;