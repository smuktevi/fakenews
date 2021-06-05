import json
import pathlib
import os
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

if __name__ == "__main__":
    with open('metadata/phase3_labels.json', 'r') as fp:
        phase3_labels = json.load(fp)

    true_labels = {}

    data_dir = pathlib.Path("../small_dataset/politifact")

    for label in ['fake', 'real']:
        label_dir = data_dir / label

        for article in os.listdir(label_dir):
            if label == 'fake':
                true_labels[article] = 1
            else:
                true_labels[article] = 0

    articles = sorted(list(phase3_labels.keys()))
    preds = np.array([phase3_labels[article] for article in articles])
    true = np.array([true_labels[article] for article in articles])

    accuracy = accuracy_score(preds, true)
    precision = precision_score(preds, true)
    recall = recall_score(preds, true)
    print(confusion_matrix(preds, true))
    print(f"GTUT produces predictions with an accuracy of {round(accuracy, 5)}")
    print(f"Precision of {round(precision, 5)}")
    print(f"Recall of {round(accuracy, 5)}")
