"""Minimal Streamlit dashboard for the recorded violations."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd
import streamlit as st

from trafficguard.storage.repository import ViolationRepository

st.set_page_config(page_title="AI Traffic Guard", layout="wide")

repo = ViolationRepository(db_path="data/trafficguard.db")
records = repo.list_all()
if records:
    df = pd.DataFrame([r.__dict__ for r in records])
    df = df.drop(columns=["_sa_instance_state"], errors="ignore")
else:
    df = pd.DataFrame(columns=["id", "violation_type", "vehicle_class", "track_id", "plate_text", "plate_confidence", "timestamp", "frame_number", "camera_id", "evidence_image_path", "plate_crop_path", "created_at"])

st.title("AI Traffic Guard")
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total violations", len(df))
col2.metric("No helmet", int((df["violation_type"] == "no_helmet").sum()) if not df.empty else 0)
col3.metric("Red light", int((df["violation_type"] == "red_light").sum()) if not df.empty else 0)
col4.metric("Unique vehicles", int(df["track_id"].nunique()) if not df.empty else 0)

st.dataframe(df, use_container_width=True)

if not df.empty:
    st.download_button(
        label="Export CSV",
        data=df.to_csv(index=False),
        file_name="violations.csv",
        mime="text/csv",
    )
