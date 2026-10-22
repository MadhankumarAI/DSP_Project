"""
Experiment 1: Basic Security Tool, TryHackMe, My IP Address, HashCalc, Basic Cryptography
a) Simple Password Strength Checker
b) Basic User Authentication Simulation (TryHackMe)
c) Identifying Network and Public IP Information - Find Local IP Address
d) Basic Cryptography Using Python - Simple Caesar Cipher
e) Practical Cryptography - Hex Encoding and Decoding
"""
import socket

# a) Password strength checker
password = input("Enter password: ")
if len(password) >= 8:
    print("Password length is good")
else:
    print("Weak password: Use at least 8 characters")

# b) Basic user authentication simulation
username = input("Enter username: ")
password = input("Enter password: ")
if username == "student" and password == "1234":
    print("Login Successful")
else:
    print("Invalid Username or Password")

# c) Find local IP address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print("Hostname:", hostname)
print("Local IP Address:", ip_address)

# d) Simple Caesar cipher
text = input("Enter message: ")
shift = 3
encrypted = "".join(chr(ord(char) + shift) for char in text)
print("Encrypted Message:", encrypted)

# e) Hex encoding and decoding
text = "Hello"
encoded = text.encode().hex()
decoded = bytes.fromhex(encoded).decode()
print("Encoded:", encoded)
print("Decoded:", decoded)
