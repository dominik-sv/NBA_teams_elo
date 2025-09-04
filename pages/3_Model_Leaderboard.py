import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
MODEL_STATS = os.path.join(DATA, "model_stats", "model_stats.json")

# Load stats
with open(MODEL_STATS) as f:
    stats = json.load(f)

df = pd.DataFrame(stats).T
df = df[["mae", "rmse", "bin_error"]].copy()
df["Score"] = df["mae"] + df["rmse"] + df["bin_error"]
df = df.sort_values("Score").reset_index().rename(columns={"index": "Model"})

# Descriptions (tooltips)
model_descriptions = {
    "elo_basic": "Classic Elo, no margin or home bonus",
    "elo_margin": "Elo + margin of victory multiplier",
    "elo_home_adv": "Elo + home court advantage",
    "elo_updK_end": "Elo with rising K as season ends",
    "elo_updK_start": "Elo with falling K as season ends",
    "elo_transfer_elo": "Elo transferred from last season with decay",
    "win_rate": "Based on regular season win %",
    "net_rating": "Based on net points per game"
}
df["Description"] = df["Model"].map(model_descriptions)

# Display text and table
st.title("Model Leaderboard")
st.markdown("Each model is evaluated based on:")
st.markdown("""
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **Binary Error** (wrong playoff prediction)
- Combined **Score** = MAE + RMSE + Binary Error
""")

st.dataframe(
    df[["Model", "Description", "mae", "rmse", "bin_error", "Score"]]
    .style.format({col: "{:.3f}" for col in ["mae", "rmse", "bin_error", "Score"]})
    .highlight_min(color="lightgreen", axis=0, subset=["mae", "rmse", "bin_error", "Score"])
)

# Chart
st.subheader("Error Comparison Chart")

melt_df = df.melt(id_vars=["Model"], value_vars=["mae", "rmse", "bin_error"], var_name="Metric", value_name="Value")
fig = px.bar(melt_df, x="Model", y="Value", color="Metric", barmode="group", title="Model Error Breakdown")
st.plotly_chart(fig, use_container_width=True)
