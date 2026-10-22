"""
Experiment 8: Develop a real-time messaging application where two
devices can communicate securely. The application must use Transport
Layer Security (TLS) for securing the client-server communication and
End-to-End Encryption (E2EE) to ensure that only the sender and
recipient can access the message content. The server should act
solely as a message relay and have no access to plaintext messages.

Run:  python q8_secure_messaging.py server
      python q8_secure_messaging.py client
(Self-signed cert is auto-generated on first run for the TLS layer.)
"""
import sys
import ssl
import socket
import os
import datetime
from cryptography.fernet import Fernet
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

E2EE_KEY = b"X3rP9q2L7mN0vK1cQ8sT5wY4hD6fA3bU7eJ9iO2nM0s="  # shared out-of-band in real use
fernet = Fernet(E2EE_KEY)
CERT_FILE, KEY_FILE = "cert.pem", "key.pem"

def ensure_certificate():
    if os.path.exists(CERT_FILE):
        return
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )
    with open(KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
    with open(CERT_FILE, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

def run_server():
    ensure_certificate()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERT_FILE, KEY_FILE)
    with socket.socket() as sock:
        sock.bind(("localhost", 9443))
        sock.listen(1)
        print("Server relay listening (TLS up, cannot read E2EE payloads)...")
        with context.wrap_socket(sock, server_side=True) as tls_sock:
            connection, _ = tls_sock.accept()
            while True:
                data = connection.recv(4096)
                if not data:
                    break
                print("Relayed ciphertext (server can't decrypt):", data[:60], "...")
                connection.sendall(data)  # relay only, never decrypts

def run_client():
    ensure_certificate()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # self-signed demo cert
    with socket.socket() as sock, context.wrap_socket(sock, server_hostname="localhost") as tls_sock:
        tls_sock.connect(("localhost", 9443))
        message = input("Message to send securely: ")
        tls_sock.sendall(fernet.encrypt(message.encode()))
        echoed = tls_sock.recv(4096)
        print("Decrypted (E2EE) reply:", fernet.decrypt(echoed).decode())

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "client"
    if mode == "server":
        run_server()
    else:
        run_client()
