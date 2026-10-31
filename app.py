import streamlit as st

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
    st.metric("Final score", 50)