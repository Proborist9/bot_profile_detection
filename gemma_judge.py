import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# The .env file sits next to this file, so the key is found no matter which
# folder you run the app or tests from.
ENV_PATH = Path(__file__).resolve().with_name('.env')

# override=True is important: an empty or placeholder GEMINI_API_KEY exported in
# the shell must never shadow the real key saved in .env. The .env file is the
# single source of truth, so the key only has to be set once.
load_dotenv(dotenv_path=ENV_PATH, override=True)

MODEL = 'gemma-4-26b-a4b-it'
MIN_KEY_LENGTH = 20


def _get_api_key():
    api_key = (os.environ.get('GEMINI_API_KEY') or '').strip().strip('"').strip("'")
    if len(api_key) < MIN_KEY_LENGTH or 'api_key' in api_key.lower():
        raise EnvironmentError(
            'GEMINI_API_KEY is missing or looks like a placeholder. '
            f'Put your real key in {ENV_PATH} on a line like:\n'
            'GEMINI_API_KEY=your-key-here\n'
            'Get a key from https://aistudio.google.com/apikey'
        )
    return api_key


def validate_setup():
    """Raise a clear error if the API key is missing.

    Call this before a long run so the job fails in a second instead of
    silently returning errors for every profile.
    """
    return _get_api_key()


@lru_cache(maxsize=1)
def _get_client():
    return genai.Client(api_key=_get_api_key())


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
