"""
Experiment 10: Digital Signatures, Authentication, and Authorization
a) Implement digital signature generation and verification using RSA
   (cryptography library).
b) Simulate authentication and authorization using a web application
   (Flask). Implement login functionality and secure API calls with
   tokens (JWT).
Case Study: Use of digital signatures in e-commerce and banking -
RSA signatures let a bank/merchant server prove a transaction message
really came from them and was not altered in transit, the same idea
demonstrated in part (a) below.

Run (b) as:  python q10_digital_signature_auth.py server
"""
import sys

def run_rsa_signature_demo():
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    sign_padding = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)

    message = input("Enter message to sign (e.g. a bank transaction): ").encode()
    signature = private_key.sign(message, sign_padding, hashes.SHA256())
    print("Signature (hex):", signature.hex()[:60], "...")

    try:
        public_key.verify(signature, message, sign_padding, hashes.SHA256())
        print("Signature VALID - message authentic & untampered.")
    except Exception:
        print("Signature INVALID - message was tampered or wrong signature.")

def run_flask_server():
    import jwt
    import datetime
    from flask import Flask, request, jsonify

    app = Flask(__name__)
    SECRET_KEY = "lab-secret-key"
    USERS = {"student": "1234"}  # demo credentials only

    @app.post("/login")
    def login():
        data = request.json or {}
        if USERS.get(data.get("username")) == data.get("password"):
            token = jwt.encode(
                {"user": data["username"], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                SECRET_KEY, algorithm="HS256",
            )
            return jsonify(token=token)
        return jsonify(error="invalid credentials"), 401

    @app.get("/secure-data")
    def secure_data():
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return jsonify(message=f"Hello {payload['user']}, here is your secure data.")
        except Exception:
            return jsonify(error="unauthorized"), 401

    app.run(port=5000)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        run_flask_server()
    else:
        run_rsa_signature_demo()
