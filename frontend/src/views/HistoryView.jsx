import { useEffect, useState } from "react";
import { listIncidents } from "../lib/api";
import ResolveForm from "../components/ResolveForm";
import { formatDate } from "../lib/format";
import { exportPostmortems } from "../lib/postmortem";

function HistoryView() {
  const [filters, setFilters] = useState({ service: "", severity: "", status: "", page: 1 });
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(null);
  const [exporting, setExporting] = useState(false);

  async function exportAll(format) {
    setExporting(true);
    setError("");
    try {
      const all = [];
      for (let page = 1; ; page++) {
        const d = await listIncidents({ ...filters, status: "resolved", page, page_size: 100 });
        all.push(...d.items);
        if (page >= (d.pages || 1)) break;
      }
      if (!exportPostmortems(all, format)) setError("No resolved incidents match these filters.");
    } catch (e) {
      setError(e.message);
    } finally {
      setExporting(false);
    }
  }

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    const t = setTimeout(() => {
      listIncidents({ ...filters, page_size: 20 })
        .then((d) => !cancelled && setData(d))
        .catch((e) => !cancelled && setError(e.message))
        .finally(() => !cancelled && setLoading(false));
    }, 250);
    return () => { cancelled = true; clearTimeout(t); };
  }, [filters]);

  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value, page: 1 });

  return (
    <>
      <div className="card">
        <h2>Incident history</h2>
        <div className="grid">
          <label>Service<input value={filters.service} onChange={set("service")} placeholder="any" /></label>
          <label>Severity
            <select value={filters.severity} onChange={set("severity")}>
              <option value="">any</option><option>low</option><option>medium</option><option>high</option><option>critical</option>
            </select>
          </label>
          <label>Status
            <select value={filters.status} onChange={set("status")}>
              <option value="">any</option><option>open</option><option>resolved</option>
            </select>
          </label>
        </div>
        <div className="export-bar">
          <span className="muted">Export resolved incidents matching these filters as postmortem reports:</span>
          <button disabled={exporting} onClick={() => exportAll("pdf")}>{exporting ? "Preparing…" : "PDF"}</button>
          <button disabled={exporting} onClick={() => exportAll("html")}>HTML</button>
          <button disabled={exporting} onClick={() => exportAll("md")}>Markdown</button>
        </div>
      </div>
      {error && <div className="error">{error}</div>}
      {loading && !data && <div className="loading">Loading incidents...</div>}
      {data && (
        <div className="card">
          <p className="muted">{data.total} incidents{loading ? " · refreshing…" : ""}</p>
          {data.items.length === 0 && <p>No incidents match these filters.</p>}
          {data.items.map((i) => (
            <div key={i.id} className="memory-card">
              <button className="row" onClick={() => setOpen(open === i.id ? null : i.id)}>
                <strong>#{i.id} · {i.service}</strong>
                <span className={`badge sev-${i.severity}`}>{i.severity}</span>
                <span className="badge">{i.status}</span>
                {i.is_synthetic && <span className="badge">seed</span>}
                <span className="muted right">{formatDate(i.created_at)}</span>
              </button>
              <p>{i.description}</p>
              {open === i.id && (
                <div>
                  <p><strong>Symptoms:</strong> {i.symptoms.join(", ")}</p>
                  <p><strong>Version:</strong> {i.deployment_version}</p>
                  {i.status === "resolved" ? (
                    <>
                      <p><strong>Root cause:</strong> {i.root_cause}</p>
                      <p><strong>Resolution:</strong> {i.resolution}</p>
                      <p><strong>Outcome:</strong> {i.successful ? "worked" : "did not work"} · {i.resolution_time_minutes} min</p>
                      <p><strong>Lessons:</strong> {i.lessons_learned}</p>
                      <div className="export-bar">
                        <span className="muted">Postmortem report:</span>
                        <button onClick={() => exportPostmortems([i], "pdf")}>PDF</button>
                        <button onClick={() => exportPostmortems([i], "html")}>HTML</button>
                        <button onClick={() => exportPostmortems([i], "md")}>Markdown</button>
                      </div>
                    </>
                  ) : (
                    <ResolveForm incident={i} />
                  )}
                  <pre className="logs">{i.logs}</pre>
                </div>
              )}
            </div>
          ))}
          {data.pages > 1 && (
            <div className="pager">
              <button disabled={filters.page <= 1} onClick={() => setFilters({ ...filters, page: filters.page - 1 })}>Previous</button>
              <span className="muted">Page {data.page} of {data.pages}</span>
              <button disabled={filters.page >= data.pages} onClick={() => setFilters({ ...filters, page: filters.page + 1 })}>Next</button>
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default HistoryView;
