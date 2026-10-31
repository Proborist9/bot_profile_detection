import streamlit as st
from rules import score_rules, profile_to_text
from gemma_judge import judge_profile

st.title("Bot Profile Detector")
st.caption("Sample detection only. This is a suspicion score, not a verdict on any real account.")

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

    # temporary: shows exactly what Gemma returned

    if gemma["verdict"] == "unknown":
        st.warning("Gemma could not give an answer. Showing the rules score only.")
        gemma_bot_score = None
        final_score = rules_score
    else:
        if gemma["verdict"] == "bot":
            gemma_bot_score = gemma["confidence"]
        else:
            gemma_bot_score = 100 - gemma["confidence"]
        final_score = (rules_score + gemma_bot_score) / 2
    if final_score >= 65:
        st.error(f"Likely a bot (suspicion {final_score:.0f}/100)")
    elif final_score <= 35:
        st.success(f"Likely a human (suspicion {final_score:.0f}/100)")
    else:
        st.warning(f"Unclear, in the middle (suspicion {final_score:.0f}/100)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rules score", f"{rules_score:.0f}")
    col2.metric("Gemma bot score", "n/a" if gemma_bot_score is None else f"{gemma_bot_score:.0f}")
    col3.metric("Final score", f"{final_score:.0f}")
    st.write("Gemma's verdict:", gemma["verdict"])
    for reason in gemma["reasons"]:
        st.write("- " + reason)
    st.caption("Sample detection only. This is a suspicion score, not a verdict on any real account.")        