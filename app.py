import os
import streamlit as st
from rules import score_rules, profile_to_text
from gemma_judge import judge_profile

def to_number(text, default=0.0):
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def load_demos():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "demo_profiles.txt")
    demos = {}
    try:
        text = open(path, encoding="utf-8").read().strip()
    except FileNotFoundError:
        return demos

    for block in text.split("---"):
        fields = {}
        for line in block.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip().lower()] = value.strip()
        if not fields:
            continue

        picture = fields.get("has profile picture", "").lower()
        name = fields.get("username", "Profile")
        demos[name] = {
            "username": fields.get("username", ""),
            "bio": fields.get("bio", ""),
            "followers": int(to_number(fields.get("followers"))),
            "following": int(to_number(fields.get("following"))),
            "account_age_days": int(to_number(fields.get("account age"))),
            "posts": int(to_number(fields.get("posts"))),
            "posts_per_day": to_number(fields.get("posts per day")),
            "has_avatar": 1 if picture in ("yes", "y", "true", "1") else 0,
        }
    return demos


DEMOS = load_demos()

DEFAULTS = {
    "username": "",
    "bio": "",
    "followers": 0,
    "following": 0,
    "account_age_days": 0,
    "posts": 0,
    "posts_per_day": 0.0,
    "has_profile_picture": True,
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)
def load_demo():
    choice = st.session_state["demo_choice"]
    if choice in DEMOS:
        d = DEMOS[choice]
        st.session_state["username"] = d["username"]
        st.session_state["bio"] = d["bio"]
        st.session_state["followers"] = d["followers"]
        st.session_state["following"] = d["following"]
        st.session_state["account_age_days"] = d["account_age_days"]
        st.session_state["posts"] = d["posts"]
        st.session_state["posts_per_day"] = d["posts_per_day"]
        st.session_state["has_profile_picture"] = bool(d["has_avatar"])

st.title("Bot Profile Detector")
st.caption("Sample detection only. This is a suspicion score, not a verdict on any real account.")

st.selectbox(
    "Load a demo profile",
    ["(choose one)"] + list(DEMOS.keys()),
    key="demo_choice",
    on_change=load_demo,
)

username = st.text_input("Username", key="username")
bio = st.text_area("Bio", key="bio")
followers = st.number_input("Followers", min_value=0, step=1, key="followers")
following = st.number_input("Following", min_value=0, step=1, key="following")
account_age_days = st.number_input("Account age (days)", min_value=0, step=1, key="account_age_days")
posts = st.number_input("Posts", min_value=0, step=1, key="posts")
posts_per_day = st.number_input("Posts per day", min_value=0.0, step=0.1, key="posts_per_day")
has_profile_picture = st.checkbox("Has profile picture", key="has_profile_picture")

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
    with st.expander("Raw Gemma JSON"):
        st.json(gemma)
    st.caption("Sample detection only. This is a suspicion score, not a verdict on any real account.")        