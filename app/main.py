import streamlit as st
import pandas as pd
import os

from graph_builder import build_network
from node_metadata import build_node_metadata

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="BCL2 Biological Network Explorer",
    layout="wide"
)

# =========================================
# TITLE
# =========================================

st.title("BCL2 Biological Network Explorer")

st.markdown("""
Interactive pathway-specific upstream and downstream  
BCL2 interaction network explorer.
""")

# =========================================
# SIDEBAR CONTROLS
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
# DATA FOLDER
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
# FILE SELECTOR
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
# LOAD FILES
# =========================================

try:

    # =====================================
    # READ EXCEL SHEETS
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
    # MAIN LAYOUT
    # =====================================

    left_col, right_col = st.columns(
        [2.3, 1]
    )

    # =====================================
    # LEFT SIDE = GRAPH
    # =====================================

    with left_col:

        st.subheader(
            "Interactive Network Visualization"
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
    # RIGHT SIDE = BIOLOGICAL EXPLORER
    # =====================================

    with right_col:

        st.subheader(
            "Biological Annotation Explorer"
        )

        node_info = metadata[selected_node]

        # =================================
        # BASIC NODE INFO
        # =================================

        st.markdown("## Node Information")

        st.write("### Node ID")
        st.code(selected_node)

        st.write("### Node Type")
        st.write(node_info["type"])

        st.write("### Connections")
        st.write(node_info["connections"])

        st.write("### Cross Pathway Node")
        st.write(node_info["cross_node"])

        # =================================
        # KEGG IDS
        # =================================

        st.markdown("---")

        st.markdown("## KEGG IDs")

        if node_info["kegg_ids"]:

            for kid in node_info["kegg_ids"]:

                st.code(kid)

        else:

            st.info(
                "No KEGG IDs found"
            )

        # =================================
        # BIOLOGICAL METADATA
        # =================================

        st.markdown("---")

        st.markdown(
            "## Biological Metadata"
        )

        if node_info["biological_data"]:

            for idx, item in enumerate(
                node_info["biological_data"]
            ):

                with st.expander(
                    f"Metadata Entry {idx + 1}"
                ):

                    st.write("### Names")

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
                        "### HSA Biological Names"
                    )

                    st.write(
                        item.get(
                            "HSA_Biological_Names",
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
                        "### EC Number"
                    )

                    st.write(
                        item.get(
                            "EC_Number",
                            ""
                        )
                    )

        else:

            st.warning(
                "No biological metadata found"
            )

        # =================================
        # RELATION EXPLORER
        # =================================

        st.markdown("---")

        st.markdown(
            "## Relation Explorer"
        )

        # =================================
        # MAIN RELATIONS
        # =================================

        related_main = df_main[
            (
                df_main["Source_NodeID"]
                == selected_node
            )
            |
            (
                df_main["Target_NodeID"]
                == selected_node
            )
        ]

        # =================================
        # CROSS RELATIONS
        # =================================

        related_cross = df_cross[
            (
                df_cross["Chain_Node"]
                == selected_node
            )
            |
            (
                df_cross["Connected_Node"]
                == selected_node
            )
        ]

        # =================================
        # MAIN CHAIN RELATIONS
        # =================================

        st.write(
            "### Main Chain Relations"
        )

        if len(related_main) > 0:

            st.dataframe(
                related_main,
                use_container_width=True
            )

        else:

            st.info(
                "No main chain relations"
            )

        # =================================
        # CROSS PATHWAY RELATIONS
        # =================================

        st.write(
            "### Cross Pathway Relations"
        )

        if len(related_cross) > 0:

            st.dataframe(
                related_cross,
                use_container_width=True
            )

        else:

            st.info(
                "No cross pathway relations"
            )

# =========================================
# ERROR HANDLING
# =========================================

except Exception as e:

    st.error(
        "Error loading biological explorer"
    )

    st.exception(e)
