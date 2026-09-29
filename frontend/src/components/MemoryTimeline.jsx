function MemoryTimeline({ memory, similar }) {
  return (
    <div className="card">
      <h2>Memory: recalled from Hindsight</h2>
      <p className="muted">
        Status: {memory.status} · {memory.memories_retrieved} memories retrieved
        {memory.error && ` · ${memory.error}`}
      </p>
      {!memory.memory_used && <p>No relevant past incidents yet — this analysis is generic.</p>}

      {similar.map((s) => (
        <div className="memory-card" key={s.incident_id}>
          <strong>Similar incident {s.incident_id}</strong>
          <p>{s.reason}</p>
        </div>
      ))}

      {memory.memories.map((m, i) => (
        <div className="memory-card" key={m.id || i}>
          {m.type && <span className="badge">{m.type}</span>}
          <p>{m.content}</p>
        </div>
      ))}
    </div>
  );
}

export default MemoryTimeline;
