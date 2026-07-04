"use strict";

const state = { sessionId: null, odd: [] };

const $ = (id) => document.getElementById(id);

// ---------- Rendu Markdown minimal ----------
function mdToHtml(md) {
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const lines = (md || "").split("\n");
  let html = "", inList = false;
  const closeList = () => { if (inList) { html += "</ul>"; inList = false; } };
  for (let raw of lines) {
    let line = raw.trimEnd();
    if (/^#{3}\s+/.test(line)) { closeList(); html += `<h3>${inline(line.replace(/^#{3}\s+/, ""))}</h3>`; }
    else if (/^#{2}\s+/.test(line)) { closeList(); html += `<h2>${inline(line.replace(/^#{2}\s+/, ""))}</h2>`; }
    else if (/^#\s+/.test(line)) { closeList(); html += `<h2>${inline(line.replace(/^#\s+/, ""))}</h2>`; }
    else if (/^\s*[-*]\s+/.test(line)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inline(line.replace(/^\s*[-*]\s+/, ""))}</li>`; }
    else if (line.trim() === "") { closeList(); }
    else { closeList(); html += `<p>${inline(line)}</p>`; }
  }
  closeList();
  function inline(s) {
    return esc(s)
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  }
  return html;
}

// ---------- Diagramme radar (toile d'araignée) 17 ODD ----------
function radarSVG(odd, scores) {
  const size = 260, cx = size / 2, cy = size / 2, R = size / 2 - 34, n = odd.length;
  const angle = (i) => (Math.PI * 2 * i) / n - Math.PI / 2;
  const pt = (i, r) => [cx + r * Math.cos(angle(i)), cy + r * Math.sin(angle(i))];
  let grid = "";
  [0.25, 0.5, 0.75, 1].forEach((f) => {
    const p = odd.map((_, i) => pt(i, R * f).map((v) => v.toFixed(1)).join(",")).join(" ");
    grid += `<polygon points="${p}" fill="none" stroke="#dddde3" stroke-width="1"/>`;
  });
  let axes = "", labels = "";
  odd.forEach((o, i) => {
    const [x, y] = pt(i, R);
    axes += `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#eee" stroke-width="1"/>`;
    const [lx, ly] = pt(i, R + 14);
    const anchor = Math.cos(angle(i)) > 0.2 ? "start" : Math.cos(angle(i)) < -0.2 ? "end" : "middle";
    labels += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" font-size="7" fill="#666" text-anchor="${anchor}" dominant-baseline="middle">${o.id}. ${o.short}</text>`;
  });
  const poly = odd.map((o, i) => pt(i, R * ((scores[o.id] ?? 50) / 100)).map((v) => v.toFixed(1)).join(",")).join(" ");
  return `<svg viewBox="0 0 ${size} ${size}" width="100%" role="img">
    ${grid}${axes}
    <polygon points="${poly}" fill="rgba(0,0,145,0.25)" stroke="#000091" stroke-width="2"/>
    ${labels}
  </svg>`;
}

// ---------- Messages ----------
function addMsg(text, cls) {
  const div = document.createElement("div");
  div.className = `msg ${cls}`;
  div.innerHTML = cls === "user" ? text.replace(/</g, "&lt;") : mdToHtml(text);
  $("messages").appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
}

// ---------- Flux de cadrage ----------
async function start() {
  $("demarrer").disabled = true;
  const r = await fetch("/api/start", { method: "POST" });
  const d = await r.json();
  state.sessionId = d.session_id;
  addMsg(d.greeting, "bot");
  askQuestion(d.question, d.step, d.total);
  $("demarrer-zone").hidden = true;
  $("saisie").hidden = false;
  $("input").focus();
}

function askQuestion(q, step, total) {
  $("progress").textContent = `Question ${step} / ${total}`;
  addMsg(q, "bot");
}

async function sendAnswer() {
  const val = $("input").value.trim();
  if (!val) return;
  addMsg(val, "user");
  $("input").value = "";
  $("envoyer").disabled = true;

  const r = await fetch("/api/answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: state.sessionId, answer: val }),
  });
  const d = await r.json();
  $("envoyer").disabled = false;

  if (!d.done) {
    askQuestion(d.question, d.step, d.total);
    $("input").focus();
  } else {
    $("saisie").hidden = true;
    addMsg("**Reformulation de votre intention :**\n\n" + d.comprehension, "bot");
    addMsg(d.message, "info");
    runAnalysis();
  }
}

// ---------- Pipeline (SSE) ----------
function runAnalysis() {
  $("pipeline").hidden = false;
  const es = new EventSource(`/api/analyze?session_id=${state.sessionId}`);
  es.onmessage = (ev) => {
    const d = JSON.parse(ev.data);
    if (d.step === "final") {
      renderRadars(d.odd, d.odd_scores, d.scenarios);
      renderDocument(d.synthese);
      es.close();
    } else if (d.step === "error") {
      addMsg("⚠️ Erreur pendant l'analyse : " + d.message, "info");
      es.close();
    } else {
      addStep(d.step, d.label, d.content);
    }
  };
  es.onerror = () => es.close();
}

function addStep(step, label, content) {
  const li = document.createElement("li");
  li.innerHTML = `<div class="etape-titre"><span class="puce">${step}</span>${label}</div>
    <div class="etape-contenu">${mdToHtml(content)}</div>`;
  $("etapes").appendChild(li);
  li.scrollIntoView({ behavior: "smooth", block: "end" });
}

function renderRadars(odd, scores, scenarios) {
  state.odd = odd;
  const grid = $("radars-grid");
  grid.innerHTML = "";
  (scenarios || []).forEach((s) => {
    const sc = scores[s.type] || {};
    const card = document.createElement("div");
    card.className = "radar-carte";
    card.innerHTML = `<h3>${s.titre || s.type}</h3>${radarSVG(odd, sc)}`;
    grid.appendChild(card);
  });
  $("radars").hidden = false;
}

function renderDocument(md) {
  $("synthese-contenu").innerHTML = mdToHtml(md);
  $("document").hidden = false;
}

// ---------- Init ----------
(async function init() {
  try {
    const cfg = await (await fetch("/api/config")).json();
    $("provider").textContent = cfg.provider;
    state.odd = cfg.odd;
  } catch (_) { $("provider").textContent = "?"; }
})();

$("demarrer").addEventListener("click", start);
$("envoyer").addEventListener("click", sendAnswer);
$("input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); sendAnswer(); }
});
$("imprimer").addEventListener("click", () => window.print());
