const $ = id => document.getElementById(id);
const S = { locs: {}, tips: null, hosp: [], filter: "all", tab: "precautions",
  user: JSON.parse(localStorage.getItem("hg_user") || "null"), state: "Maharashtra", city: "Pune" };
const COL = { Low: "#1f8a5b", Moderate: "#c77700", High: "#d92d3f" };
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function api(url, body) {
  const r = await fetch(url, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || "Something went wrong.");
  return j;
}

function go(p) {
  if (p === "dashboard" && !S.user) p = "login";
  document.querySelectorAll(".page").forEach(e => e.classList.toggle("on", e.id === "p-" + p));
  const key = ["location", "form", "result"].includes(p) ? "location" : p === "login" ? "dashboard" : p;
  document.querySelectorAll("#nav button").forEach(b => b.classList.toggle("on", b.dataset.go === key));
  if (p === "tips") renderTips();
  if (p === "hospitals") loadHosp();
  if (p === "dashboard") loadDash();
  window.scrollTo(0, 0);
}
document.addEventListener("click", e => { const b = e.target.closest("[data-go]"); if (b) go(b.dataset.go); });

/* ---------- location selects ---------- */
function fillState(sel) { sel.innerHTML = Object.keys(S.locs).map(s => `<option>${esc(s)}</option>`).join(""); sel.value = S.state; }
function fillCity(sel) { sel.innerHTML = Object.keys(S.locs[S.state] ? S.locs[S.state] : {}).length ? S.locs[S.state].map(c => `<option>${esc(c)}</option>`).join("") : ""; if (S.locs[S.state].includes(S.city)) sel.value = S.city; else S.city = sel.value; }
function bindLoc(stEl, ctEl, after) {
  fillState(stEl); fillCity(ctEl);
  stEl.onchange = () => { S.state = stEl.value; S.city = S.locs[S.state][0]; fillCity(ctEl); after && after(); };
  ctEl.onchange = () => { S.city = ctEl.value; after && after(); };
}
$("toForm").onclick = () => go("form");

/* ---------- assessment ---------- */
const radio = n => document.querySelector(`input[name=${n}]:checked`).value === "1";
$("submit").onclick = async () => {
  $("err").textContent = "";
  if (!$("gender").value) { $("err").textContent = "Select your gender."; return; }
  const body = { age: $("age").value, gender: $("gender").value, sys: $("sys").value, dia: $("dia").value, chol: $("chol").value, hr: $("hr").value,
    smoking: radio("smoking"), diabetes: radio("diabetes"), family: radio("family"), chest: radio("chest") };
  try { showResult(await api("/api/risk", body)); } catch (e) { $("err").textContent = e.message; }
};

let actx, timer, muted = false;
function alarm() {
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)(); actx.resume();
    let n = 0; muted = false;
    (function pulse() {
      if (muted || n++ >= 8) return;
      [880, 660].forEach((f, i) => {
        const o = actx.createOscillator(), g = actx.createGain(), t = actx.currentTime + i * .25;
        o.type = "square"; o.frequency.value = f; g.gain.value = .12; o.connect(g); g.connect(actx.destination); o.start(t); o.stop(t + .2);
      });
      timer = setTimeout(pulse, 700);
    })();
  } catch (e) { /* audio unavailable */ }
}
$("playAlert").onclick = () => { muted = true; clearTimeout(timer); alarm(); };

function showResult(r) {
  const c = COL[r.level];
  $("banner").className = "banner " + r.level;
  $("rTitle").textContent = r.level + " Heart Attack Risk Estimate";
  $("rSub").textContent = { High: "Your inputs indicate a higher risk of heart attack.", Moderate: "Some of your numbers need attention.", Low: "Your inputs indicate a lower risk." }[r.level];
  $("ring").style.cssText = `--c:${c};--p:${r.score * 10}`;
  $("rScore").textContent = r.score + " / 10";
  $("rFactors").innerHTML = (r.factors.length ? r.factors : ["No major risk factors found"]).map(f => `<li>${esc(f)}</li>`).join("");
  $("rMeans").textContent = "This estimate is based on the information you provided and is not a diagnosis. Please consult a healthcare professional for a proper evaluation." +
    (r.level === "High" ? " If you have chest pain right now, call 108 immediately." : "");
  $("sos").style.display = $("playAlert").style.display = r.level === "High" ? "flex" : "none";
  go("result");
  if (r.level === "High") showEmergencySimulation();
}

