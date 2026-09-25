"""
CIA Triad + Password Attack Lab  ---  Flask backend
=====================================================
An educational tool for a cybersecurity presentation.

It demonstrates:
  1. CIA TRIAD
       - Confidentiality : simple XOR cipher (encrypt / decrypt)
       - Integrity       : SHA-256 hashing + tamper detection
       - Availability    : a tiny rate-limit / DoS simulation
  2. DICTIONARY ATTACK  (against plaintext OR a hash)
  3. BRUTE-FORCE ATTACK (with a live progress bar via SSE)
  4. PASSWORD TOOLS     (strength checker, wordlist analysis, export)

Everything is intentionally small and readable so it can be explained
line-by-line during the demo.
"""

import hashlib
import itertools
import json
import time
import io
import csv

from flask import Flask, render_template, request, jsonify, Response, send_file

app = Flask(__name__)

WORDLIST_FILE = "wordlist.txt"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def load_wordlist():
    """Read the dictionary file into a list of words (one per line)."""
    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def make_hash(text, algo):
    """Hash `text` with the chosen algorithm (md5 / sha1 / sha256)."""
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


# ===========================================================================
# 1. CIA TRIAD
# ===========================================================================

# ---- Confidentiality : XOR cipher --------------------------------------
def xor_cipher(text, key):
    """
    XOR each character of `text` with a repeating `key`.
    XOR is reversible: running it twice with the same key gives the
    original text back. That is enough to explain 'confidentiality'.
    Output is hex so it is printable.
    """
    key = key or "key"
    out = []
    for i, ch in enumerate(text):
        out.append(ord(ch) ^ ord(key[i % len(key)]))
    return "".join(f"{b:02x}" for b in out)


def xor_decipher(hex_text, key):
    """Reverse of xor_cipher: hex -> bytes -> XOR back to plaintext."""
    key = key or "key"
    raw = bytes.fromhex(hex_text)
    out = []
    for i, b in enumerate(raw):
        out.append(chr(b ^ ord(key[i % len(key)])))
    return "".join(out)


@app.route("/api/confidentiality", methods=["POST"])
def confidentiality():
    data = request.get_json()
    text = data.get("text", "")
    key = data.get("key", "")
    action = data.get("action", "encrypt")

    if action == "encrypt":
        result = xor_cipher(text, key)
    else:
        try:
            result = xor_decipher(text, key)
        except ValueError:
            return jsonify({"error": "Input is not valid encrypted hex."}), 400
    return jsonify({"result": result})


# ---- Integrity : hashing + tamper check --------------------------------
@app.route("/api/integrity", methods=["POST"])
def integrity():
    """
    Compute a fingerprint (SHA-256) of a message.
    If the message changes by even one character the hash changes
    completely -> that is how tampering is detected.
    """
    data = request.get_json()
    message = data.get("message", "")
    original_hash = data.get("original_hash", "")

    current_hash = make_hash(message, "sha256")

    result = {"current_hash": current_hash}
    if original_hash:
        # We are re-checking a message against a hash we saw earlier.
        result["tampered"] = (current_hash != original_hash)
    return jsonify(result)


# ---- Availability : DoS / rate-limit simulation ------------------------
@app.route("/api/availability", methods=["POST"])
def availability():
    """
    Simulate a server that can only handle `capacity` requests.
    We fire `requests_sent` requests; anything over capacity is
    'dropped' -> the service becomes unavailable to those users.
    Turning on 'protection' (rate limiting) keeps it available.
    """
    data = request.get_json()
    requests_sent = int(data.get("requests", 100))
    capacity = int(data.get("capacity", 50))
    protection = bool(data.get("protection", False))

    if protection:
        # Rate limiting throttles the flood so legit traffic gets served.
        served = min(requests_sent, capacity)
        dropped = requests_sent - served
        status = "ONLINE (protected by rate limiting)"
    else:
        if requests_sent > capacity:
            served = 0            # overwhelmed -> full outage
            dropped = requests_sent
            status = "OFFLINE (server overwhelmed by DoS)"
        else:
            served = requests_sent
            dropped = 0
            status = "ONLINE"

    return jsonify({
        "served": served,
        "dropped": dropped,
        "capacity": capacity,
        "requests": requests_sent,
        "status": status,
    })


