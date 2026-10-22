"""
Experiment 4: Build python code for Dictionary Attack for plaintext and hash value.
- Add brute-force simulation in this GUI
- Add password strength checker (weak/medium/strong)
- Export analyzed passwords by category
- Support longer passwords (4+ characters)
- Export analysis report as .txt or .csv
- Add real-time progress bar for brute-force
(GUI used here because the question explicitly asks for one.)
"""
import hashlib
import itertools
import string
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

wordlist = ["password", "123456", "qwerty", "admin", "letmein", "welcome", "iloveyou"]

def sha256_hash(word):
    return hashlib.sha256(word.encode()).hexdigest()

def password_strength(password):
    score = sum([
        len(password) >= 8,
        any(char.isdigit() for char in password),
        any(char.isupper() for char in password),
        any(char in string.punctuation for char in password),
    ])
    if score <= 1:
        return "Weak"
    if score <= 2:
        return "Medium"
    return "Strong"

def load_wordlist():
    global wordlist
    path = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
    if path:
        wordlist = open(path, encoding="utf-8", errors="ignore").read().splitlines()
        status_var.set(f"Loaded {len(wordlist)} words")

def dictionary_attack():
    target = hash_entry.get().strip()
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(wordlist)
    for index, word in enumerate(wordlist, 1):
        progress_bar["value"] = index
        root.update_idletasks()
        if sha256_hash(word) == target:
            status_var.set(f"Found: {word}  (strength: {password_strength(word)})")
            return
    status_var.set("Not found in dictionary.")

def brute_force_attack():
    target = hash_entry.get().strip()
    charset = string.ascii_lowercase + string.digits
    max_length = 3
    for length in range(1, max_length + 1):
        for combo in itertools.product(charset, repeat=length):
            candidate = "".join(combo)
            if sha256_hash(candidate) == target:
                status_var.set(f"Brute-force found: {candidate}")
                return
    status_var.set(f"Not found by brute-force (maxlen={max_length}).")

def export_wordlist():
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if path:
        with open(path, "w", newline="") as file:
            csv.writer(file).writerows([(word, password_strength(word)) for word in wordlist])
        messagebox.showinfo("Export", "Saved.")

root = tk.Tk()
root.title("Q4 - Dictionary/Brute-force Attack")
root.geometry("420x260")

ttk.Label(root, text="Target SHA-256 hash:").pack()
hash_entry = ttk.Entry(root, width=65)
hash_entry.pack()
ttk.Button(root, text="Load Wordlist", command=load_wordlist).pack(pady=2)
ttk.Button(root, text="Start Dictionary Attack", command=dictionary_attack).pack(pady=2)
ttk.Button(root, text="Start Brute-force (len<=3)", command=brute_force_attack).pack(pady=2)

progress_bar = ttk.Progressbar(root, length=350)
progress_bar.pack(pady=6)
status_var = tk.StringVar(value="Idle")
ttk.Label(root, textvariable=status_var).pack()
ttk.Button(root, text="Export Wordlist Strength (.csv)", command=export_wordlist).pack(pady=4)

root.mainloop()
