// Scores one analysis out of 100 so the with/without-memory answers can be compared.
const STOP = new Set("the a an of to in on for and or is was were with after before by from due that this into at as be".split(" "));
const words = (t) => new Set(String(t || "").toLowerCase().match(/[a-z0-9]{3,}/g)?.filter((w) => !STOP.has(w)) || []);

export function rootCauseMatch(predicted, actual) {
  const a = words(actual);
  if (!a.size) return null;
  const p = words(predicted);
  let hit = 0;
  a.forEach((w) => p.has(w) && hit++);
  return hit / a.size;
}

export function scoreAnalysis(result, actualRootCause) {
  const a = result?.analysis || {};
  const conf = { low: 5, medium: 15, high: 25 }[a.confidence] ?? 0;
  const recalled = Math.min(result?.memory?.memories_retrieved || 0, 5) * 3;
  const similar = Math.min(a.similar_incidents?.length || 0, 3) * 5;
  const actions = Math.min(a.recommended_actions?.length || 0, 5) * 2;
  const match = rootCauseMatch(a.likely_root_cause, actualRootCause);
  const parts = [
    { label: "Confidence", value: conf, max: 25 },
    { label: "Memories recalled", value: recalled, max: 15 },
    { label: "Similar incidents cited", value: similar, max: 15 },
    { label: "Concrete actions", value: actions, max: 10 },
  ];
  if (match != null) parts.push({ label: "Matches the real root cause", value: Math.round(match * 35), max: 35 });
  const max = parts.reduce((s, p) => s + p.max, 0);
  const total = Math.round((parts.reduce((s, p) => s + p.value, 0) / max) * 100);
  return { total, parts, match };
}
