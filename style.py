import streamlit as st

CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2rem; max-width: 960px;}
.hero h1 {font-size: 2.4rem; font-weight: 800; margin-bottom: 0.2rem;}
.hero p {color: #94A3B8; font-size: 1.05rem; margin-top: 0;}
.card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.score-number {font-size: 3.5rem; font-weight: 800; line-height: 1;}
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
}
.badge-bot {background: #7F1D1D; color: #FECACA;}
.badge-human {background: #14532D; color: #BBF7D0;}
.badge-unsure {background: #713F12; color: #FDE68A;}
.reason {padding: 0.35rem 0; color: #CBD5E1;}
.disclaimer {
    font-size: 0.85rem;
    color: #94A3B8;
    border-left: 3px solid #F59E0B;
    padding-left: 0.75rem;
}
</style>
"""


def apply_theme():
    # Must be the first Streamlit command in app.py.
    st.set_page_config(page_title="Bot Profile Detector", page_icon="🛡️", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)


def hero():
    st.markdown(
        '<div class="hero"><h1>Bot Profile Detector</h1>'
        '<p>Estimates how likely a profile is to be a fake or bot account.</p></div>',
        unsafe_allow_html=True,
    )


def verdict_badge(score):
    # These cut-offs are design choices, not measured results. Change them later
    # once your held-out test tells you where the boundaries should be.
    if score >= 70:
        return '<span class="badge badge-bot">Likely bot</span>'
    if score <= 30:
        return '<span class="badge badge-human">Likely human</span>'
    return '<span class="badge badge-unsure">Unclear</span>'


def score_card(final_score, rules_score, gemma_score):
    st.markdown(
        f'<div class="card">'
        f'<div class="score-number">{final_score:.0f}</div>'
        f'<p style="color:#94A3B8;margin:0.25rem 0 0.75rem 0;">Suspicion score (0 to 100)</p>'
        f'{verdict_badge(final_score)}'
        f'</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    col1.metric("Rules score", f"{rules_score:.0f}")
    col2.metric("Gemma score", f"{gemma_score:.0f}")


def reasons_card(reasons):
    items = "".join(f'<div class="reason">• {reason}</div>' for reason in reasons)
    st.markdown(f'<div class="card"><strong>Why</strong>{items}</div>', unsafe_allow_html=True)


def disclaimer():
    st.markdown(
        '<p class="disclaimer">This is a suspicion score on fictional sample profiles, '
        'not a verdict on any real account.</p>',
        unsafe_allow_html=True,
    )

