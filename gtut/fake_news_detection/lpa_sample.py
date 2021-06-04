from sklearn import datasets
from sklearn import semi_supervised
import numpy as np

d = datasets.load_iris()
X = d.data.copy()
print(X)
y = d.target.copy()
print(y)
names = d.target_names.copy()
print(names)
names = np.append(names, ['unlabeled'])
print(names)
y[np.random.choice([True, False], len(y))] = -1
print(y)
print(names[y])

# label propagation
lp = semi_supervised.LabelPropagation()
print(lp.fit(X, y))
preds = lp.predict(X)
print(preds)
print(y)
print(np.mean(preds == d.target))

# label spreading
# ls = semi_supervised.LabelSpreading()
# print(ls.fit(X, y))
# print(np.mean(ls.predict(X) == d.target))
