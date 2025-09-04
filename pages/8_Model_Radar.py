import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# ------------ Paths -------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE_DIR, "..", "Data")
MODEL_STATS = os.path.join(DATA, "model_stats", "model_stats.json")

st.title("Model Radar (Normalized Performance)")

# ------------ Guards -------------
if not os.path.exists(MODEL_STATS):
    st.warning(
        "Missing file: Data/model_stats/model_stats.json\n\n"
        "Run `python evaluate_models.py` to generate model metrics (MAE, RMSE, Binary Error)."
    )
    st.stop()

# ------------ Load metrics -------------
with open(MODEL_STATS, "r") as f:
    raw = json.load(f)

df = pd.DataFrame(raw).T.reset_index().rename(columns={"index": "Model"})

# Expecting columns: mae, rmse, bin_error
required_cols = {"mae", "rmse", "bin_error"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing columns in model stats: {', '.join(sorted(missing))}")
    st.stop()

# Keep only relevant columns + model name
df = df[["Model", "mae", "rmse", "bin_error"]].copy()

st.subheader("Raw Error Metrics")
st.dataframe(df.style.format({"mae": "{:.3f}", "rmse": "{:.3f}", "bin_error": "{:.3f}"}), use_container_width=True)

# ------------ Normalize errors to 0..1 then invert to 'Performance' -------------
# For each error metric: norm = (x - min) / (max - min). Then performance = 1 - norm
perf = df.copy()
for col in ["mae", "rmse", "bin_error"]:
    col_min = perf[col].min()
    col_max = perf[col].max()
    if col_max == col_min:
        # All equal -> give neutral 0.5 so it doesn't crash or mislead
        perf[col + "_perf"] = 0.5
    else:
        perf[col + "_perf"] = 1.0 - (perf[col] - col_min) / (col_max - col_min)

# Long-form for polar chart
radar = perf.melt(
    id_vars=["Model"],
    value_vars=["mae_perf", "rmse_perf", "bin_error_perf"],
    var_name="Metric",
    value_name="Performance"
)

metric_labels = {
    "mae_perf": "MAE (Performance)",
    "rmse_perf": "RMSE (Performance)",
    "bin_error_perf": "Binary Error (Performance)"
}
radar["Metric"] = radar["Metric"].map(metric_labels)

st.subheader("Radar Chart (Higher = Better)")
fig = px.line_polar(
    radar,
    r="Performance",
    theta="Metric",
    color="Model",
    line_close=True,
    range_r=[0, 1]
)
fig.update_traces(fill="toself")
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Each metric is min-max normalized across models, then inverted so that higher means better. "
    "This makes different error scales comparable on one radar."
)
