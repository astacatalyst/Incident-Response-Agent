function MemoryTimeline({ incidents }) {
  return (
    <div>
      <h2>Memory: Similar Past Incidents</h2>
      {incidents.map((incident) => (
        <div
          key={incident.id}
          style={{
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "10px",
          }}
        >
          <strong>
            {incident.id} · {incident.service}
          </strong>
          <p>Recalled from {incident.date}</p>
          <p>Root cause: {incident.rootCause}</p>
          <p>Fix: {incident.resolution}</p>
          <p>Resolved in {incident.timeToResolve}</p>
        </div>
      ))}
    </div>
  );
}

export default MemoryTimeline;