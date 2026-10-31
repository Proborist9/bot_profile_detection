import os
import pandas as pd
from gemma_judge import judge_profile
from rules import profile_to_text

CSV_PATH = 'data/profiles.csv'
SAMPLE_SIZE = 5


def main():
    if not os.path.exists(CSV_PATH):
        print('Could not find data/profiles.csv. Ask Person A to push it, then run git pull.')
        return

    df = pd.read_csv(CSV_PATH)

    # Pick a mix: the first few rows usually include both bots and humans.
    rows = list(df.head(SAMPLE_SIZE).iterrows())

    correct = 0
    for i, (_, row) in enumerate(rows, start=1):
        label = 'bot' if row['is_bot'] == 1 else 'human'
        result = judge_profile(profile_to_text(row))
        match = result['verdict'] == label
        if match:
            correct += 1

        print(f"--- Profile {i}: {row['username']}")
        print(f"    Real label:  {label}")
        print(f"    Gemma says:  {result['verdict']} (confidence {result['confidence']})")
        print(f"    Reasons:     {result['reasons']}")
        print(f"    Match:       {'YES' if match else 'NO'}")

    print()
    print(f"Gemma matched {correct} out of {len(rows)} profiles.")


if __name__ == '__main__':
    main()