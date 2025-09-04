import streamlit as st

st.set_page_config(page_title="NBA Elo Dashboard", layout="wide")

st.title("NBA Elo Ratings Dashboard")
st.markdown("""
Welcome! Use the left sidebar or the tabs above (if using `pages/`) to explore:

- Elo progression by team and season
- Elo vs. win percentage
- Model leaderboard
- Playoff predictions and champion accuracy
""")
