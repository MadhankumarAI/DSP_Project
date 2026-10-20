"""Q7: Phishing Website Detection - tiny ML model (scikit-learn) on URL features."""
import tkinter as tk
from tkinter import ttk
from sklearn.tree import DecisionTreeClassifier

# Sample labeled URLs: 1 = phishing, 0 = legitimate
training_data = [
    ("http://secure-login-paypal.com/verify@update", 1),
    ("http://bank-update.info/signin?user=@", 1),
    ("http://free-gift-claim-now.tk", 1),
    ("http://192.168.1.1/login@account", 1),
    ("https://www.google.com", 0),
    ("https://www.wikipedia.org", 0),
    ("https://github.com/login", 0),
    ("https://www.amazon.com/account", 0),
]

def extract_features(url):
    return [len(url), url.count("@"), int(url.startswith("https")), url.count("-")]

features = [extract_features(url) for url, label in training_data]
labels = [label for url, label in training_data]
model = DecisionTreeClassifier().fit(features, labels)

def check_url():
    url = url_entry.get().strip()
    if not url:
        return
    prediction = model.predict([extract_features(url)])[0]
    result_var.set("PHISHING!" if prediction else "Looks Legitimate")

root = tk.Tk()
root.title("Q7 - Phishing Detector (ML)")
root.geometry("420x160")

ttk.Label(root, text="Enter URL:").pack(pady=4)
url_entry = ttk.Entry(root, width=50)
url_entry.pack()
ttk.Button(root, text="Check", command=check_url).pack(pady=8)
result_var = tk.StringVar()
ttk.Label(root, textvariable=result_var, font=("Arial", 13, "bold")).pack()

root.mainloop()
