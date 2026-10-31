import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()  # automatically loads GEMINI_API_KEY from .env file

MODEL = 'gemma-4-26b-a4b-it'

def _get_client():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Run: export GEMINI_API_KEY='your_key_here'"
        )
    return genai.Client(api_key=api_key)

PROMPT_TEMPLATE = """You are helping spot likely bot accounts on a social media platform.
Look at the profile below and decide if it is more likely a bot or a human.
A missing profile picture alone does not prove a bot.
Judge using the username pattern, bio, follower and following counts, account age, and posting rate.

Profile:
{profile_text}

Reply with JSON only. No extra words. No code fences. Use exactly this shape:
{{"verdict": "bot" or "human", "confidence": a whole number from 0 to 100, "reasons": ["short reason", "short reason"]}}
"""


def clean_json_text(text):
    start, end = text.find('{'), text.rfind('}')
    return text[start:end + 1] if start != -1 and end != -1 else text.strip()


def judge_profile(profile_text):
    prompt = PROMPT_TEMPLATE.format(profile_text=profile_text)
    try:
        client = _get_client()
        response = client.models.generate_content(model=MODEL, contents=prompt)
        data = json.loads(clean_json_text(response.text))

        verdict = str(data.get('verdict', 'unknown')).lower()
        if verdict not in ('bot', 'human'):
            verdict = 'unknown'

        confidence = int(data.get('confidence', 0))
        confidence = max(0, min(100, confidence))

        reasons = data.get('reasons', [])
        if not isinstance(reasons, list):
            reasons = [str(reasons)]

        return {
            'verdict': verdict,
            'confidence': confidence,
            'reasons': [str(reason) for reason in reasons],
        }
    except Exception as error:
        return {
            'verdict': 'unknown',
            'confidence': 0,
            'reasons': ['could not get a valid answer: ' + str(error)],
        }


if __name__ == '__main__':
    sample = """Username: deal_hunter_83219
Bio: DM for promo
Followers: 40, Following: 900
Account age: 12 days, Posts: 300
Has profile picture: no"""
    print(judge_profile(sample))