import os
import sys
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from gemma_judge import judge_profile

load_dotenv()

CSV_PATH = 'data/profiles.csv'
WORKERS = 5

# Usage:
#   python3 test_all.py        -> all profiles
#   python3 test_all.py 16     -> quick test on 16 profiles (mixed bots and humans)
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else None


def profile_to_text(row):
    avatar = 'yes' if str(row.get('has_avatar', '0')) == '1' else 'no'
    bio = str(row.get('bio', ''))
    if bio.lower() == 'nan':
        bio = ''
    return (
        f"Username: {row['username']}\n"
        f"Bio: {bio}\n"
        f"Followers: {row['followers']}, Following: {row['following']}\n"
        f"Account age: {row['account_age_days']} days, Posts: {row['posts']}\n"
        f"Posts per day: {row.get('posts_per_day', '')}\n"
        f"Has profile picture: {avatar}"
    )
    


def judge_with_retry(text):
    for attempt in range(5):
        result = judge_profile(text)
        if result['verdict'] != 'unknown':
            return result
        # Check if rate limited
        reasons_str = ' '.join(result.get('reasons', []))
        if '429' in reasons_str or 'RESOURCE_EXHAUSTED' in reasons_str:
            time.sleep(10 * (attempt + 1))
        else:
            time.sleep(2)
    return result


def pick_rows(rows, limit):
    if limit is None or limit >= len(rows):
        return rows
    bots = [r for r in rows if r['is_bot'] == '1']
    humans = [r for r in rows if r['is_bot'] != '1']
    half = limit // 2
    return bots[:half] + humans[:limit - half]


def main():
    if not os.path.exists(CSV_PATH):
        print('Could not find', CSV_PATH, '- run git pull')
        return

    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    rows = pick_rows(rows, LIMIT)
    print('Testing', len(rows), 'profiles with', WORKERS, 'at a time...')
    start = time.time()

    texts = [profile_to_text(r) for r in rows]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(judge_with_retry, texts))

    tp = fp = tn = fn = unknown = 0
    mistakes = []
    for row, result in zip(rows, results):
        label = 'bot' if row['is_bot'] == '1' else 'human'
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
            mistakes.append((row['username'], label, verdict, result['confidence'], result['reasons']))

    total = tp + fp + tn + fn
    print()
    print('Finished in', round(time.time() - start), 'seconds')
    print('Bots caught (true positives):', tp)
    print('Humans wrongly flagged (false positives):', fp)
    print('Humans correctly passed (true negatives):', tn)
    print('Bots missed (false negatives):', fn)
    print('Unknown (errors):', unknown)
    if total > 0:
        print('Accuracy:', round((tp + tn) / total * 100), '%')
    if tp + fp > 0:
        print('Precision:', round(tp / (tp + fp) * 100), '%')
    if tp + fn > 0:
        print('Recall:', round(tp / (tp + fn) * 100), '%')

    print()
    print('MISTAKES:')
    for name, label, verdict, conf, reasons in mistakes:
        print('-', name, '| real:', label, '| gemma:', verdict, conf)
        print('   ', reasons)


if __name__ == '__main__':
    main()