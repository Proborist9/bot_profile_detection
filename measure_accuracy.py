import pandas as pd
from rules import score_rules

CUTOFF = 50  # predict "bot" at this score or higher

df = pd.read_csv("data/profiles.csv")
wrong = []

for _, row in df.iterrows():
    score = score_rules(row)
    predicted = 1 if score >= CUTOFF else 0
    actual = int(row["is_bot"])
    if predicted != actual:
        wrong.append((row["username"], score, actual))

correct = len(df) - len(wrong)
print(f"Accuracy: {correct}/{len(df)} = {correct / len(df):.1%}")
print()
print("Wrong predictions:")
if not wrong:
    print("  none")
for username, score, actual in wrong:
    kind = "bot" if actual == 1 else "human"
    print(f"  {username}: score {score}, actually a {kind}")