import streamlit as st
import pandas as pd
import os

from graph_builder import build_network
from node_metadata import build_node_metadata

from ui_components import (
    render_header,
    render_legend
)

from relation_explorer import (
    render_relation_explorer
)


# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="BCL2 Explorer",
    layout="wide"
)


# =========================================
# HEADER
# =========================================

render_header()


# =========================================
# SIDEBAR
# =========================================

st.sidebar.header(
    "Explorer Controls"
)

network_type = st.sidebar.radio(
    "Network Type",
    ["Upstream", "Downstream"]
)

if network_type == "Upstream":
    data_folder = "data/upstream"
else:
    data_folder = "data/downstream"


# =========================================
# FILES
# =========================================

files = sorted([
    f for f in os.listdir(data_folder)
    if f.endswith(".xlsx")
])

selected_file = st.sidebar.selectbox(
    "Pathway File",
    files
)

include_cross_nodes = st.sidebar.checkbox(
    "Include Cross Pathway Nodes",
    value=False
)


# =========================================
# FILE PATH
# =========================================

file_path = os.path.join(
    data_folder,
    selected_file
)


# =========================================
# LOAD DATA
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

    metadata = build_node_metadata(
        df_main,
        df_cross
    )

    # =====================================
    # NODE SELECTOR
    # =====================================

    all_nodes = sorted(
        metadata.keys()
    )

    selected_node = st.sidebar.selectbox(
        "Select Node ID",
        all_nodes
    )

    # =====================================
    # LAYOUT
    # =====================================

    graph_col, info_col = st.columns(
        [2.3, 1]
    )

    # =====================================
    # GRAPH PANEL
    # =====================================

    with graph_col:

        st.subheader(
            "Interactive Biological Network"
        )

        html_graph = build_network(
            df_main,
            df_cross,
            include_cross_nodes,
            selected_node
        )

        st.components.v1.html(
            html_graph,
            height=950,
            scrolling=True
        )

    # =====================================
    # METADATA PANEL
    # =====================================

    with info_col:

        st.subheader(
            "Biological Annotation Explorer"
        )

        node_info = metadata[selected_node]

        st.markdown(
            "## Node Information"
        )

        st.code(selected_node)

        st.write(
            f"Type: {node_info['type']}"
        )

        st.write(
            f"Connections: {node_info['connections']}"
        )

        st.write(
            f"Cross Pathway: {node_info['cross_node']}"
        )

        st.markdown("---")

        st.markdown("## KEGG IDs")

        for kid in node_info[
            "kegg_ids"
        ]:

            st.code(kid)

        st.markdown("---")

        st.markdown(
            "## Biological Metadata"
        )

        if node_info[
            "biological_data"
        ]:

            for idx, item in enumerate(
                node_info[
                    "biological_data"
                ]
            ):

                with st.expander(
                    f"Metadata {idx + 1}"
                ):

                    st.write(
                        "### Names"
                    )

                    st.write(
                        item.get(
                            "Names",
                            ""
                        )
                    )

                    st.write(
                        "### HSA Symbols"
                    )

                    st.write(
                        item.get(
                            "HSA_Symbols",
                            ""
                        )
                    )

                    st.write(
                        "### GO IDs"
                    )

                    st.write(
                        item.get(
                            "GO_IDs",
                            ""
                        )
                    )

                    st.write(
                        "### GO Labels"
                    )

                    st.write(
                        item.get(
                            "GO_Labels",
                            ""
                        )
                    )

                    st.write(
                        "### UniProt IDs"
                    )

                    st.write(
                        item.get(
                            "UniProt_IDs",
                            ""
                        )
                    )

        render_relation_explorer(
            selected_node,
            df_main,
            df_cross
        )

        render_legend()

except Exception as e:

    st.error(
        "Error loading explorer"
    )

    st.exception(e)