/* ---------- tips ---------- */
function renderTips() {
  const t = S.tips, box = $("tipBody");
  if (!t) return;
  if (S.tab === "precautions") box.innerHTML = t.precautions.map(([a, b]) => `<div class="item"><b>${esc(a)}</b><span>${esc(b)}</span></div>`).join("") +
    `<div class="note"><b>Important</b><br>Do not start or intensify exercise based solely on this score. If you have symptoms like chest pain, shortness of breath or dizziness, seek immediate medical care.</div>`;
  else if (S.tab === "exercise") box.innerHTML = `<h3>Safe Exercise Recommendations</h3><div class="ex">` +
    t.exercise.map(([n, d, f, i]) => `<div><i>${i}</i><b>${esc(n)}</b><small>${esc(d)}</small><small>(${esc(f)})</small></div>`).join("") +
    `</div><div class="note"><b>Remember</b><ul>${t.exercise_rules.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div>`;
  else box.innerHTML = t.diet.map(([a, b]) => `<div class="item"><b>${esc(a)}</b><span>${esc(b)}</span></div>`).join("");
}
$("tipTabs").onclick = e => { const b = e.target.closest("button"); if (!b) return; S.tab = b.dataset.t; document.querySelectorAll("#tipTabs button").forEach(x => x.classList.toggle("on", x === b)); renderTips(); };

/* ---------- hospitals ---------- */
async function loadHosp() {
  S.hosp = await api(`/api/hospitals?state=${encodeURIComponent(S.state)}&city=${encodeURIComponent(S.city)}`);
  drawHosp();
}
function drawHosp() {
  const f = S.filter, list = S.hosp.filter(h => f === "all" || (f === "multi" && !h.heart) || (f === "gov" && h.gov) || (f === "pvt" && !h.gov));
  $("hList").innerHTML = list.length ? list.map(h => {
    const q = encodeURIComponent(`${h.name} ${S.city} ${S.state}`);
    return `<div class="hosp"><div><b>${esc(h.name)}</b><br><span>${h.heart ? "Cardiology institute" : "Multi-speciality"} · ${h.gov ? "Government" : "Private"} · ${esc(S.city)}, ${esc(S.state)}</span></div>
    <a target="_blank" rel="noopener" href="https://www.google.com/maps/search/${q}">View on Map</a></div>`;
  }).join("") : `<p class="mut">No hospitals in this filter for ${esc(S.city)}. Try another tab.</p>`;
}
$("hTabs").onclick = e => { const b = e.target.closest("button"); if (!b) return; S.filter = b.dataset.f; document.querySelectorAll("#hTabs button").forEach(x => x.classList.toggle("on", x === b)); drawHosp(); };

/* ---------- login + dashboard ---------- */
function paintUser() {
  $("who").textContent = S.user ? "Signed in as " + S.user.name : "";
  $("loginBtn").textContent = S.user ? "Log out" : "Login";
}
$("loginBtn").onclick = () => { if (S.user) { S.user = null; localStorage.removeItem("hg_user"); paintUser(); go("home"); } else go("login"); };
$("lGo").onclick = async () => {
  try {
    S.user = await api("/api/login", { name: $("lName").value, id: $("lId").value });
    localStorage.setItem("hg_user", JSON.stringify(S.user)); paintUser(); go("dashboard");
  } catch (e) { $("lErr").textContent = e.message; }
};
async function loadDash() {
  const h = new Date().getHours();
  $("dHi").textContent = `Good ${h < 12 ? "morning" : h < 17 ? "afternoon" : "evening"}, ${S.user.name}`;
  const rows = await api("/api/checkins/" + encodeURIComponent(S.user.id)), last = rows[rows.length - 1];
  $("dStats").innerHTML = last
    ? `<div><small>Resting Heart Rate</small><b>${last.hr} bpm</b></div><div><small>Blood Pressure</small><b>${last.sys}/${last.dia}</b></div><div><small>Steps · mood ${esc(last.mood)}</small><b>${last.steps}</b></div>`
    : `<div><b>No check-ins yet</b><small>Log your first one below.</small></div>`;
  const max = Math.max(1, ...rows.map(r => r.hr));
  $("dBars").innerHTML = rows.map(r => `<div style="height:${r.hr / max * 100}%" title="${r.date}"><span>${r.hr}</span></div>`).join("") || `<p class="mut">Your chart appears after your first check-in.</p>`;
}
$("cGo").onclick = async () => {
  $("cErr").textContent = "";
  try {
    await api("/api/checkin", { id: S.user.id, hr: $("ch").value, sys: $("cs").value, dia: $("cd").value, steps: $("cst").value, mood: $("cm").value });
    loadDash();
  } catch (e) { $("cErr").textContent = e.message; }
};

/* ---------- start ---------- */
(async () => {
  [S.locs, S.tips] = await Promise.all([api("/api/locations"), api("/api/tips")]);
  bindLoc($("state"), $("city"));
  bindLoc($("hState"), $("hCity"), loadHosp);
  paintUser(); go("home");
})();

