import json
import pathlib
import os


if __name__ == "__main__":
    with open('metadata/phase2_labels.json', 'r') as f:
        dta = json.load(f)

    true_labels = {}


    data_dir = pathlib.Path("../small_dataset/politifact")

    for label in ['real', 'fake']:
        label_dir = data_dir / label

        for article in os.listdir(label_dir):
            if label == 'real':
                true_labels[article] = 0
            else:
                true_labels = 1



