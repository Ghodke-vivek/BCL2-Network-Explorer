import streamlit as st
import pandas as pd
import os

from cytoscape_builder import (
    render_cytoscape
)

from node_metadata import (
    build_node_metadata
)

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
# SESSION STATE
# =========================================

if "selected_element" not in st.session_state:

    st.session_state[
        "selected_element"
    ] = {}

if "selected_node" not in st.session_state:

    st.session_state[
        "selected_node"
    ] = None


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

# =========================================
# DATA FOLDER
# =========================================

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

    # =====================================
    # LOAD EXCEL FILES
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
    # NODE LIST
    # =====================================

    all_nodes = sorted(
        metadata.keys()
    )

    # =====================================
    # SIDEBAR NODE SELECTOR
    # =====================================

    sidebar_selected_node = st.sidebar.selectbox(
        "Select Node ID",
        all_nodes
    )

    # =====================================
    # INITIAL NODE
    # =====================================

    if st.session_state[
        "selected_node"
    ] is None:

        st.session_state[
            "selected_node"
        ] = sidebar_selected_node

    # =====================================
    # MAIN LAYOUT
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

        selected_element = render_cytoscape(
            df_main,
            df_cross,
            metadata,
            include_cross_nodes
        )

        # =================================
        # STORE CYTOSCAPE SELECTION
        # =================================

        if selected_element:

            st.session_state[
                "selected_element"
            ] = selected_element

        # =================================
        # LOAD CURRENT SELECTION
        # =================================

        selected_element = st.session_state.get(
            "selected_element",
            {}
        )

        # =================================
        # AUTO NODE UPDATE
        # =================================

        try:

            selected_nodes = selected_element.get(
                "nodes",
                []
            )

            if selected_nodes:

                clicked_node = selected_nodes[0].get(
                    "data",
                    {}
                ).get("id")

                if clicked_node:

                    st.session_state[
                        "selected_node"
                    ] = clicked_node

        except:
            pass

        # =================================
        # DEBUG PANEL
        # =================================

        with st.expander(
            "Selection Debug"
        ):

            st.write(
                selected_element
            )

    # =====================================
    # RIGHT PANEL
    # =====================================

    with info_col:

        st.subheader(
            "Biological Annotation Explorer"
        )

        selected_node = st.session_state.get(
            "selected_node",
            sidebar_selected_node
        )

        node_info = metadata.get(
            selected_node,
            {}
        )

        # =================================
        # NODE INFO
        # =================================

        st.markdown(
            "## Node Information"
        )

        st.code(selected_node)

        st.write(
            f"Type: {node_info.get('type', '')}"
        )

        st.write(
            f"Connections: "
            f"{node_info.get('connections', '')}"
        )

        st.write(
            f"Cross Pathway: "
            f"{node_info.get('cross_node', '')}"
        )

        # =================================
        # KEGG IDS
        # =================================

        st.markdown("---")

        st.markdown(
            "## KEGG IDs"
        )

        for kid in node_info.get(
            "kegg_ids",
            []
        ):

            st.code(kid)

        # =================================
        # BIOLOGICAL METADATA
        # =================================

        st.markdown("---")

        st.markdown(
            "## Biological Metadata"
        )

        biological_data = node_info.get(
            "biological_data",
            []
        )

        if biological_data:

            for idx, item in enumerate(
                biological_data
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

        # =================================
        # RELATION EXPLORER
        # =================================

        st.markdown("---")

        render_relation_explorer(
            selected_node,
            df_main,
            df_cross
        )

        # =================================
        # LEGEND
        # =================================

        st.markdown("---")

        render_legend()

# =========================================
# ERROR HANDLING
# =========================================

except Exception as e:

    st.error(
        "Error loading explorer"
    )

    st.exception(e)
