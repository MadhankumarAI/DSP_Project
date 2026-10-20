"""Q1: Basic Security Tools - password check, login sim, local IP, Caesar cipher, hex codec."""
import socket
import tkinter as tk
from tkinter import ttk, messagebox

def check_strength():
    password = pw_entry.get()
    msg = "Password length is good" if len(password) >= 8 else "Weak password: use at least 8 characters"
    messagebox.showinfo("Strength", msg)

def login():
    ok = user_entry.get() == "student" and pass_entry.get() == "1234"
    messagebox.showinfo("Login", "Login Successful" if ok else "Invalid Username or Password")

def show_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    messagebox.showinfo("IP Info", f"Hostname: {hostname}\nLocal IP: {ip_address}")

def caesar_encrypt():
    shift = 3
    encrypted = "".join(chr(ord(char) + shift) for char in msg_entry.get())
    caesar_output.config(text=f"Encrypted: {encrypted}")

def hex_codec():
    text = hex_entry.get()
    encoded = text.encode().hex()
    decoded = bytes.fromhex(encoded).decode()
    hex_output.config(text=f"Hex: {encoded}  |  Decoded back: {decoded}")

root = tk.Tk()
root.title("Q1 - Basic Security Tools")
root.geometry("420x360")

ttk.Label(root, text="Password:").pack()
pw_entry = ttk.Entry(root, show="*")
pw_entry.pack()
ttk.Button(root, text="Check Strength", command=check_strength).pack(pady=4)

ttk.Label(root, text="Username:").pack()
user_entry = ttk.Entry(root)
user_entry.pack()
ttk.Label(root, text="Password (try 1234):").pack()
pass_entry = ttk.Entry(root, show="*")
pass_entry.pack()
ttk.Button(root, text="Login (user: student)", command=login).pack(pady=4)

ttk.Button(root, text="Show My Local IP", command=show_ip).pack(pady=4)

ttk.Label(root, text="Message to Caesar-encrypt (shift=3):").pack()
msg_entry = ttk.Entry(root)
msg_entry.pack()
ttk.Button(root, text="Encrypt", command=caesar_encrypt).pack()
caesar_output = ttk.Label(root, text="")
caesar_output.pack()

ttk.Label(root, text="Text to hex-encode/decode:").pack()
hex_entry = ttk.Entry(root)
hex_entry.pack()
ttk.Button(root, text="Hex Encode/Decode", command=hex_codec).pack()
hex_output = ttk.Label(root, text="")
hex_output.pack()

root.mainloop()
