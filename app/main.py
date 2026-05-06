import streamlit as st
import pandas as pd
import os

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="BCL2 Network Explorer",
    layout="wide"
)

st.title("BCL2 Network Explorer")

# =========================================
# SELECT NETWORK TYPE
# =========================================

network_type = st.sidebar.radio(
    "Select Network Type",
    ["Upstream", "Downstream"]
)

# =========================================
# FOLDER PATHS
# =========================================

if network_type == "Upstream":
    data_folder = "data/upstream"
else:
    data_folder = "data/downstream"

# =========================================
# GET FILE LIST
# =========================================

files = [
    f for f in os.listdir(data_folder)
    if f.endswith(".xlsx")
]

# =========================================
# FILE SELECTOR
# =========================================

selected_file = st.sidebar.selectbox(
    "Select Pathway File",
    files
)

# =========================================
# FULL FILE PATH
# =========================================

file_path = os.path.join(data_folder, selected_file)

# =========================================
# LOAD EXCEL SHEETS
# =========================================

try:

    df_main = pd.read_excel(
        file_path,
        sheet_name=0
    )

    df_cross = pd.read_excel(
        file_path,
        sheet_name=1
    )

    # =====================================
    # DISPLAY INFO
    # =====================================

    st.subheader("Selected File")
    st.write(selected_file)

    # =====================================
    # MAIN CHAIN
    # =====================================

    st.subheader("Sheet 1: Main Chain Relations")

    st.write(f"Rows: {len(df_main)}")
    st.dataframe(df_main.head())

    # =====================================
    # CROSS PATHWAY
    # =====================================

    st.subheader("Sheet 2: Cross Pathway Nodes")

    st.write(f"Rows: {len(df_cross)}")
    st.dataframe(df_cross.head())

except Exception as e:

    st.error("Error loading file")
    st.exception(e)
