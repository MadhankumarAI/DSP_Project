"""Q9: Hash functions (MD5/SHA-256) + a simple code-obfuscation demo."""
import hashlib
import base64
import tkinter as tk
from tkinter import ttk

def compute_hashes():
    text = text_entry.get().encode()
    md5_label.config(text=f"MD5: {hashlib.md5(text).hexdigest()}")
    sha_label.config(text=f"SHA-256: {hashlib.sha256(text).hexdigest()}")

def obfuscation_demo():
    # "hides" source logic by base64-encoding it and executing it at runtime
    source_code = "def secret():\n    return 2 + 2"
    encoded_blob = base64.b64encode(source_code.encode()).decode()
    namespace = {}
    exec(base64.b64decode(encoded_blob).decode(), namespace)
    obf_label.config(text=f"Obfuscated blob: {encoded_blob}\nDecoded & run -> secret() = {namespace['secret']()}")

root = tk.Tk()
root.title("Q9 - Hashing & Obfuscation")
root.geometry("500x260")

ttk.Label(root, text="Text to hash:").pack()
text_entry = ttk.Entry(root, width=50)
text_entry.pack()
ttk.Button(root, text="Compute Hashes", command=compute_hashes).pack(pady=4)
md5_label = ttk.Label(root, text="")
md5_label.pack()
sha_label = ttk.Label(root, text="")
sha_label.pack()

ttk.Button(root, text="Obfuscation Demo", command=obfuscation_demo).pack(pady=8)
obf_label = ttk.Label(root, text="", wraplength=460, justify="left")
obf_label.pack()

root.mainloop()
