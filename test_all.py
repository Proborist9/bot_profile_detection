import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from gemma_judge import judge_profile

CSV_PATH = 'data/profiles.csv'
MAX_WORKERS = 10  # parallel API calls at once


def profile_to_text(row):
    avatar = 'yes' if row['has_avatar'] == '1' else 'no'
    return (
        'Username: ' + row['username'] + '\n'
        + 'Bio: ' + row['bio'] + '\n'
        + 'Followers: ' + row['followers'] + ', Following: ' + row['following'] + '\n'
        + 'Account age: ' + row['account_age_days'] + ' days, Posts: ' + row['posts'] + '\n'
        + 'Has profile picture: ' + avatar
    )


def evaluate_row(args):
    i, row = args
    label = 'bot' if row['is_bot'] == '1' else 'human'
    result = judge_profile(profile_to_text(row))
    return i, row['username'], label, result


def main():
    if not os.path.exists(CSV_PATH):
        print('Could not find', CSV_PATH, '- run git pull')
        return

    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    print(f'Testing {len(rows)} profiles in parallel (workers={MAX_WORKERS})...')

    tp = fp = tn = fn = unknown = 0
    mistakes = []
    results = [None] * len(rows)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(evaluate_row, (i, row)): i for i, row in enumerate(rows)}
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()

    for i, username, label, result in results:
        verdict = result['verdict']
        if verdict == 'unknown':
            unknown += 1
        elif verdict == 'bot' and label == 'bot':
            tp += 1
        elif verdict == 'bot' and label == 'human':
            fp += 1
        elif verdict == 'human' and label == 'human':
            tn += 1
        else:
            fn += 1

        if verdict != label:
            mistakes.append((username, label, verdict, result['confidence'], result['reasons']))

        print(i + 1, username, '| real:', label, '| gemma:', verdict, result['confidence'])

    total = tp + fp + tn + fn
    print()
    print('Bots caught (true positives):', tp)
    print('Humans wrongly flagged as bots (false positives):', fp)
    print('Humans correctly passed (true negatives):', tn)
    print('Bots missed (false negatives):', fn)
    print('Unknown (errors):', unknown)
    if total > 0:
        print('Accuracy:', round((tp + tn) / total * 100), '%')
    if tp + fp > 0:
        print('Precision (of flagged, how many were real bots):', round(tp / (tp + fp) * 100), '%')
    if tp + fn > 0:
        print('Recall (of real bots, how many caught):', round(tp / (tp + fn) * 100), '%')

    print()
    print('MISTAKES:')
    for name, lbl, verdict, conf, reasons in mistakes:
        print('-', name, '| real:', lbl, '| gemma:', verdict, conf)
        print('   ', reasons)


main()