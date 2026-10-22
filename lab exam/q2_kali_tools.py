"""
Experiment 2: Kali Linux, Wireshark, Burp Suite, OWASP, CryptoHack
a) Exploring Kali Linux - Check System Information
b) Network Traffic Analysis Using Wireshark
c) Basic Web Security Testing - Simple Input Validation
d) Understanding OWASP Security Risks - Simple SQL Injection Keyword Detection
"""
import platform
import urllib.request

# a) Check system information
print("Operating System:", platform.system())
print("Version:", platform.version())
print("Machine:", platform.machine())

# b) Generate network traffic (capture this in Wireshark)
website = "https://example.com"
response = urllib.request.urlopen(website)
print("Status Code:", response.status)

# c) Simple input validation
username = input("Enter username: ")
if username.isalnum():
    print("Valid Input")
else:
    print("Invalid Input: Special characters detected")

# d) Simple SQL injection keyword detection
user_input = input("Enter username: ")
keywords = ["SELECT", "DROP", "DELETE", "--"]
for word in keywords:
    if word.lower() in user_input.lower():
        print("Possible malicious input detected")
        break
else:
    print("Input appears normal")
