import re
import pandas as pd

# Words and phrases that often show up in spam bios (all lowercase)
SPAM_PHRASES = [
    "dm for promo",
    "follow back",
    "link in bio",
    "earn money fast",
    "free gift",
    "free prizes",
]

# Each rule takes one profile (a row) and returns True if it looks suspicious.

def many_digits_in_username(row):
    # 4 or more digits in a row, like deal_hunter_83219
    return re.search(r"\d{4,}", row["username"]) is not None

def spam_bio(row):
    bio = str(row["bio"]).lower()
    return any(phrase in bio for phrase in SPAM_PHRASES)

def follows_too_many(row):
    # follows lots of people but has few followers
    return row["following"] >= 300 and row["following"] > 5 * max(row["followers"], 1)

def new_account(row):
    return row["account_age_days"] < 90

def posts_too_much(row):
    return row["posts_per_day"] > 20

def no_avatar(row):
    return row["has_avatar"] == 0

# A dictionary: the text on the left is shown to the user,
# the function on the right is the check
RULES = {
    "Username has 4+ digits": many_digits_in_username,
    "Spam words in bio": spam_bio,
    "Follows far more than followers": follows_too_many,
    "Account under 90 days old": new_account,
    "More than 20 posts per day": posts_too_much,
    "No profile picture": no_avatar,
}

# How many rules must trigger before we say "needs review"
THRESHOLD = 3


def check_profile(row):
    """Return the list of rule names that triggered for this profile."""
    return [name for name, rule in RULES.items() if rule(row)]


if __name__ == "__main__":
    df = pd.read_csv("data/profiles.csv")
    correct = 0

    for _, row in df.iterrows():
        reasons = check_profile(row)
        flagged = 1 if len(reasons) >= THRESHOLD else 0
        actual = int(row["is_bot"])
        if flagged == actual:
            correct += 1
        print(f"{row['username']:<22} signals={len(reasons)}  flagged={flagged}  actual={actual}")

    print()
    print(f"Matched the label on {correct} of {len(df)} profiles")