# DSP Lab Viva — Q&A

Based on the 12 lab experiments and Module 1–4 content (CIA triad, cryptography,
obfuscation, privacy models, GDPR/DPDP).

## CIA Triad & Core Security Properties

**Q: What is the CIA triad?**
Confidentiality (only authorized parties can read data), Integrity (data isn't
modified without detection), Availability (data/systems stay accessible to
authorized users, even under attack).

**Q: What is non-repudiation?**
The sender of a message cannot later deny having sent it. Digital signatures
provide this — only the sender's private key could have produced a valid
signature, so they can't credibly deny authorship.

**Q: How is non-repudiation different from integrity?**
Integrity proves the data wasn't altered. Non-repudiation proves *who* sent
it and that they can't deny it. A hash gives you integrity; a digital
signature (hash + encryption with sender's private key) gives you both.

**Q: What is accountability in security?**
The ability to trace an action back to the specific entity (user/system)
responsible for it — usually via logging/audit trails.

## Cryptography

**Q: Symmetric vs asymmetric encryption?**
Symmetric (AES, DES) uses one shared key for encrypt+decrypt — fast, but key
distribution is a problem. Asymmetric (RSA, Diffie-Hellman) uses a public/
private key pair — solves key distribution, but much slower, so in practice
it's often used only to exchange a symmetric session key (hybrid encryption).

**Q: What properties should a good hash function have?**
Deterministic, fast to compute, pre-image resistant (can't reverse hash to
input), second pre-image resistant, collision resistant (hard to find two
inputs with the same hash), and small input changes should produce a wildly
different output (avalanche effect).

**Q: Why is MD5 considered weak today?**
It's collision-prone — practical collision attacks exist, so two different
inputs can be crafted to produce the same MD5 hash. SHA-256 doesn't have
this problem at a practical level, so it's preferred for integrity checks.

**Q: How does RSA digital signing work?**
The sender hashes the message, then encrypts that hash with their RSA
*private* key — that's the signature. The receiver decrypts the signature
with the sender's *public* key and compares it to their own hash of the
message. Match = authentic and untampered.

**Q: What is TLS, and how is it different from E2EE?**
TLS secures the transport link (e.g. client↔server) — anyone who can see
inside the server (e.g. the server operator) can see the plaintext. E2EE
encrypts the message so only sender and final recipient can decrypt it —
even a compromised or malicious relay server in between can't read it.
A secure messaging app typically uses both: TLS for the pipe, E2EE for the
payload.

## Obfuscation

**Q: What is obfuscation?**
Transforming human-readable code or data into a form that's hard to
understand/reverse-engineer, while keeping it fully functional. Goal is to
hide logic or secrets (e.g. signing keys) from casual inspection — not to
provide cryptographic-strength security.

**Q: What are the three primary data-obfuscation techniques?**
1. **Masking** — create a similar-looking but different version of the
   data (same structure/type, different value), e.g. replacing real credit
   card digits with fake ones for a test environment.
2. **Substitution/Pseudonymization** — replace sensitive values with a
   realistic-looking but fake value (a pseudonym), so it's still usable for
   testing/analytics without exposing the real value.
3. **Encryption** — scrambles the value completely so it's unusable
   without the key; most secure but you lose the ability to analyze/use the
   data without decrypting it first.

**Q: Is obfuscation the same as encryption?**
No. Encryption is mathematically reversible only with a key and gives a
measurable security guarantee. Obfuscation just makes something *harder to
read/understand* — a sufficiently motivated reverse-engineer can usually
still recover it (e.g. base64-encoding or reordering code isn't secure, just
inconvenient to read).

## Privacy-Preserving Models (Anonymization)

**Q: What is k-anonymity?**
A dataset satisfies k-anonymity if every combination of quasi-identifiers
(e.g. age, gender, zip code) is shared by at least **k** records — so any
individual is indistinguishable from at least k-1 others.

**Q: How do you achieve k-anonymity?**
- **Suppression** — replace some values with "*" (e.g. hide the Name
  column entirely).
- **Generalization** — replace a specific value with a broader range/
  category (e.g. age "23" → "20<Age≤30", exact zip → region).

**Q: What is a quasi-identifier?**
An attribute that isn't identifying on its own (age, zip code, gender) but
can identify someone when combined with other quasi-identifiers or outside
knowledge.

**Q: What's the main weakness of k-anonymity?**
The **homogeneity attack** — if all k records in a group share the same
sensitive value (e.g. all have "heart disease"), an attacker who knows
someone is in that group learns their sensitive value even without picking
out the exact record. k-anonymity also doesn't defend against attackers
with external/background knowledge, and never fully eliminates
re-identification risk — it only reduces it as k increases.

**Q: What is l-diversity, and what problem does it fix?**
l-diversity requires each k-anonymous group to also contain at least **l**
*distinct* values for the sensitive attribute — directly fixing the
homogeneity attack, since a group can no longer have all-identical
sensitive values.

**Q: What's the weakness of l-diversity, and how does t-closeness fix it?**
l-diversity doesn't account for how *similar* those distinct values are, or
how their distribution compares to the overall dataset (the **skewness/
similarity attack** — e.g. a group with 1 "HIV positive" and 9 "flu" still
technically has 2 distinct values, but leaks a strong probability signal).
t-closeness fixes this by requiring each group's distribution of the
sensitive attribute to be close (within threshold t) to the distribution in
the whole dataset, limiting how much extra information a group reveals.

**Q: What is differential privacy, and how is it different from k-anonymity/
l-diversity/t-closeness?**
k-anonymity, l-diversity and t-closeness all make assumptions about what
background knowledge an attacker has — differential privacy doesn't. It
adds carefully calibrated random noise to query results (or to the data)
so that the presence or absence of any single individual's record barely
changes the output — giving a mathematical privacy guarantee regardless of
what the attacker already knows.

**Q: What does "sensitivity" mean in differential privacy?**
How much a function's output can change when a single individual's record
is added or removed from the dataset. Higher sensitivity needs more noise
to hide an individual's contribution.

**Q: Order these from weakest to strongest privacy guarantee: k-anonymity,
l-diversity, t-closeness, differential privacy.**
k-anonymity < l-diversity < t-closeness < differential privacy — each one
closes an attack the previous one is vulnerable to, with differential
privacy being the only one that doesn't rely on assumptions about attacker
knowledge.

## PII & Data Classification

**Q: What is PII?**
Personally Identifiable Information — any data that can identify a specific
individual, either alone (name, SSN/Aadhaar, email) or combined with other
data (quasi-identifiers like age + zip + gender).

**Q: What are the three states of data, and why does it matter for
security?**
In-transit (moving over a network — protect with TLS/encryption),
at-rest (stored on disk — protect with encryption, access controls),
in-use (actively being processed in memory — hardest to protect, relevant
to things like confidential computing). Each state needs different controls.

## Governance & Regulation

**Q: What does a Data Protection Officer (DPO) do?**
Oversees an organization's data-protection compliance strategy — monitors
adherence to the law, handles data-subject/principal requests, is the
point of contact for the regulator, and advises on privacy impact
assessments. Both GDPR and India's DPDP Act 2023 require one for
organizations processing data at scale.

**Q: Key differences between GDPR and DPDP Act 2023?**
GDPR applies to EU residents' data globally, requires breach notification
within 72 hours, and penalties up to €20M/4% of global turnover. DPDP Act
2023 applies to digital personal data of Indian residents, requires
notifying India's Data Protection Board "without delay" (no fixed hour
limit), and penalties up to ₹250 crore per instance.

