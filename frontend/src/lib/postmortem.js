// Builds polished, self-contained postmortem reports for resolved incidents.

const esc = (v) =>
  String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const fmt = (v) => {
  if (!v) return "—";
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? String(v) : d.toLocaleString();
};

const duration = (m) => {
  if (m == null || m === "") return "—";
  const n = Number(m);
  return n >= 60 ? `${Math.floor(n / 60)}h ${n % 60}m` : `${n} min`;
};

const lessonsList = (text) =>
  String(text || "")
    .split(/\n|(?:^|\s)[-•]\s|;\s/)
    .map((s) => s.trim())
    .filter(Boolean);

function section(i) {
  const ok = i.successful;
  const lessons = lessonsList(i.lessons_learned);
  return `
<article class="pm">
  <header>
    <div class="eyebrow">Postmortem · Incident #${esc(i.id)}</div>
    <h1>${esc(i.service)} — ${esc(i.title || i.description?.slice(0, 90) || "Incident")}</h1>
    <div class="chips">
      <span class="chip sev-${esc(i.severity)}">${esc(i.severity)} severity</span>
      <span class="chip ${ok ? "ok" : "bad"}">${ok ? "Resolved successfully" : "Fix did not hold"}</span>
      ${i.deployment_version ? `<span class="chip">version ${esc(i.deployment_version)}</span>` : ""}
    </div>
  </header>
  <dl class="facts">
    <div><dt>Detected</dt><dd>${esc(fmt(i.created_at))}</dd></div>
    <div><dt>Resolved</dt><dd>${esc(fmt(i.resolved_at))}</dd></div>
    <div><dt>Time to resolve</dt><dd>${esc(duration(i.resolution_time_minutes))}</dd></div>
    <div><dt>Service</dt><dd>${esc(i.service)}</dd></div>
  </dl>
  <h2>Summary</h2><p>${esc(i.description)}</p>
  ${i.symptoms?.length ? `<h2>Symptoms</h2><ul>${i.symptoms.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>` : ""}
  <h2>Root cause</h2><p class="callout">${esc(i.root_cause || "Not recorded")}</p>
  <h2>Resolution</h2><p>${esc(i.resolution || "Not recorded")}</p>
  <h2>Outcome</h2><p>${ok ? "The fix restored service" : "The fix did not fully restore service"} after ${esc(duration(i.resolution_time_minutes))}.</p>
  <h2>Lessons learned</h2>
  ${lessons.length ? `<ol>${lessons.map((l) => `<li>${esc(l)}</li>`).join("")}</ol>` : "<p>None recorded.</p>"}
  ${i.logs ? `<h2>Log excerpt</h2><pre>${esc(String(i.logs).slice(0, 2500))}</pre>` : ""}
  <footer>Stored in IncidentIQ memory · recalled automatically for similar future incidents</footer>
</article>`;
}

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;600&family=JetBrains+Mono&display=swap');
*{box-sizing:border-box}body{margin:0;background:#eef1f6;color:#0f1a2e;font:15px/1.6 'IBM Plex Sans',sans-serif}
.toolbar{position:sticky;top:0;background:#0b1220;color:#e6ecf5;padding:12px 24px;display:flex;justify-content:space-between;align-items:center}
.toolbar button{background:#f5a524;border:0;border-radius:6px;padding:8px 14px;font-weight:600;cursor:pointer}
.pm{background:#fff;max-width:820px;margin:28px auto;padding:48px 56px;border-radius:10px;box-shadow:0 2px 14px rgba(15,26,46,.08);page-break-after:always}
.eyebrow{font:500 12px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:#7c5cff}
h1{font:700 26px/1.25 'Space Grotesk',sans-serif;margin:6px 0 14px}
h2{font:700 15px 'Space Grotesk',sans-serif;text-transform:uppercase;letter-spacing:.05em;color:#43506a;margin:28px 0 6px;border-bottom:1px solid #e3e8f0;padding-bottom:4px}
.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{font-size:12px;padding:3px 10px;border-radius:99px;background:#eef1f6;text-transform:capitalize}
.chip.ok{background:#dcf5e6;color:#11653a}.chip.bad{background:#fde2e2;color:#9b1c1c}
.sev-critical{background:#fde2e2;color:#9b1c1c}.sev-high{background:#fdebd3;color:#8a4b00}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0 0;padding:16px;background:#f6f8fb;border-radius:8px}
.facts dt{font-size:11px;text-transform:uppercase;color:#6b7891}.facts dd{margin:2px 0 0;font-weight:600;font-size:13px}
.callout{border-left:4px solid #7c5cff;background:#f4f1ff;padding:10px 14px;border-radius:0 6px 6px 0}
pre{font:12px/1.5 'JetBrains Mono',monospace;background:#0b1220;color:#cfe3ff;padding:14px;border-radius:6px;white-space:pre-wrap;overflow:hidden}
footer{margin-top:32px;font-size:12px;color:#6b7891;border-top:1px solid #e3e8f0;padding-top:10px}
@media print{body{background:#fff}.toolbar{display:none}.pm{box-shadow:none;margin:0 auto;padding:24px 8px}}`;

export function postmortemHtml(incidents) {
  const title = incidents.length === 1 ? `Postmortem — Incident #${incidents[0].id}` : `Postmortems — ${incidents.length} incidents`;
  return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>${CSS}</style></head>
<body><div class="toolbar"><strong>IncidentIQ · ${esc(title)}</strong><button onclick="window.print()">Save as PDF</button></div>
${incidents.map(section).join("")}</body></html>`;
}

export function postmortemMarkdown(incidents) {
  return incidents
    .map((i) => {
      const lessons = lessonsList(i.lessons_learned);
      return [
        `# Postmortem — Incident #${i.id}: ${i.service}`,
        `**Severity:** ${i.severity} · **Outcome:** ${i.successful ? "resolved successfully" : "fix did not hold"} · **Time to resolve:** ${duration(i.resolution_time_minutes)}`,
        `**Detected:** ${fmt(i.created_at)} · **Resolved:** ${fmt(i.resolved_at)}${i.deployment_version ? ` · **Version:** ${i.deployment_version}` : ""}`,
        `## Summary\n${i.description}`,
        i.symptoms?.length ? `## Symptoms\n${i.symptoms.map((s) => `- ${s}`).join("\n")}` : "",
        `## Root cause\n${i.root_cause || "Not recorded"}`,
        `## Resolution\n${i.resolution || "Not recorded"}`,
        `## Lessons learned\n${lessons.length ? lessons.map((l, n) => `${n + 1}. ${l}`).join("\n") : "None recorded."}`,
      ].filter(Boolean).join("\n\n");
    })
    .join("\n\n---\n\n");
}

function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function exportPostmortems(incidents, format = "html") {
  const resolved = incidents.filter((i) => i.status === "resolved");
  if (!resolved.length) return 0;
  const base = resolved.length === 1 ? `postmortem-incident-${resolved[0].id}` : `postmortems-${new Date().toISOString().slice(0, 10)}`;
  if (format === "md") download(`${base}.md`, postmortemMarkdown(resolved), "text/markdown");
  else if (format === "pdf") {
    const w = window.open("", "_blank");
    if (!w) return download(`${base}.html`, postmortemHtml(resolved), "text/html"), resolved.length;
    w.document.write(postmortemHtml(resolved));
    w.document.close();
    setTimeout(() => w.print(), 600);
  } else download(`${base}.html`, postmortemHtml(resolved), "text/html");
  return resolved.length;
}
