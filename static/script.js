/* ---------------------------------------------------------------
   Front-end logic. Talks to the Flask backend with fetch() and,
   for the live progress bars, with EventSource (Server-Sent Events).
   --------------------------------------------------------------- */

// ---------- QUESTION SWITCHING (Q3 / Q4 / Q5) ----------
document.querySelectorAll(".qtab").forEach(function (btn) {
  btn.addEventListener("click", function () {
    document.querySelectorAll(".qtab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".question").forEach(q => q.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.q).classList.add("active");
  });
});

// ---------- SUB-TAB SWITCHING (inside Q4) ----------
document.querySelectorAll(".tab").forEach(function (btn) {
  btn.addEventListener("click", function () {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// small helper: POST json and return json
async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

function setOut(id, text, cls) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "output" + (cls ? " " + cls : "");
}

// =========================================================
// CIA : CONFIDENTIALITY
// =========================================================
async function doCipher(action) {
  const textEl = document.getElementById("c-text");
  const text = textEl.value;
  const key = document.getElementById("c-key").value;

  if (action === "decrypt" && !/^[0-9a-fA-F]*$/.test(text.trim())) {
    return setOut("c-out",
      "To DECRYPT, the TEXT box must hold the ENCRYPTED hex\n" +
      "(the output of ENCRYPT), not the key or plain text.\n" +
      "Tip: press ENCRYPT first, then DECRYPT to reverse it.", "bad");
  }

  const data = await postJSON("/api/confidentiality", { text, key, action });
  if (data.error) return setOut("c-out", data.error, "bad");

  const verb = action === "encrypt" ? "ENCRYPTED" : "DECRYPTED";
  setOut("c-out", verb + ":\n" + data.result, "ok");
  // Put the result back in the TEXT box so encrypt <-> decrypt round-trips.
  textEl.value = data.result;
}

// =========================================================
// CIA : INTEGRITY
// =========================================================
async function hashMessage() {
  const message = document.getElementById("i-msg").value;
  const data = await postJSON("/api/integrity", { message });
  document.getElementById("i-saved").value = data.current_hash;  // "store" it
  setOut("i-out", "SHA-256 FINGERPRINT:\n" + data.current_hash +
    "\n\n(Saved above. Now edit the message and press VERIFY.)", "ok");
}

async function verifyMessage() {
  const message = document.getElementById("i-msg").value;
  const original_hash = document.getElementById("i-saved").value;
  if (!original_hash) return setOut("i-out", "Generate a hash first.", "bad");
  const data = await postJSON("/api/integrity", { message, original_hash });
  if (data.tampered) {
    setOut("i-out", "!! TAMPERING DETECTED !!\nHash no longer matches.\n\nNOW: " +
      data.current_hash, "bad");
  } else {
    setOut("i-out", "INTEGRITY OK - message unchanged.\n" + data.current_hash, "ok");
  }
}

// =========================================================
// CIA : AVAILABILITY
// =========================================================
async function testAvailability() {
  const requests = document.getElementById("a-req").value;
  const capacity = document.getElementById("a-cap").value;
  const protection = document.getElementById("a-prot").checked;
  const d = await postJSON("/api/availability", { requests, capacity, protection });
  const online = d.status.startsWith("ONLINE");
  setOut("a-out",
    "STATUS : " + d.status +
    "\nSERVED : " + d.served + " / " + d.requests +
    "\nDROPPED: " + d.dropped,
    online ? "ok" : "bad");
}

// =========================================================
// SHARED : run an SSE attack (dictionary or brute force)
// =========================================================
function runAttack(url, barId, outId) {
  const bar = document.getElementById(barId);
  const out = document.getElementById(outId);
  bar.style.width = "0%";
  out.className = "output";
  out.textContent = "ATTACKING...";

  const es = new EventSource(url);

  es.onmessage = function (e) {
    const d = JSON.parse(e.data);

    if (d.type === "progress") {
      bar.style.width = d.percent + "%";
      out.textContent =
        "TRYING : " + d.current +
        "\nATTEMPT: " + d.attempt + " / " + d.total +
        "\n" + d.percent + "%";
    }

    if (d.type === "done") {
      es.close();
      if (d.found !== null) {
        bar.style.width = "100%";
        out.className = "output ok";
        out.textContent =
          ">> PASSWORD CRACKED <<\n" +
          "FOUND    : " + d.found +
          "\nATTEMPTS : " + d.attempts +
          "\nTIME     : " + d.elapsed + "s";
      } else {
        out.className = "output bad";
        out.textContent =
          "NOT FOUND.\nSearched " + d.attempts + " of " + d.total +
          " combinations in " + d.elapsed + "s.";
      }
    }
  };

  es.onerror = function () { es.close(); };
}

function runDictionary() {
  const target = encodeURIComponent(document.getElementById("d-target").value);
  const mode = document.getElementById("d-mode").value;
  runAttack(`/api/dictionary-attack?target=${target}&mode=${mode}`, "d-bar", "d-out");
}

function runBrute() {
  const target = encodeURIComponent(document.getElementById("b-target").value);
  const mode = document.getElementById("b-mode").value;
  const charset = document.getElementById("b-charset").value;
  const maxlen = document.getElementById("b-maxlen").value;
  runAttack(
    `/api/brute-force?target=${target}&mode=${mode}&charset=${charset}&maxlen=${maxlen}`,
    "b-bar", "b-out");
}

// =========================================================
// PASSWORD TOOLS
// =========================================================
let strengthTimer = null;
function checkStrength() {
  clearTimeout(strengthTimer);
  strengthTimer = setTimeout(async function () {
    const password = document.getElementById("s-pw").value;
    if (!password) { setOut("s-out", ""); document.getElementById("s-meter").style.width = "0%"; return; }
    const d = await postJSON("/api/strength", { password });

    const meter = document.getElementById("s-meter");
    meter.style.width = (d.score / 5 * 100) + "%";
    // colour: red -> orange -> green
    meter.style.background = d.score <= 2 ? "#ff3b30" : (d.score === 3 ? "#ff9500" : "#00a86b");

    let txt = "STRENGTH: " + d.label + " (" + d.score + "/5)";
    if (d.notes.length) txt += "\n\nTIPS:\n- " + d.notes.join("\n- ");
    setOut("s-out", txt);
  }, 150);
}

// ---- passwords the user has explicitly added to their report ----
const analyzed = [];

function renderAnalyzed() {
  const el = document.getElementById("s-history");
  if (!analyzed.length) { el.textContent = "(no passwords added yet — press ADD TO REPORT)"; return; }
  el.textContent = "IN REPORT (" + analyzed.length + "):\n" +
    analyzed.map(a => a.password.padEnd(18) + " " + a.category + " (" + a.score + "/5)").join("\n");
}

async function addAnalyzed() {
  const pw = document.getElementById("s-pw").value;
  if (!pw) { setOut("s-history", "Type a password first, then ADD TO REPORT.", "bad"); return; }
  const d = await postJSON("/api/strength", { password: pw });
  const category = d.score <= 2 ? "WEAK" : (d.score === 3 ? "MEDIUM" : "STRONG");
  const rec = { password: pw, label: d.label, score: d.score, category: category };
  const i = analyzed.findIndex(a => a.password === pw);   // dedupe
  if (i >= 0) analyzed[i] = rec; else analyzed.push(rec);
  renderAnalyzed();
}

function clearAnalyzed() {
  analyzed.length = 0;
  renderAnalyzed();
}

function csvField(v) { return '"' + String(v).replace(/"/g, '""') + '"'; }

function exportAnalyzed(fmt) {
  if (!analyzed.length) {
    setOut("s-history", "Nothing to export yet. Add some passwords first.", "bad");
    return;
  }
  let content, mime, name;
  if (fmt === "csv") {
    content = "password,label,score,category\n" +
      analyzed.map(a => [a.password, a.label, a.score, a.category].map(csvField).join(",")).join("\n") + "\n";
    mime = "text/csv"; name = "analyzed_passwords.csv";
  } else {
    content = "ANALYZED PASSWORD REPORT\n" + "=".repeat(40) + "\n" +
      analyzed.map(a => a.password.padEnd(20) + " " + a.label.padEnd(12) +
        " score=" + a.score + " [" + a.category + "]").join("\n") + "\n";
    mime = "text/plain"; name = "analyzed_passwords.txt";
  }
  // build the file in the browser and trigger a download
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

async function analyzeWordlist() {
  const d = await postJSON("/api/analyze-wordlist", {});
  const b = d.buckets;
  let txt = "WORDLIST BREAKDOWN\n" +
    "WEAK   : " + b.WEAK.length + "\n" +
    "MEDIUM : " + b.MEDIUM.length + "\n" +
    "STRONG : " + b.STRONG.length + "\n\n" +
    "Use the export buttons to download the full report.";
  setOut("w-out", txt);
}

// =========================================================
// VIRUS SIMULATION (Q5)
// =========================================================
async function runVirusSpread() {
  const body = {
    files: document.getElementById("v-files").value,
    spread_rate: document.getElementById("v-rate").value,
    ticks: document.getElementById("v-ticks").value,
    antivirus: document.getElementById("v-av").checked,
    detection_rate: document.getElementById("v-det").value,
  };
  const d = await postJSON("/api/virus/spread", body);

  // Draw a simple text bar-chart of infected files per tick.
  let lines = ["TICK  INFECTED  (bar = infected files)"];
  d.timeline.forEach(function (row) {
    const bar = "#".repeat(row.infected);
    lines.push(
      String(row.tick).padStart(3, " ") + "   " +
      String(row.infected).padStart(4, " ") + "   " + bar);
  });
  lines.push("");
  lines.push(d.contained
    ? ">> CONTAINED: antivirus eliminated the threat."
    : ">> FINAL INFECTED: " + d.final_infected + " / " + d.total + " files.");

  setOut("v-out", lines.join("\n"), d.contained ? "ok" : "bad");
}

async function loadSample() {
  const res = await fetch("/api/virus/sample");
  const d = await res.json();
  document.getElementById("vs-content").value = d.content;
  setOut("vs-out", "Sample file loaded. Press SCAN FILE.");
}

async function scanContent() {
  const content = document.getElementById("vs-content").value;
  const d = await postJSON("/api/virus/scan", { content });
  if (d.infected) {
    setOut("vs-out", "!! THREAT DETECTED !!\nSignature found: " + d.signature +
      "\n\nACTION: quarantine the file.", "bad");
  } else {
    setOut("vs-out", "CLEAN - no known signature found.", "ok");
  }
}

// =========================================================
// Q9 : HASH + OBFUSCATION
// =========================================================
async function runHash() {
  const fileEl = document.getElementById("h-file");
  let res;
  if (fileEl.files.length) {
    const fd = new FormData();
    fd.append("file", fileEl.files[0]);
    res = await fetch("/api/hash", { method: "POST", body: fd });
  } else {
    res = await fetch("/api/hash", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: document.getElementById("h-text").value }),
    });
  }
  const d = await res.json();
  setOut("h-out",
    "SOURCE : " + d.source + "  (" + d.length + " bytes)\n\n" +
    "MD5    : " + d.hashes.md5 + "\n" +
    "SHA1   : " + d.hashes.sha1 + "\n" +
    "SHA256 : " + d.hashes.sha256 + "\n" +
    "SHA512 : " + d.hashes.sha512, "ok");
}

let lastObfuscated = "";
async function runObfuscate() {
  const code = document.getElementById("o-code").value;
  const d = await postJSON("/api/obfuscate", { code });
  lastObfuscated = d.obfuscated;
  setOut("o-out", "OBFUSCATED (logic hidden, but still runs):\n\n" + d.obfuscated);
}
async function runDeobfuscate() {
  if (!lastObfuscated) return setOut("o-out", "Press OBFUSCATE first.", "bad");
  const d = await postJSON("/api/deobfuscate", { obfuscated: lastObfuscated });
  if (d.error) return setOut("o-out", d.error, "bad");
  setOut("o-out", "RECOVERED ORIGINAL CODE:\n\n" + d.code, "ok");
}

// =========================================================
// Q10 : RSA SIGNATURES + JWT AUTH
// =========================================================
async function rsaSign() {
  const message = document.getElementById("r-msg").value;
  const d = await postJSON("/api/rsa/sign", { message });
  document.getElementById("r-sig").value = d.signature;
  setOut("r-out", "SIGNED with the PRIVATE key.\nSignature placed below.\n" +
    "Now press VERIFY — or edit the message first to watch it fail.", "ok");
}
async function rsaVerify() {
  const message = document.getElementById("r-msg").value;
  const signature = document.getElementById("r-sig").value;
  const d = await postJSON("/api/rsa/verify", { message, signature });
  if (d.valid) setOut("r-out", ">> VALID: signature matches the message.\nAuthentic and untampered.", "ok");
  else setOut("r-out", ">> INVALID: the message was changed or the signature is wrong.", "bad");
}

async function authLogin() {
  const username = document.getElementById("a-user").value;
  const password = document.getElementById("a-pass").value;
  const d = await postJSON("/api/auth/login", { username, password });
  if (d.error) { document.getElementById("a-token").value = ""; return setOut("auth-out", d.error, "bad"); }
  document.getElementById("a-token").value = d.token;
  setOut("auth-out", "LOGIN OK — role: " + d.role +
    "\nA signed JWT token was issued (below). Now call the protected APIs.", "ok");
}
async function authCall(kind) {
  const token = document.getElementById("a-token").value;
  const d = await postJSON("/api/auth/" + kind, { token });
  if (d.error) return setOut("auth-out", d.error, "bad");
  setOut("auth-out", d.message + "\n(role: " + d.role + ")", "ok");
}

// =========================================================
// Q11 : PII + ANONYMIZATION
// =========================================================
async function runPII() {
  const text = document.getElementById("p-text").value;
  const d = await postJSON("/api/pii/classify", { text });
  let txt = "DATA TYPE : " + d.structure +
    "\nPII FOUND : " + d.count +
    "\nDATA STATES: at-rest (stored) / in-transit (sent) / in-use (processed)\n\n";
  txt += d.found.length
    ? d.found.map(x => "  [" + x.type + "] " + x.value).join("\n")
    : "  (no PII detected)";
  setOut("p-out", txt);
}

async function runAnon() {
  const d = await postJSON("/api/anon/apply", {});
  const head = "NAME   AGE    G  PIN      DISEASE";
  const fmt = rows => rows.map(r =>
    ("" + r.name).padEnd(7) + ("" + r.age).padEnd(7) +
    ("" + r.gender).padEnd(3) + ("" + r.pincode).padEnd(9) + r.disease).join("\n");
  const txt =
    "ORIGINAL (identifiable):\n" + head + "\n" + fmt(d.original) +
    "\n\nANONYMIZED (generalised):\n" + head + "\n" + fmt(d.anonymized) +
    "\n\nMETRICS\n" +
    "  k-anonymity : " + d.k + "  (every record hides in a group of >= " + d.k + ")\n" +
    "  l-diversity : " + d.l + "  (distinct diseases per group)\n" +
    "  t-closeness : " + d.t + "  (0 = closest to overall, best)\n" +
    "  groups      : " + d.groups + "\n" +
    "  RE-ID RISK  : " + d.risk_before + "%  ->  " + d.risk_after + "%";
  setOut("an-out", txt, "ok");
}

async function runDP() {
  const disease = document.getElementById("dp-disease").value;
  const epsilon = document.getElementById("dp-eps").value;
  const d = await postJSON("/api/anon/dp", { disease, epsilon });
  setOut("dp-out",
    "Query: how many patients have " + d.disease + "?\n" +
    "  TRUE count  : " + d.true_count + "\n" +
    "  NOISY count : " + d.noisy_count + "   (epsilon = " + d.epsilon + ")\n\n" +
    "Smaller epsilon = more noise = more privacy.", "ok");
}

// =========================================================
// TASKBAR CLOCK (cosmetic)
// =========================================================
function tickClock() {
  const el = document.getElementById("clock");
  if (!el) return;
  const now = new Date();
  let h = now.getHours();
  const m = String(now.getMinutes()).padStart(2, "0");
  const ampm = h >= 12 ? "PM" : "AM";
  h = h % 12 || 12;
  el.textContent = h + ":" + m + " " + ampm;
}
tickClock();
setInterval(tickClock, 15000);

// show the empty-report placeholder on first load
if (document.getElementById("s-history")) renderAnalyzed();
