export function formatDate(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  const days = Math.round((Date.now() - d.getTime()) / 86400000);
  const rel = days <= 0 ? "today" : days === 1 ? "yesterday" : days < 60 ? `${days} days ago` : `${Math.round(days / 30)} months ago`;
  return `${d.toLocaleDateString()} (${rel})`;
}

const DATE_KEYS = ["occurred_start", "occurred_at", "mentioned_at", "created_at", "timestamp", "date", "resolved_at"];

export function memoryDate(m) {
  for (const k of DATE_KEYS) {
    if (m[k]) return m[k];
    if (m.metadata?.[k]) return m.metadata[k];
  }
  return null;
}

export function memoryIncidentId(m) {
  if (m.metadata?.incident_id) return m.metadata.incident_id;
  try {
    return JSON.parse(m.content)?.incident_id ?? null;
  } catch {
    return m.content.match(/incident[_ ]id["']?\s*[:=]\s*"?(\w+)/i)?.[1] ?? null;
  }
}
