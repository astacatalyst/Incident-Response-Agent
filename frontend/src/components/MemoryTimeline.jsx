import { formatDate, memoryDate, memoryIncidentId } from "../lib/format";

function preview(content) {
  try {
    const j = JSON.parse(content);
    return [
      j.service && `Service: ${j.service}`,
      j.root_cause && `Root cause: ${j.root_cause}`,
      j.resolution && `Fix: ${j.resolution}`,
      j.resolution_time_minutes != null && `Resolved in ${j.resolution_time_minutes} min`,
      j.lessons_learned && `Lesson: ${j.lessons_learned}`,
    ].filter(Boolean);
  } catch {
    return [content];
  }
}

function MemoryTimeline({ memory, similar }) {
  return (
    <div className="card memory-panel">
      <h2>Memory: recalled from Hindsight</h2>
      <p className="muted">
        Status: {memory.status} · {memory.memories_retrieved} memories retrieved
        {memory.error && ` · ${memory.error}`}
      </p>
      {!memory.memory_used && <p>No relevant past incidents yet — this analysis is generic.</p>}

      {similar.length > 0 && (
        <>
          <h3>Incidents the agent relied on</h3>
          {similar.map((s) => (
            <div className="memory-card" key={s.incident_id}>
              <strong>Incident {s.incident_id}</strong>
              <p>{s.reason}</p>
            </div>
          ))}
        </>
      )}

      {memory.memories.length > 0 && <h3>Raw recalled memories</h3>}
      {memory.memories.map((m, i) => {
        const id = memoryIncidentId(m);
        const date = memoryDate(m);
        const scores = Object.entries(m.scores || {}).filter(([, v]) => v != null);
        return (
          <div className="memory-card" key={m.id || i}>
            <div className="row-static">
              <strong>{id ? `Incident #${id}` : `Memory ${i + 1}`}</strong>
              {m.type && <span className="badge">{m.type}</span>}
              {date && <span className="badge">Recalled from {formatDate(date)}</span>}
            </div>
            {scores.length > 0 && (
              <div className="scores">
                {scores.map(([k, v]) => (
                  <span key={k} className="score">
                    {k.replace(/_/g, " ")}: {typeof v === "number" ? v.toFixed(3) : v}
                  </span>
                ))}
              </div>
            )}
            {preview(m.content).map((line, j) => <p key={j}>{line}</p>)}
          </div>
        );
      })}
    </div>
  );
}

export default MemoryTimeline;
