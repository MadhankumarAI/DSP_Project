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
import base64
import hmac
import re
import math
import random
from collections import Counter

from flask import Flask, render_template, request, jsonify, Response, send_file

# RSA digital signatures (Q10) -- from the 'cryptography' library
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

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


# ===========================================================================
# 6. HASH FUNCTIONS & OBFUSCATION  (Q9)
# ===========================================================================
@app.route("/api/hash", methods=["POST"])
def api_hash():
    """
    Hash a STRING or an uploaded FILE with several algorithms at once
    (MD5, SHA1, SHA256, SHA512) so the differences are visible side by side.
    """
    if request.files.get("file") and request.files["file"].filename:
        f = request.files["file"]
        data = f.read()
        source = "file: " + f.filename
        length = len(data)
    else:
        text = request.form.get("text")
        if text is None:
            text = (request.get_json(silent=True) or {}).get("text", "")
        data = text.encode("utf-8")
        source = "text"
        length = len(text)

    def H(algo):
        h = hashlib.new(algo)
        h.update(data)
        return h.hexdigest()

    return jsonify({
        "source": source,
        "length": length,
        "hashes": {"md5": H("md5"), "sha1": H("sha1"),
                   "sha256": H("sha256"), "sha512": H("sha512")},
    })


@app.route("/api/obfuscate", methods=["POST"])
def obfuscate():
    """
    Simple obfuscation: Base64-encode the source code and wrap it in an
    exec() call. The logic is hidden (unreadable) but the one-liner still
    runs exactly the same. This is reversible -- see /api/deobfuscate.
    """
    code = request.get_json().get("code", "")
    b64 = base64.b64encode(code.encode("utf-8")).decode()
    obf = 'import base64\nexec(base64.b64decode("%s").decode())' % b64
    return jsonify({"obfuscated": obf, "b64": b64})


@app.route("/api/deobfuscate", methods=["POST"])
def deobfuscate():
    """Reverse the obfuscation above -> recover the original readable code."""
    obf = request.get_json().get("obfuscated", "")
    m = re.search(r'b64decode\("([^"]+)"\)', obf)
    payload = m.group(1) if m else obf.strip()
    try:
        return jsonify({"code": base64.b64decode(payload).decode("utf-8")})
    except Exception:
        return jsonify({"error": "Could not decode the obfuscated payload."}), 400


# ===========================================================================
# 7. DIGITAL SIGNATURES (RSA) + AUTH/AUTHORIZATION (JWT)  (Q10)
# ===========================================================================
# One RSA key pair is generated when the server starts.
_rsa_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_rsa_public = _rsa_private.public_key()
_PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                   salt_length=padding.PSS.MAX_LENGTH)


@app.route("/api/rsa/keys")
def rsa_keys():
    pem = _rsa_public.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    return jsonify({"public_key": pem})


@app.route("/api/rsa/sign", methods=["POST"])
def rsa_sign():
    """Sign a message with the PRIVATE key -> produces a signature."""
    msg = request.get_json().get("message", "").encode("utf-8")
    sig = _rsa_private.sign(msg, _PSS, hashes.SHA256())
    return jsonify({"signature": base64.b64encode(sig).decode()})


@app.route("/api/rsa/verify", methods=["POST"])
def rsa_verify():
    """Verify a signature with the PUBLIC key. If the message was changed,
    verification fails -> proves authenticity + integrity."""
    d = request.get_json()
    msg = d.get("message", "").encode("utf-8")
    try:
        sig = base64.b64decode(d.get("signature", ""))
        _rsa_public.verify(sig, msg, _PSS, hashes.SHA256())
        return jsonify({"valid": True})
    except Exception:
        return jsonify({"valid": False})


# ---- minimal JWT (HS256) implemented by hand, so it can be explained -----
JWT_SECRET = "demo-secret-key-change-me"
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user":  {"password": "user123",  "role": "user"},
}


