const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error(
      "Could not reach the backend. It may be waking up (free hosting sleeps) — try again in ~30 seconds."
    );
  }
  const data = await res.json().catch(() => null);
  if (!res.ok && !(res.status === 502 && data?.incident)) {
    const d = data?.detail;
    const msg =
      typeof d === "string" ? d
      : d?.message ? d.message
      : Array.isArray(d) ? d.map((e) => `${e.loc?.slice(-1)[0]}: ${e.msg}`).join("; ")
      : `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const analyzeIncident = (payload, excludeId) =>
  request(`/api/incidents/analyze${excludeId ? `?exclude_incident_id=${excludeId}` : ""}`, { method: "POST", body: JSON.stringify(payload) });

export const resolveIncident = (id, payload) =>
  request(`/api/incidents/${id}/resolve`, { method: "POST", body: JSON.stringify(payload) });

export const getHealth = () => request("/health");

export const analyzeWithoutMemory = (payload) =>
  request("/api/incidents/analyze?use_memory=false", { method: "POST", body: JSON.stringify(payload) });

export const listIncidents = (params = {}) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null));
  return request(`/api/incidents?${q}`);
};

export const getMemoryDashboard = () => request("/api/memory");

export const askIncidents = (question) =>
  request("/api/incidents/ask", { method: "POST", body: JSON.stringify({ question }) });
