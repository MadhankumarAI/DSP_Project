"""
Experiment 9: Hash Functions and Obfuscation
a) Implement common hash functions (e.g., SHA-256, MD5) using Python's
   hashlib. Input: A string or file. Output: Its hash value.
b) Explore obfuscation techniques. Example: Create a simple
   obfuscation script that hides a Python function's logic.
"""
import hashlib
import base64

# a) Hash functions
text = input("Enter text to hash: ").encode()
print("MD5:", hashlib.md5(text).hexdigest())
print("SHA-256:", hashlib.sha256(text).hexdigest())

# b) Obfuscation demo - hide a function's logic by base64-encoding its
# source and only decoding/executing it at runtime
source_code = "def secret():\n    return 2 + 2"
encoded_blob = base64.b64encode(source_code.encode()).decode()
print("\nObfuscated blob:", encoded_blob)

namespace = {}
exec(base64.b64decode(encoded_blob).decode(), namespace)
print("Decoded & run -> secret() =", namespace["secret"]())
