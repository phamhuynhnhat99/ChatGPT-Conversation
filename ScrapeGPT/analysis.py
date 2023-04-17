import pandas as pd

all_labels = ["Positive", "Negative", "Neutral", "Unknown"]

df = pd.read_csv("result.csv")

y_pred, y_true = list(df.predict)[-30:], list(df.label)[-30:]

check = []
for t, p in zip(y_true, y_pred):
    if t == p:
        check.append(1)
    else:
        check.append(0)
print(sum(check)/len(y_pred))

cm = dict()
for i in all_labels:
    cm[i] = dict()
    for j in all_labels:
        cm[i][j] = 0

for p, t in zip(y_pred, y_true):
    cm[p][t] += 1

confusion = pd.DataFrame()
for p in all_labels:
    confusion[p] = [cm[p][t] for t in all_labels]
confusion["all_labels"] = all_labels
confusion.set_index("all_labels", inplace=True)
confusion.to_csv("confusion.csv", index=True)
