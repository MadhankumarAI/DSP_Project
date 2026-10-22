"""
Experiment 7: Phishing Website Detection using Python
Use a dataset of phishing and legitimate websites. Train a simple ML
model using scikit-learn to classify URLs based on features like
length, presence of @, https, etc.
"""
import tkinter as tk
from tkinter import ttk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Sample labeled URLs: 1 = phishing, 0 = legitimate
training_data = [
    ("http://secure-login-paypal.com/verify@update", 1),
    ("http://bank-update.info/signin?user=@", 1),
    ("http://free-gift-claim-now.tk", 1),
    ("http://192.168.1.1/login@account", 1),
    ("http://paypal-security-alert.ru/login", 1),
    ("http://verify-account-now.xyz/bank", 1),
    ("https://www.google.com", 0),
    ("https://www.wikipedia.org", 0),
    ("https://github.com/login", 0),
    ("https://www.amazon.com/account", 0),
    ("https://www.microsoft.com/en-us", 0),
    ("https://www.paypal.com/signin", 0),
]

urls = [url for url, label in training_data]
labels = [label for url, label in training_data]

# TF-IDF over character n-grams + Logistic Regression - captures suspicious
# substrings (e.g. "paypal", "secure-login", "verify") far better than
# just checking length/@/https individually on such a small dataset.
model = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5))),
    ("logreg", LogisticRegression()),
])
model.fit(urls, labels)

def check_url():
    prediction = model.predict([url_entry.get()])[0]
    result_var.set("PHISHING!" if prediction else "Looks Legitimate")

root = tk.Tk()
root.title("Phishing URL Detector")
root.geometry("420x150")

ttk.Label(root, text="Enter URL:").pack(pady=4)
url_entry = ttk.Entry(root, width=50)
url_entry.pack()
ttk.Button(root, text="Check", command=check_url).pack(pady=8)
result_var = tk.StringVar()
ttk.Label(root, textvariable=result_var, font=("Arial", 13, "bold")).pack()

root.mainloop()
