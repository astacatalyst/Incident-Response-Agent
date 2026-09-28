function MemoryTimeline({ incidents }) {
  return (
    <div className="card">
      <h2>Memory: Similar Past Incidents</h2>
      {incidents.map((incident) => (
        <div className="memory-card" key={incident.id}>
          <strong>
            {incident.id} · {incident.service}
          </strong>
          <span className="badge">Recalled from {incident.date}</span>
          <p>Root cause: {incident.rootCause}</p>
          <p>Fix: {incident.resolution}</p>
          <p>Resolved in {incident.timeToResolve}</p>
        </div>
      ))}
    </div>
  );
}

export default MemoryTimeline;