def _b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def jwt_encode(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    seg = [_b64url(json.dumps(header).encode()),
           _b64url(json.dumps(payload).encode())]
    signing_input = ".".join(seg).encode()
    sig = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    seg.append(_b64url(sig))
    return ".".join(seg)


def jwt_decode(token):
    try:
        h, p, s = token.split(".")
        signing_input = (h + "." + p).encode()
        expected = _b64url(hmac.new(JWT_SECRET.encode(), signing_input,
                                    hashlib.sha256).digest())
        if not hmac.compare_digest(expected, s):
            return None, "invalid signature (token tampered)"
        payload = json.loads(base64.urlsafe_b64decode(p + "=="))
        if payload.get("exp", 0) < time.time():
            return None, "token expired"
        return payload, None
    except Exception:
        return None, "malformed token"


def _bearer_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return (request.get_json(silent=True) or {}).get("token", "")


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    d = request.get_json()
    user = USERS.get(d.get("username", ""))
    if not user or user["password"] != d.get("password", ""):
        return jsonify({"error": "Invalid username or password"}), 401
    token = jwt_encode({"sub": d["username"], "role": user["role"],
                        "exp": int(time.time()) + 300})   # valid 5 minutes
    return jsonify({"token": token, "role": user["role"]})


@app.route("/api/auth/protected", methods=["POST"])
def auth_protected():
    payload, err = jwt_decode(_bearer_token())
    if err:
        return jsonify({"error": "Access denied: " + err}), 401
    return jsonify({"message": "Welcome, " + payload["sub"] +
                    "! You reached a protected resource.",
                    "role": payload["role"]})


@app.route("/api/auth/admin", methods=["POST"])
def auth_admin():
    payload, err = jwt_decode(_bearer_token())
    if err:
        return jsonify({"error": "Access denied: " + err}), 401
    if payload.get("role") != "admin":
        return jsonify({"error": "Forbidden: admin role required "
                        "(you are '" + payload.get("role", "?") + "')"}), 403
    return jsonify({"message": "ADMIN AREA unlocked: sensitive settings.",
                    "role": payload["role"]})


# ===========================================================================
# 8. PII CLASSIFICATION + ANONYMIZATION  (Q11)
# ===========================================================================
# Order = priority. Earlier patterns claim their characters first, so an
# overlapping later pattern (e.g. Aadhaar over a +91 phone) is skipped.
PII_PATTERNS = [
    ("Email",          r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    ("PAN",            r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    ("SSN",            r"\b\d{3}-\d{2}-\d{4}\b"),
    ("Date of Birth",  r"\b\d{2}[/-]\d{2}[/-]\d{4}\b"),
    ("IP Address",     r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ("Phone (India)",  r"(?:\+91[-\s]?)?[6-9]\d{9}"),
    ("Aadhaar",        r"\d{4}\s\d{4}\s\d{4}|\b\d{12}\b"),
]


@app.route("/api/pii/classify", methods=["POST"])
def pii_classify():
    """Scan text for PII elements and guess if it is structured or not."""
    text = request.get_json().get("text", "")
    found = []
    claimed = []   # character spans already matched, to avoid double-counting
    for name, pat in PII_PATTERNS:
        for m in re.finditer(pat, text):
            s, e = m.span()
            if any(not (e <= cs or s >= ce) for cs, ce in claimed):
                continue
            claimed.append((s, e))
            found.append({"type": name, "value": m.group()})
    found.sort(key=lambda x: text.find(x["value"]))

    t = text.strip()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if t.startswith("{") or t.startswith("["):
        structure = "Structured (JSON-like)"
    elif len(lines) > 1 and sum("," in ln for ln in lines) >= len(lines) - 1:
        structure = "Structured (CSV-like table)"
    else:
        structure = "Unstructured (free text)"

    return jsonify({"found": found, "count": len(found),
                    "structure": structure})


# ---- a small sample healthcare dataset with PII --------------------------
HEALTH_DATA = [
    {"name": "Rahul",  "age": 28, "pincode": 560001, "gender": "M", "disease": "Flu"},
    {"name": "Arjun",  "age": 22, "pincode": 560002, "gender": "M", "disease": "Cancer"},
    {"name": "Priya",  "age": 24, "pincode": 560001, "gender": "F", "disease": "Diabetes"},
    {"name": "Sneha",  "age": 21, "pincode": 560003, "gender": "F", "disease": "Flu"},
    {"name": "Vikram", "age": 33, "pincode": 560002, "gender": "M", "disease": "Cancer"},
    {"name": "Karan",  "age": 36, "pincode": 560004, "gender": "M", "disease": "Flu"},
    {"name": "Divya",  "age": 37, "pincode": 560001, "gender": "F", "disease": "Diabetes"},
    {"name": "Meera",  "age": 31, "pincode": 560003, "gender": "F", "disease": "Cancer"},
    {"name": "Rohit",  "age": 45, "pincode": 560002, "gender": "M", "disease": "Flu"},
    {"name": "Dev",    "age": 41, "pincode": 560004, "gender": "M", "disease": "Diabetes"},
    {"name": "Anita",  "age": 48, "pincode": 560001, "gender": "F", "disease": "Cancer"},
    {"name": "Kavya",  "age": 43, "pincode": 560003, "gender": "F", "disease": "Flu"},
]


def _age_band(a):
    lo = (a // 10) * 10
    return "%d-%d" % (lo, lo + 9)


def _zip_gen(z):
    return str(z)[:4] + "XX"


@app.route("/api/anon/apply", methods=["POST"])
def anon_apply():
    """
    Apply k-anonymity by generalising quasi-identifiers (age -> band,
    pincode -> prefix) and suppressing the name. Then measure k-anonymity,
    l-diversity, (simplified) t-closeness, and re-identification risk.
    """
    data = HEALTH_DATA

    # --- re-identification risk BEFORE (records unique on quasi-identifiers)
    orig_keys = [(r["age"], r["gender"], r["pincode"]) for r in data]
    oc = Counter(orig_keys)
    unique_before = sum(1 for key in orig_keys if oc[key] == 1)
    risk_before = round(unique_before / len(data) * 100, 1)

    # --- anonymise
    anon = [{"name": "*", "age": _age_band(r["age"]), "gender": r["gender"],
             "pincode": _zip_gen(r["pincode"]), "disease": r["disease"]}
            for r in data]

    # --- equivalence classes on the generalised quasi-identifiers
    groups = {}
    for r in anon:
        groups.setdefault((r["age"], r["gender"], r["pincode"]), []).append(r)

    k = min(len(g) for g in groups.values())                      # k-anonymity
    l = min(len(set(x["disease"] for x in g)) for g in groups.values())  # l-div

    # --- simplified t-closeness: max total-variation distance between a
    #     group's sensitive distribution and the overall distribution
    overall = Counter(r["disease"] for r in anon)
    n = len(anon)
    diseases = list(overall)
    t = 0.0
    for g in groups.values():
        gc = Counter(x["disease"] for x in g)
        tvd = 0.5 * sum(abs(gc[d] / len(g) - overall[d] / n) for d in diseases)
        t = max(t, tvd)

    risk_after = round(1 / k * 100, 1)   # best case an attacker can do: 1/k

    return jsonify({
        "original": data, "anonymized": anon,
        "k": k, "l": l, "t": round(t, 2), "groups": len(groups),
        "risk_before": risk_before, "risk_after": risk_after,
    })


@app.route("/api/anon/dp", methods=["POST"])
def anon_dp():
    """
    Differential privacy: answer a COUNT query but add Laplace noise so no
    single person's presence can be detected. Smaller epsilon = more noise
    = more privacy.
    """
    d = request.get_json() or {}
    disease = d.get("disease", "Flu")
    eps = float(d.get("epsilon", 1.0))

    true_count = sum(1 for r in HEALTH_DATA
                     if r["disease"].lower() == disease.lower())

    # sample Laplace noise with scale b = sensitivity(=1) / epsilon
    u = random.random() - 0.5
    b = 1.0 / max(eps, 0.01)
    noise = -b * math.copysign(1, u) * math.log(1 - 2 * abs(u))
    noisy = round(true_count + noise, 2)

    return jsonify({"disease": disease, "epsilon": eps,
                    "true_count": true_count, "noisy_count": noisy})


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
