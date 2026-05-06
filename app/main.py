import streamlit as st
import pandas as pd
import os

from graph_builder import build_network

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="BCL2 Network Explorer",
    layout="wide"
)

# =========================================
# TITLE
# =========================================

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

files = sorted([
    f for f in os.listdir(data_folder)
    if f.endswith(".xlsx")
])

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

file_path = os.path.join(
    data_folder,
    selected_file
)

# =========================================
# LOAD EXCEL FILE
# =========================================

try:

    # =====================================
    # READ SHEETS
    # =====================================

    df_main = pd.read_excel(
        file_path,
        sheet_name=0
    )

    df_cross = pd.read_excel(
        file_path,
        sheet_name=1
    )

    # =====================================
    # FILE INFO
    # =====================================

    st.subheader("Selected File")
    st.write(selected_file)

    # =====================================
    # MAIN CHAIN TABLE
    # =====================================

    st.subheader("Sheet 1: Main Chain Relations")

    st.write(f"Rows: {len(df_main)}")

    st.dataframe(
        df_main.head(),
        use_container_width=True
    )

    # =====================================
    # CROSS PATHWAY TABLE
    # =====================================

    st.subheader("Sheet 2: Cross Pathway Nodes")

    st.write(f"Rows: {len(df_cross)}")

    st.dataframe(
        df_cross.head(),
        use_container_width=True
    )

    # =====================================
    # CROSS NODE OPTION
    # =====================================

    include_cross_nodes = st.checkbox(
        "Include Cross Pathway Nodes",
        value=True
    )

    # =====================================
    # GRAPH SECTION
    # =====================================

    st.subheader("Network Visualization")

    html_graph = build_network(
        df_main,
        df_cross,
        include_cross_nodes
    )

    st.components.v1.html(
        html_graph,
        height=950,
        scrolling=True
    )

# =========================================
# ERROR HANDLING
# =========================================

except Exception as e:

    st.error("Error loading or visualizing file")

    st.exception(e)