## Attacks & Detection

**Q: Dictionary attack vs brute-force attack?**
Dictionary attack tries a curated list of likely passwords/words (fast,
works well against weak/reused passwords). Brute-force tries every possible
combination of a character set (guaranteed to eventually find it, but
exponentially slower as length/charset grows).

**Q: Why hash passwords instead of storing them in plaintext?**
If the database leaks, plaintext passwords are immediately usable by an
attacker. A hash (ideally salted, with a slow algorithm like bcrypt) means
the attacker only gets hashes, and has to run their own dictionary/brute-
force attack against them — which can be made computationally expensive.

**Q: What features help detect a phishing URL?**
URL length, presence of "@" (used to hide the real domain), lack of HTTPS,
excessive hyphens/subdomains, use of IP addresses instead of domain names,
and suspicious keywords (e.g. "verify", "secure-login", "update-account").
A TF-IDF + classifier approach over the URL's characters can pick up these
suspicious substrings automatically instead of hand-coding each feature.

**Q: What makes SQL injection possible, and how do you defend against it?**
Concatenating untrusted user input directly into a SQL query string lets an
attacker inject SQL keywords/syntax to alter the query's meaning. Defense:
parameterized queries/prepared statements (never string-concatenate SQL),
input validation, and least-privilege DB accounts.

**Q: Name some common vulnerable coding patterns a static scanner should
flag.**
`eval()`/`exec()` on untrusted input (code injection), `os.system()` with
unsanitized input (command injection), hardcoded passwords/secrets, string-
concatenated SQL queries, `pickle.loads()` on untrusted data (unsafe
deserialization — can execute arbitrary code), weak hash algorithms (MD5),
and disabled TLS verification (`verify=False`).

## Authentication & Authorization

**Q: Authentication vs authorization?**
Authentication answers "who are you?" (verifying identity — login).
Authorization answers "what are you allowed to do?" (checking permissions
after identity is confirmed).

**Q: What is a JWT, and why use it for API authentication?**
A JSON Web Token — a signed (not necessarily encrypted) token containing
claims (e.g. username, expiry), issued after login. The server can verify
its signature on every request without a database lookup or server-side
session state, since the token itself proves it was issued by the server
and hasn't been tampered with.