/* ---------- Emergency SOS simulation (demo only: never places a real call) ---------- */
let sosTimer, sosSteps = [];
const getContact = () => { try { return JSON.parse(localStorage.getItem("hg_contact") || "null"); } catch (e) { return null; } };
function sosClear() { clearInterval(sosTimer); sosSteps.forEach(clearTimeout); sosSteps = []; }
function closeSOS() { sosClear(); muted = true; clearTimeout(timer); $("sosModal").classList.remove("show"); }

function showEmergencySimulation() {
  sosClear();
  let sec = 10;
  $("sosModal").classList.add("show");
  $("sosBody").innerHTML = `<p class="sos-ico">&#9888;&#65039;</p><h2 id="sosTitle">HIGH RISK DETECTED</h2>
   <p>Your entered health values indicate a potentially elevated cardiovascular risk. This tool is not a medical diagnosis. If you have chest pain, breathing difficulty, fainting or sweating, seek immediate medical care.</p>
   <p class="sos-count">Emergency support will be activated in <b id="sosSec">10</b> seconds</p>
   <button class="sos-cancel" id="sosCancel">Cancel Alert</button><a class="sos-call" href="tel:112">Call 112 Now</a>
   <p class="sos-demo">DEMO MODE: this prototype never places a real emergency call.</p>`;
  $("sosCancel").onclick = cancelSOS;
  $("sosCancel").focus();
  alarm();
  sosTimer = setInterval(() => { sec--; $("sosSec").textContent = sec; if (sec <= 0) { sosClear(); runSimulation(); } }, 1000);
}

function cancelSOS() {
  sosClear(); muted = true; clearTimeout(timer);
  $("sosBody").innerHTML = `<p class="sos-ico">&#9995;</p><h2 id="sosTitle">Alert Cancelled</h2>
   <p>The emergency simulation was stopped. If this is a real emergency, call 112 immediately.</p>
   <button class="sos-cancel" id="sosClose">Close</button><a class="sos-call" href="tel:112">Call 112 Now</a>`;
  $("sosClose").onclick = closeSOS; $("sosClose").focus();
}

function runSimulation() {
  muted = true; clearTimeout(timer);
  const c = getContact(), who = S.user ? S.user.name : "the user", loc = `${S.city}, ${S.state}`;
  const lines = [
    ["Dialling Emergency Service 112 (simulated)", 1],
    ["Call connected: emergency operator (simulated)", 1],
    [`Location sharing completed: ${loc} (simulated)`, 1],
    c ? [`Trusted contact notified: ${c.name}, ${c.phone} (simulated)`, 1] : ["No trusted contact saved. Add one on the Emergency page.", 0],
  ];
  $("sosBody").innerHTML = `<p class="sos-ico">&#128222;</p><h2 id="sosTitle">Simulated Emergency Call</h2>
   <p class="sos-demo big">DEMO MODE: No real emergency call was made.</p><ul class="sos-log" id="sosLog"></ul><div id="sosEnd"></div>`;
  lines.forEach(([t, ok], i) => sosSteps.push(setTimeout(() =>
    $("sosLog").insertAdjacentHTML("beforeend", `<li>${ok ? "&#10003;" : "&ndash;"} ${esc(t)}</li>`), (i + 1) * 1200)));
  sosSteps.push(setTimeout(() => {
    $("sosBody").querySelector("h2").textContent = "Emergency Alert Simulated";
    $("sosBody").querySelector(".sos-ico").innerHTML = "&#10003;";
    $("sosEnd").innerHTML = (c ? `<div class="sos-msg"><b>Demo message to ${esc(c.name)} (${esc(c.rel)}):</b><br>"HeartGuard detected a high-risk assessment for ${esc(who)}. Please contact them immediately."</div>` : "") +
      `<button class="sos-cancel" id="sosDone">Close Demo</button><a class="sos-call" href="tel:112">Call 112 Now</a>`;
    $("sosDone").onclick = closeSOS; $("sosDone").focus();
  }, (lines.length + 1) * 1200));
}
$("sosAgain").onclick = showEmergencySimulation;
document.addEventListener("keydown", e => { if (e.key === "Escape" && $("sosModal").classList.contains("show")) closeSOS(); });

/* trusted contact (kept in this browser only) */
(() => { const c = getContact(); if (c) { $("tcName").value = c.name; $("tcPhone").value = c.phone; $("tcRel").value = c.rel; } })();
$("tcSave").onclick = () => {
  const name = $("tcName").value.trim(), phone = $("tcPhone").value.trim().replace(/[\s-]/g, "");
  if (!name || !/^(\+91)?[6-9]\d{9}$/.test(phone)) { $("tcMsg").textContent = "Enter a name and a valid 10-digit Indian mobile number."; return; }
  localStorage.setItem("hg_contact", JSON.stringify({ name, phone: $("tcPhone").value.trim(), rel: $("tcRel").value }));
  $("tcMsg").textContent = "Saved on this device. Demo only: no SMS or call is ever sent.";
};
