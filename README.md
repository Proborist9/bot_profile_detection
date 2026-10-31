# Bot Profile Detector

Bot Profile Detector is a small web app that estimates how likely a social media profile is to be a fake or bot account. Fake accounts spread spam and scams, and they are hard to spot one at a time. The app combines two signals: a rule-based score (checks like follower ratio, account age and posting rate) and a judgement from the Gemma AI model. The two scores are averaged into one suspicion score from 0 to 100, and Gemma's verdict and reasons are shown next to it. This is a prototype built on fictional sample profiles.

## Team

- Jheel Santani: rules and dataset
- Saksham Mishra: Gemma judge
- Vritika Sheth: app, UI and demo

## How to run

1. Install the requirements:
   ```bash
   pip install streamlit google-genai pandas
   ```
2. Set your Gemini API key.
   - Mac/Linux: `export GEMINI_API_KEY="your-key-here"`
   - Windows PowerShell: `$env:GEMINI_API_KEY="your-key-here"`
3. Start the app:
   ```bash
   streamlit run app.py
   ```
4. Open http://localhost:8501, pick a demo profile from the dropdown, and click **Analyze**.

## Model

*Model used:* Gemma 4 (⁠ gemma-4-26b-a4b-it ⁠), accessed through the Gemini API with the ⁠ google-genai ⁠ Python SDK.

### What Gemma does in this project

Gemma is the "AI judge" half of the detector. For each profile, the app turns the profile fields (username, bio, follower and following counts, account age, post count, posts per day, profile picture yes/no) into a short block of text and asks Gemma whether the account looks more like a bot or a human. Gemma replies with JSON:

⁠ json
{"verdict": "bot", "confidence": 85, "reasons": ["Username ends in a long number", "Bio is a promotional spam phrase", "Follows far more accounts than follow it"]}
 ⁠

•⁠  ⁠⁠ verdict ⁠: ⁠ bot ⁠ or ⁠ human ⁠
•⁠  ⁠⁠ confidence ⁠: a whole number from 0 to 100
•⁠  ⁠⁠ reasons ⁠: short, profile-specific explanations that a person can check

### How the API is called

⁠python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


## How scoring works

Rule-based scoring (rules.py)
score_rules(row) starts at 0 and adds points for each suspicious signal. The total is capped at 100.
Rule	Points
Username has 4 or more digits	+20
No profile picture	+10
Account younger than 90 days	+15
More than 20 posts per day	+20
Following more than 3 times followers	+15
Bio is empty or contains a spam word	+15
A profile is predicted to be a bot when its score is 50 or higher.
profile_to_text(row) converts a profile into a readable text block that is sent to Gemma.
Accuracy
Measured with measure_accuracy.py on all 38 rows.
Rules-only accuracy: 36 / 38 = 94.7%.
Wrong predictions:
arjun2005: a human, wrongly flagged as a bot (the year in his username counted as digits).
tech_news_daily: a bot with a normal-looking bio, missed by the rules (score 20).
Limitation: the dataset is small and was written by the team, so this accuracy says little about real accounts. The output is a suspicion score, not a verdict on any real person.

The final score combines both signals:

1. **Rules score (0 to 100):** calculated from the profile fields.
2. **Gemma bot score (0 to 100):** Gemma returns a verdict and a confidence. If the verdict is "bot", the bot score is the confidence. Otherwise it is 100 minus the confidence.
3. **Final score:** (rules score + Gemma bot score) / 2.

## Dataset note

File: data/profiles.csv
Size: 38 labeled rows, roughly half bots (is_bot = 1) and half humans (is_bot = 0).
How it was made: written by hand by the team. All profiles are fictional sample data. No real accounts were scraped or copied.
Bot rows follow common patterns: usernames with many digits, spam bios ("DM for promo", "follow back", "link in bio", "earn money fast"), following far higher than followers, new accounts, very high posts per day, and no avatar.
Human rows have real-sounding names, specific bios, balanced followers and following, older accounts, and normal posting rates.
A few tricky rows were added on purpose, for example a human with no avatar and a bot with a decent-looking bio.

All profiles in this project are fictional samples made for this demo. They do not describe any real account.

## Limitations and ethics

- The dataset is very small, so the rules have not been tested on real data.
- Gemma can be wrong or overconfident, and its answers may differ between runs.
- Both the rules and the model rely on surface signals. A real person with an unusual profile can look suspicious, and a careful bot can look normal.
- The app produces a suspicion score, not a verdict. It must not be used to make decisions about real people or accounts.
