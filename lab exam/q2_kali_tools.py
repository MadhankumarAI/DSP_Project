"""Q2: Kali Linux / Wireshark / Burp / OWASP / CryptoHack basics."""
import platform
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox

def show_system_info():
    info = f"OS: {platform.system()}\nVersion: {platform.version()}\nMachine: {platform.machine()}"
    messagebox.showinfo("System Info", info)

def generate_traffic():
    try:
        status_code = urllib.request.urlopen("https://example.com", timeout=5).status
    except Exception as error:
        status_code = f"error: {error}"
    messagebox.showinfo("Network Traffic (capture this in Wireshark)", f"Status Code: {status_code}")

def validate_input():
    username = user_entry.get()
    valid = username.isalnum()
    messagebox.showinfo("Input Validation", "Valid Input" if valid else "Invalid Input: special characters detected")

def check_sql_injection():
    user_input = sql_entry.get().lower()
    keywords = ["select", "drop", "delete", "--"]
    hit = next((word for word in keywords if word in user_input), None)
    if hit:
        messagebox.showwarning("OWASP Check", f"Possible malicious input detected: '{hit}'")
    else:
        messagebox.showinfo("OWASP Check", "Input appears normal")

root = tk.Tk()
root.title("Q2 - Kali/Wireshark/Burp/OWASP")
root.geometry("400x260")

ttk.Button(root, text="Check System Info (Kali)", command=show_system_info).pack(pady=6)
ttk.Button(root, text="Generate & Check Traffic (Wireshark)", command=generate_traffic).pack(pady=6)

ttk.Label(root, text="Username (Burp input test):").pack()
user_entry = ttk.Entry(root)
user_entry.pack()
ttk.Button(root, text="Validate Input", command=validate_input).pack(pady=4)

ttk.Label(root, text="Input to scan (OWASP/SQLi):").pack()
sql_entry = ttk.Entry(root, width=30)
sql_entry.pack()
ttk.Button(root, text="Scan for SQL Injection", command=check_sql_injection).pack(pady=4)

root.mainloop()
