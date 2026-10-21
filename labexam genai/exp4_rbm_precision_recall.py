"""
Experiment 4: RBM + Precision-Recall
- Load the MNIST handwritten digit dataset & display (any 5)
- Preprocess the dataset by normalizing pixel values between 0 & 1
- Implement a Restricted Boltzmann Machine. Use a logistic regression
  classifier with RBM features to classify the digits from 0-9
- Generate classification report -> Precision, Recall, F1 for each digit
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.neural_network import BernoulliRBM
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# Load MNIST
mnist = fetch_openml("mnist_784", version=1, as_frame=False)
pixels, labels = mnist.data, mnist.target.astype(int)

# Display any 5 digits
fig, axes = plt.subplots(1, 5, figsize=(8, 2))
for i, ax in enumerate(axes):
    ax.imshow(pixels[i].reshape(28, 28), cmap="gray")
    ax.set_title(labels[i])
    ax.axis("off")
plt.show()

# Normalize pixel values between 0 and 1
pixels = pixels / 255.0

x_train, x_test, y_train, y_test = train_test_split(pixels, labels, test_size=0.2, random_state=0)

# RBM feature extractor + Logistic Regression classifier
rbm = BernoulliRBM(n_components=100, learning_rate=0.05, n_iter=10, random_state=0)
classifier = LogisticRegression(max_iter=1000)
model = Pipeline([("rbm", rbm), ("logistic", classifier)])
model.fit(x_train, y_train)

predictions = model.predict(x_test)

print("Classification Report (Precision, Recall, F1 per digit):\n")
print(classification_report(y_test, predictions))
