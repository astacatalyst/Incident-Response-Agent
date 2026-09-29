import MemoryTimeline from "./MemoryTimeline";

function AgentResponse({ result }) {
  const { analysis, memory, incident } = result;
  return (
    <div>
      <div className="card">
        <h2>Analysis · Incident #{incident.id}</h2>
        <p>{analysis.summary}</p>
        <h3>Likely root cause <span className="badge">confidence: {analysis.confidence}</span></h3>
        <p>{analysis.likely_root_cause}</p>

        {analysis.recommended_actions.length > 0 && (
          <>
            <h3>Recommended actions</h3>
            <ol>
              {analysis.recommended_actions.map((a, i) => (
                <li key={i}><strong>{a.step}</strong> — {a.reason}</li>
              ))}
            </ol>
          </>
        )}
        {analysis.evidence.length > 0 && (
          <><h3>Evidence</h3><ul>{analysis.evidence.map((e, i) => <li key={i}>{e}</li>)}</ul></>
        )}
        {analysis.memory_insights.length > 0 && (
          <><h3>What memory taught the agent</h3><ul>{analysis.memory_insights.map((e, i) => <li key={i}>{e}</li>)}</ul></>
        )}
        {analysis.uncertainties.length > 0 && (
          <><h3>Uncertainties</h3><ul>{analysis.uncertainties.map((e, i) => <li key={i}>{e}</li>)}</ul></>
        )}
      </div>

      <MemoryTimeline memory={memory} similar={analysis.similar_incidents} />
    </div>
  );
}

export default AgentResponse;
