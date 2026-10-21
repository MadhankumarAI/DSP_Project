"""
Experiment 4: RBM + Precision & Recall
1) Load MNIST handwritten digit dataset & display any 5 sample images
2) Preprocess dataset by normalising pixel values b/w 0 & 1, splitting
   data into training & testing sets
3) Implement Restricted Boltzmann Machine. Use logistic regression
   classifier with RBM feature to classify handwritten digits 0-9
4) Generate classification report showing precision, recall, F1-score
   for each digit
5) Display some RBM-reconstructed handwritten digits & compare them
   with original image
"""
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist
from sklearn.model_selection import train_test_split
from sklearn.neural_network import BernoulliRBM
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

(xtr,ytr),(xte,yte)=mnist.load_data()
pixels=np.concatenate((xtr,xte))
labels=np.concatenate((ytr,yte))
pixels=pixels.reshape(-1,784).astype("float32")

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

# Step 5: RBM-reconstructed digits vs originals.
# Use the deterministic mean-field pass P(h|v) then P(v|h) (sigmoid probabilities),
# NOT rbm.gibbs() - gibbs() draws stochastic binary 0/1 samples, which look like
# noisy dots rather than a clean reconstruction of the original grayscale digit.
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

fitted_rbm = model.named_steps["rbm"]
hidden_probs = sigmoid(x_test[:5] @ fitted_rbm.components_.T + fitted_rbm.intercept_hidden_)
rec = sigmoid(hidden_probs @ fitted_rbm.components_ + fitted_rbm.intercept_visible_)

print("og")
fig,axes=plt.subplots(1,5,figsize=(15,15))
for i,ax in enumerate(axes):
  ax.imshow(xte[i].reshape(28,28),cmap="gray")
  ax.set_title(yte[i])
plt.show()

print("rec")
fig,axes=plt.subplots(1,5,figsize=(15,15))
for i,ax in enumerate(axes):
  ax.imshow(rec[i].reshape(28,28),cmap="gray")
  ax.set_title(yte[i])
plt.show()
