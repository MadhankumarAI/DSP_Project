"""Q5: Safe, non-malicious virus simulation - spreads a fake signature across in-memory
files and a scanner detects/removes it. Nothing here touches real files or the OS."""
import random
import tkinter as tk
from tkinter import ttk

SIGNATURE = "X-SIM-VIRUS-42"
fake_filesystem = {f"file{i}.txt": "normal content" for i in range(1, 9)}

def refresh_list():
    file_listbox.delete(0, tk.END)
    for name, content in fake_filesystem.items():
        tag = "INFECTED" if SIGNATURE in content else "clean"
        file_listbox.insert(tk.END, f"{name}: {tag}")

def infect_random_file():
    clean_files = [name for name, content in fake_filesystem.items() if SIGNATURE not in content]
    if clean_files:
        target = random.choice(clean_files)
        fake_filesystem[target] += " " + SIGNATURE
        log_box.insert(tk.END, f"[Infect] {target} got infected (simulated).\n")
    refresh_list()

def scan_and_disinfect():
    cleaned = 0
    for name, content in fake_filesystem.items():
        if SIGNATURE in content:
            fake_filesystem[name] = content.replace(SIGNATURE, "").strip()
            cleaned += 1
    log_box.insert(tk.END, f"[Scan] Disinfected {cleaned} file(s).\n")
    refresh_list()

root = tk.Tk()
root.title("Q5 - Virus Simulation (Educational, Safe)")
root.geometry("420x420")

ttk.Button(root, text="Simulate Spread (infect 1 file)", command=infect_random_file).pack(pady=6)
ttk.Button(root, text="Scan & Disinfect", command=scan_and_disinfect).pack(pady=6)

file_listbox = tk.Listbox(root, width=40, height=10)
file_listbox.pack(pady=6)
log_box = tk.Text(root, height=8)
log_box.pack(fill="both", expand=True, padx=6, pady=6)

refresh_list()
root.mainloop()
