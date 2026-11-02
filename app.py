import streamlit as st
from rules import score_rules, profile_to_text
from gemma_judge import judge_profile
from style import apply_theme, hero, score_card, reasons_card, disclaimer

apply_theme()  # must come first, before any other st. call
hero()

username = st.text_input("Username")
bio = st.text_area("Bio")
followers = st.number_input("Followers", min_value=0, step=1)
following = st.number_input("Following", min_value=0, step=1)
account_age_days = st.number_input("Account age (days)", min_value=0, step=1)
posts = st.number_input("Posts", min_value=0, step=1)
posts_per_day = st.number_input("Posts per day", min_value=0.0, step=0.1)
has_profile_picture = st.checkbox("Has profile picture", value=True)

if st.button("Analyze"):
    profile = {
        "username": username,
        "bio": bio,
        "followers": followers,
        "following": following,
        "account_age_days": account_age_days,
        "posts": posts,
        "posts_per_day": posts_per_day,
        "has_avatar": int(has_profile_picture),
    }

    rules_score = score_rules(profile)
    gemma = judge_profile(profile_to_text(profile))

    if gemma["verdict"] == "unknown":
        st.warning("Gemma could not give an answer. Showing the rules score only.")
        gemma_bot_score = 0
        final_score = rules_score
    else:
        if gemma["verdict"] == "bot":
            gemma_bot_score = gemma["confidence"]
        else:
            gemma_bot_score = 100 - gemma["confidence"]
        final_score = (rules_score + gemma_bot_score) / 2

    # Results section using style helpers
    score_card(final_score, rules_score, gemma_bot_score)
    reasons_card(gemma.get("reasons", []))
    disclaimer()
