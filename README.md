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

[Person B: paste the model section here. It should include the model name: gemma-4-26b-a4b-it via the Gemini API.]

## How scoring works

[Person A: paste the scoring explanation here, including the rules and their weights.]

The final score combines both signals:

1. **Rules score (0 to 100):** calculated from the profile fields.
2. **Gemma bot score (0 to 100):** Gemma returns a verdict and a confidence. If the verdict is "bot", the bot score is the confidence. Otherwise it is 100 minus the confidence.
3. **Final score:** (rules score + Gemma bot score) / 2.

## Dataset note

[Person A: paste the dataset note here.]

All profiles in this project are fictional samples made for this demo. They do not describe any real account.

## Limitations and ethics

- The dataset is very small, so the rules have not been tested on real data.
- Gemma can be wrong or overconfident, and its answers may differ between runs.
- Both the rules and the model rely on surface signals. A real person with an unusual profile can look suspicious, and a careful bot can look normal.
- The app produces a suspicion score, not a verdict. It must not be used to make decisions about real people or accounts.