# ===========================================================================
# 2. DICTIONARY ATTACK   (streamed with Server-Sent Events for a progress bar)
# ===========================================================================
@app.route("/api/dictionary-attack")
def dictionary_attack():
    """
    Try every word in the wordlist against the target.
      mode = 'plain'  -> compare word == target
      mode = 'md5' / 'sha1' / 'sha256' -> compare hash(word) == target
    Streams progress events so the UI can show a live progress bar.
    """
    target = request.args.get("target", "").strip()
    mode = request.args.get("mode", "plain")

    def generate():
        words = load_wordlist()
        total = len(words)
        start = time.time()
        found = None

        for i, word in enumerate(words, start=1):
            candidate = word if mode == "plain" else make_hash(word, mode)
            if candidate == target:
                found = word

            # Send a progress update.
            yield sse({
                "type": "progress",
                "attempt": i,
                "total": total,
                "current": word,
                "percent": round(i / total * 100, 1),
            })
            time.sleep(0.02)   # slow it down so the bar is visible in the demo
            if found:
                break

        yield sse({
            "type": "done",
            "found": found,
            "attempts": i,
            "total": total,
            "elapsed": round(time.time() - start, 3),
        })

    return Response(generate(), mimetype="text/event-stream")


# ===========================================================================
# 3. BRUTE-FORCE ATTACK  (streamed, live progress bar)
# ===========================================================================
CHARSETS = {
    "digits": "0123456789",
    "lower": "abcdefghijklmnopqrstuvwxyz",
    "lower_digits": "abcdefghijklmnopqrstuvwxyz0123456789",
}


@app.route("/api/brute-force")
def brute_force():
    """
    Generate every combination of the chosen charset up to `maxlen`
    characters and test it against the target (plaintext or hash).
    This shows why long passwords matter: the search space explodes.
    """
    target = request.args.get("target", "").strip()
    mode = request.args.get("mode", "plain")
    maxlen = int(request.args.get("maxlen", 3))
    charset = CHARSETS.get(request.args.get("charset", "lower_digits"),
                           CHARSETS["lower_digits"])

    maxlen = min(maxlen, 5)   # safety cap so the demo stays responsive

    def generate():
        # Total combinations = n^1 + n^2 + ... + n^maxlen
        n = len(charset)
        total = sum(n ** L for L in range(1, maxlen + 1))
        start = time.time()
        attempt = 0
        found = None

        for length in range(1, maxlen + 1):
            for combo in itertools.product(charset, repeat=length):
                attempt += 1
                guess = "".join(combo)
                candidate = guess if mode == "plain" else make_hash(guess, mode)
                if candidate == target:
                    found = guess

                # Only emit every so often so we don't flood the browser.
                if found or attempt % 200 == 0:
                    yield sse({
                        "type": "progress",
                        "attempt": attempt,
                        "total": total,
                        "current": guess,
                        "percent": round(attempt / total * 100, 1),
                    })
                if found:
                    break
            if found:
                break

        yield sse({
            "type": "done",
            "found": found,
            "attempts": attempt,
            "total": total,
            "elapsed": round(time.time() - start, 3),
        })

    return Response(generate(), mimetype="text/event-stream")


# ===========================================================================
# 4. PASSWORD TOOLS
# ===========================================================================
def strength_of(pw):
    """
    Very simple strength score based on length + character variety.
    Returns (label, score 0-5, notes list).
    """
    score = 0
    notes = []

    if len(pw) >= 8:
        score += 1
    else:
        notes.append("Too short (use 8+ characters)")
    if len(pw) >= 12:
        score += 1
    if any(c.islower() for c in pw) and any(c.isupper() for c in pw):
        score += 1
    else:
        notes.append("Mix upper and lower case")
    if any(c.isdigit() for c in pw):
        score += 1
    else:
        notes.append("Add a number")
    if any(not c.isalnum() for c in pw):
        score += 1
    else:
        notes.append("Add a symbol")

    label = {0: "VERY WEAK", 1: "WEAK", 2: "WEAK",
             3: "MEDIUM", 4: "STRONG", 5: "VERY STRONG"}[score]
    return label, score, notes


@app.route("/api/strength", methods=["POST"])
def strength():
    pw = request.get_json().get("password", "")
    label, score, notes = strength_of(pw)
    return jsonify({"label": label, "score": score, "notes": notes})


@app.route("/api/analyze-wordlist", methods=["POST"])
def analyze_wordlist():
    """Categorise every word in the wordlist as weak / medium / strong."""
    words = load_wordlist()
    buckets = {"WEAK": [], "MEDIUM": [], "STRONG": []}
    detailed = []
    for w in words:
        label, score, _ = strength_of(w)
        group = "WEAK" if score <= 2 else ("MEDIUM" if score == 3 else "STRONG")
        buckets[group].append(w)
        detailed.append({"password": w, "label": label, "score": score,
                         "category": group})
    return jsonify({"buckets": buckets, "detailed": detailed})


