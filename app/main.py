import streamlit as st
import pandas as pd
import os

from graph_builder import build_network
from node_metadata import build_node_metadata

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

st.markdown("""
Interactive visualization of pathway-specific  
upstream and downstream BCL2 interaction chains.
""")

# =========================================
# SIDEBAR
# =========================================

st.sidebar.header("Network Controls")

# =========================================
# NETWORK TYPE
# =========================================

network_type = st.sidebar.radio(
    "Select Network Type",
    ["Upstream", "Downstream"]
)

# =========================================
# DATA PATH
# =========================================

if network_type == "Upstream":
    data_folder = "data/upstream"
else:
    data_folder = "data/downstream"

# =========================================
# FILE LIST
# =========================================

files = sorted([
    f for f in os.listdir(data_folder)
    if f.endswith(".xlsx")
])

# =========================================
# FILE SELECTION
# =========================================

selected_file = st.sidebar.selectbox(
    "Select Pathway File",
    files
)

# =========================================
# CROSS NODE OPTION
# =========================================

include_cross_nodes = st.sidebar.checkbox(
    "Include Cross Pathway Nodes",
    value=False
)

# =========================================
# FULL FILE PATH
# =========================================

file_path = os.path.join(
    data_folder,
    selected_file
)

# =========================================
# LOAD DATA
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
    # BUILD NODE METADATA
    # =====================================

    metadata = build_node_metadata(
        df_main,
        df_cross
    )

    # =====================================
    # SIDEBAR NODE SEARCH
    # =====================================

    all_nodes = sorted(metadata.keys())

    selected_node = st.sidebar.selectbox(
        "Search Node ID",
        ["None"] + all_nodes
    )

    # =====================================
    # FILE INFO
    # =====================================

    st.subheader("Selected File")

    st.info(selected_file)

    # =====================================
    # NETWORK STATS
    # =====================================

    total_main_edges = len(df_main)

    total_cross_edges = len(df_cross)

    total_nodes = len(metadata)

    gene_nodes = sum(
        1 for n in metadata.values()
        if n["type"] == "Gene"
    )

    cross_nodes = sum(
        1 for n in metadata.values()
        if n["cross_node"]
    )

    # =====================================
    # METRIC DISPLAY
    # =====================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Main Edges", total_main_edges)

    col2.metric("Cross Edges", total_cross_edges)

    col3.metric("Total Nodes", total_nodes)

    col4.metric("Gene Nodes", gene_nodes)

    col5.metric("Cross Nodes", cross_nodes)

    # =====================================
    # NODE DETAILS PANEL
    # =====================================

    if selected_node != "None":

        st.subheader("Selected Node Metadata")

        node_info = metadata[selected_node]

        st.json({
            "Node_ID": selected_node,
            "Type": node_info["type"],
            "Connections": node_info["connections"],
            "Cross_Pathway_Node": node_info["cross_node"]
        })

    # =====================================
    # MAIN CHAIN TABLE
    # =====================================

    with st.expander("Sheet 1: Main Chain Relations"):

        st.write(f"Rows: {len(df_main)}")

        st.dataframe(
            df_main,
            use_container_width=True
        )

    # =====================================
    # CROSS PATHWAY TABLE
    # =====================================

    with st.expander("Sheet 2: Cross Pathway Nodes"):

        st.write(f"Rows: {len(df_cross)}")

        st.dataframe(
            df_cross,
            use_container_width=True
        )

    # =====================================
    # LEGEND
    # =====================================

    st.subheader("Network Legend")

    st.markdown("""
    - 🟢 / Cyan → Gene Nodes  
    - 🔵 → Protein / General Nodes  
    - 🩷 → Cross Pathway Nodes  

    Edge Colors:
    - Green → Activation  
    - Red → Inhibition  
    - Blue → Expression  
    - Gray → Other / Cross Pathway  
    """)

    # =====================================
    # GRAPH SECTION
    # =====================================

    st.subheader("Interactive Network Visualization")

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

    st.error("Error loading or visualizing network")

    st.exception(e)
