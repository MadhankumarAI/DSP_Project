"""Q10a: RSA digital signature sign/verify (tkinter GUI) - default mode.
Q10b: Flask login + JWT-secured API - run as: python q10_digital_signature_auth.py server"""
import sys

def run_rsa_gui():
    import tkinter as tk
    from tkinter import ttk
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    signature_holder = {"signature": None}

    def sign_message():
        message = message_entry.get().encode()
        signature_holder["signature"] = private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        result_label.config(text=f"Signature (hex): {signature_holder['signature'].hex()[:60]}...")

    def verify_message():
        try:
            public_key.verify(
                signature_holder["signature"],
                message_entry.get().encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            result_label.config(text="Signature VALID - message authentic & untampered.")
        except Exception:
            result_label.config(text="Signature INVALID - message was tampered or wrong signature.")

    root = tk.Tk()
    root.title("Q10a - RSA Digital Signature")
    root.geometry("420x200")
    ttk.Label(root, text="Message (e.g. bank transaction):").pack()
    message_entry = ttk.Entry(root, width=45)
    message_entry.pack()
    ttk.Button(root, text="Sign", command=sign_message).pack(pady=4)
    ttk.Button(root, text="Verify", command=verify_message).pack(pady=4)
    result_label = ttk.Label(root, text="", wraplength=380)
    result_label.pack(pady=6)
    root.mainloop()

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
        run_rsa_gui()
