"""Q3: CIA Triad simulation - Confidentiality, Integrity, Availability."""
import hashlib
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from cryptography.fernet import Fernet

def log(message):
    output_box.insert(tk.END, message + "\n")
    output_box.see(tk.END)

def confidentiality_demo():
    key = Fernet.generate_key()
    cipher = Fernet(key)
    message = b"Top Secret: AI is amazing!"
    encrypted = cipher.encrypt(message)
    decrypted = cipher.decrypt(encrypted)
    log(f"[Confidentiality] Original: {message}\nEncrypted: {encrypted}\nDecrypted: {decrypted}")

def integrity_demo():
    original_hash = hashlib.sha256(b"Data must stay the same").hexdigest()
    tampered_hash = hashlib.sha256(b"Data must stay different").hexdigest()
    result = "OK: unchanged" if original_hash == tampered_hash else "BREACH: data was altered!"
    log(f"[Integrity] Original hash: {original_hash}\nTampered hash: {tampered_hash}\n{result}")

def availability_demo():
    def worker():
        log("[Availability] Server running, files available.")
        log("[Availability] Simulating DDoS attack... server busy!")
        time.sleep(2)
        log("[Availability] Server restored and available again.")
    threading.Thread(target=worker, daemon=True).start()

root = tk.Tk()
root.title("Q3 - CIA Triad")
root.geometry("480x380")

ttk.Button(root, text="Confidentiality Demo", command=confidentiality_demo).pack(pady=4)
ttk.Button(root, text="Integrity Demo", command=integrity_demo).pack(pady=4)
ttk.Button(root, text="Availability Demo", command=availability_demo).pack(pady=4)

output_box = scrolledtext.ScrolledText(root, height=18)
output_box.pack(fill="both", expand=True, padx=6, pady=6)

root.mainloop()