@app.route("/api/export")
def export():
    """
    Export the wordlist analysis as .txt or .csv.
      /api/export?fmt=csv
      /api/export?fmt=txt
      /api/export?fmt=csv&category=WEAK   (only one category)
    """
    fmt = request.args.get("fmt", "txt")
    category = request.args.get("category", "").upper()

    words = load_wordlist()
    rows = []
    for w in words:
        label, score, _ = strength_of(w)
        group = "WEAK" if score <= 2 else ("MEDIUM" if score == 3 else "STRONG")
        if category and group != category:
            continue
        rows.append((w, label, score, group))

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["password", "label", "score", "category"])
        writer.writerows(rows)
        data = buf.getvalue().encode("utf-8")
        return send_file(io.BytesIO(data), mimetype="text/csv",
                         as_attachment=True, download_name="analysis.csv")
    else:
        lines = ["PASSWORD ANALYSIS REPORT", "=" * 40]
        for w, label, score, group in rows:
            lines.append(f"{w:<20} {label:<12} score={score} [{group}]")
        data = "\n".join(lines).encode("utf-8")
        return send_file(io.BytesIO(data), mimetype="text/plain",
                         as_attachment=True, download_name="analysis.txt")


# ===========================================================================
# 5. VIRUS SIMULATION  (100% safe -- no real files, no real malware)
# ===========================================================================
# A harmless marker string that stands in for a "malware signature".
# It is inspired by the EICAR idea but is our own invented text, so it can
# never trigger a real antivirus and does nothing at all.
VIRUS_SIGNATURE = "X5O!VIRUS-SIM-SAFE-SIGNATURE-DO-NOTHING"


@app.route("/api/virus/spread", methods=["POST"])
def virus_spread():
    """
    Simulate how an infection spreads through a set of imaginary files,
    tick by tick, and how an antivirus (defender) slows or stops it.

    Malware behaviours shown:
      - REPLICATION : each infected file infects `spread_rate` healthy files.
    Defender behaviours shown:
      - DETECTION   : each tick the antivirus quarantines a share of the
                      infected files (signature-based scan).
    Everything below is just arithmetic on counters -- nothing executes.
    """
    data = request.get_json()
    num_files = int(data.get("files", 20))
    spread_rate = int(data.get("spread_rate", 2))
    ticks = int(data.get("ticks", 8))
    antivirus = bool(data.get("antivirus", False))
    detection_rate = float(data.get("detection_rate", 0.5))

    infected = 1                      # patient zero
    healthy = max(num_files - 1, 0)
    quarantined = 0

    timeline = [{"tick": 0, "infected": infected,
                 "healthy": healthy, "quarantined": quarantined}]

    for t in range(1, ticks + 1):
        # --- malware replicates ---
        new_infections = min(healthy, infected * spread_rate)
        infected += new_infections
        healthy -= new_infections

        # --- defender responds ---
        if antivirus:
            caught = round(infected * detection_rate)
            infected -= caught
            quarantined += caught

        timeline.append({"tick": t, "infected": infected,
                         "healthy": healthy, "quarantined": quarantined})

        if infected <= 0:             # threat eliminated
            break

    return jsonify({
        "timeline": timeline,
        "contained": infected <= 0,
        "final_infected": infected,
        "total": num_files,
    })


@app.route("/api/virus/scan", methods=["POST"])
def virus_scan():
    """
    Signature-based detection demo: does the pasted 'file content' contain
    the known malware signature? This is exactly how simple antivirus
    engines flag known threats.
    """
    content = request.get_json().get("content", "")
    infected = VIRUS_SIGNATURE in content
    return jsonify({"infected": infected, "signature": VIRUS_SIGNATURE})


@app.route("/api/virus/sample")
def virus_sample():
    """Return a harmless 'infected' sample file so the scanner has something
    to detect during the demo."""
    sample = ("# report.txt\n"
              "Quarterly numbers look fine.\n"
              + VIRUS_SIGNATURE + "\n"
              "End of file.\n")
    return jsonify({"content": sample})


# ---------------------------------------------------------------------------
def sse(obj):
    """Format a dict as a Server-Sent Event line."""
    return f"data: {json.dumps(obj)}\n\n"


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # threaded=True lets the SSE streams run while the page stays responsive.
    app.run(debug=True, threaded=True, port=5000)
