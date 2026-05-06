import streamlit as st
import pandas as pd
import networkx as nx
from pathlib import Path
import json

from streamlit_cytoscapejs import st_cytoscapejs

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BCL2 Network Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #F3F4F7;
    }

    .main {
        background-color: #F3F4F7;
    }

    .block-container {
        padding-top: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
    }

    h1, h2, h3 {
        color: #1D1D1F !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
    }

    p, div, span, label {
        color: #1D1D1F;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E5EA;
    }

    .network-box {
        background-color: #FCFCFD;
        border-radius: 24px;
        padding: 18px;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.06);
    }

    .inspector-box {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.06);
        min-height: 920px;
        overflow-y: auto;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
    }

    div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }

    div[role="listbox"] {
        background-color: #FFFFFF !important;
    }

    div[role="option"] {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TITLE
# =========================================================

st.title("BCL2 Network Explorer")

st.markdown(
    """
    Interactive biological signaling traversal and pathway crosstalk visualization platform.
    """
)

# =========================================================
# PATHS
# =========================================================

UPSTREAM_DIR = Path("data/upstream")
DOWNSTREAM_DIR = Path("data/downstream")

METADATA_FILE = Path(
    "data/metadata/14. Annotated_Keggid_Metadata.xlsx"
)

# =========================================================
# LOAD METADATA
# =========================================================

metadata_df = pd.read_excel(METADATA_FILE)

metadata_lookup = {}

for _, row in metadata_df.iterrows():

    metadata_lookup[str(row["KEGG_ID"])] = row.to_dict()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Network Controls")

network_type = st.sidebar.radio(
    "Network Direction",
    ["Upstream", "Downstream"]
)

show_cross_pathway = st.sidebar.toggle(
    "Show Cross Pathway Nodes",
    value=True
)

# =========================================================
# LOAD FILES
# =========================================================

if network_type == "Upstream":
    files = sorted(UPSTREAM_DIR.glob("*.xlsx"))
else:
    files = sorted(DOWNSTREAM_DIR.glob("*.xlsx"))

file_names = [f.name for f in files]

selected_file = st.sidebar.selectbox(
    "Select Pathway",
    file_names
)

# =========================================================
# LOAD NETWORK
# =========================================================

if selected_file:

    if network_type == "Upstream":
        file_path = UPSTREAM_DIR / selected_file
    else:
        file_path = DOWNSTREAM_DIR / selected_file

    # =====================================================
    # READ DATA
    # =====================================================

    sheet1 = pd.read_excel(file_path, sheet_name=0)
    sheet2 = pd.read_excel(file_path, sheet_name=1)

    # =====================================================
    # GRAPH
    # =====================================================

    G = nx.DiGraph()

    node_metadata = {}
    edge_metadata = {}

    # =====================================================
    # MAIN CHAIN
    # =====================================================

    for _, row in sheet1.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

        relation_id = str(row["RelationID"])

        source_kegg = str(row["Source"])
        target_kegg = str(row["Target"])

        node_classification = "protein"

        if "GErel" in interaction:
            node_classification = "gene"

        G.add_node(
            source,
            node_type="main_chain"
        )

        G.add_node(
            target,
            node_type="main_chain"
        )

        G.add_edge(
            source,
            target,
            relation_id=relation_id,
            interaction=interaction,
            edge_type="main_chain"
        )

        node_metadata[source] = {
            "Node ID": source,
            "KEGG IDs": source_kegg,
            "GO IDs": row.get("Source_GO_IDs", ""),
            "GO Labels": row.get("Source_GO_Labels", ""),
            "Classification": node_classification,
            "Degree": G.degree(source)
        }

        node_metadata[target] = {
            "Node ID": target,
            "KEGG IDs": target_kegg,
            "GO IDs": row.get("Target_GO_IDs", ""),
            "GO Labels": row.get("Target_GO_Labels", ""),
            "Classification": node_classification,
            "Degree": G.degree(target)
        }

        edge_metadata[relation_id] = {
            "Relation ID": relation_id,
            "Cluster ID": row["ClusterID"],
            "Interaction": interaction,
            "Source Node": source,
            "Target Node": target,
            "Pathway": row["Pathway_Name"]
        }

    # =====================================================
    # CROSS PATHWAY
    # =====================================================

    if show_cross_pathway:

        for _, row in sheet2.iterrows():

            source = str(row["Chain_Node"])
            target = str(row["Connected_Node"])

            relation_id = str(row["RelationID"])

            G.add_node(
                target,
                node_type="cross_pathway"
            )

            G.add_edge(
                source,
                target,
                relation_id=relation_id,
                interaction=row["Interaction"],
                edge_type="cross_pathway"
            )

            edge_metadata[relation_id] = {
                "Relation ID": relation_id,
                "Interaction": row["Interaction"],
                "Connected Pathway": row["Connected_Pathway"],
                "Source Node": source,
                "Target Node": target
            }

    # =====================================================
    # METRICS
    # =====================================================

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Nodes", len(G.nodes()))

    with m2:
        st.metric("Edges", len(G.edges()))

    with m3:
        st.metric("Main Chain", len(sheet1))

    with m4:
        st.metric("Cross Links", len(sheet2))

    # =====================================================
    # ELEMENTS
    # =====================================================

    elements = []

    # =====================================================
    # NODES
    # =====================================================

    for node in G.nodes():

        degree = G.degree(node)

        node_type = G.nodes[node]["node_type"]

        if node_type == "main_chain":

            color = "#4F8EF7"
            size = 22 + (degree * 1.2)
            shape = "ellipse"

        else:

            color = "#D6E6FF"
            size = 15 + (degree * 0.5)
            shape = "round-rectangle"

        elements.append({
            "data": {
                "id": node,
                "label": node,
                "degree": degree,
                "color": color,
                "size": size,
                "shape": shape
            }
        })

    # =====================================================
    # EDGES
    # =====================================================

    for source, target, data in G.edges(data=True):

        if data["edge_type"] == "main_chain":

            edge_color = "#4F8EF7"
            width = 2.5

        else:

            edge_color = "#C8DBFF"
            width = 1

        elements.append({
            "data": {
                "id": data["relation_id"],
                "source": source,
                "target": target,
                "label": data["relation_id"],
                "color": edge_color,
                "width": width
            }
        })

    # =====================================================
    # STYLESHEET
    # =====================================================

    stylesheet = [

        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": 10,
                "color": "#1D1D1F",
                "border-width": 2,
                "border-color": "#FFFFFF",
                "background-color": "data(color)",
                "width": "data(size)",
                "height": "data(size)",
                "shape": "data(shape)"
            }
        },

        {
            "selector": "edge",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "line-color": "data(color)",
                "target-arrow-color": "data(color)",
                "width": "data(width)"
            }
        }

    ]

    # =====================================================
    # LAYOUT
    # =====================================================

    graph_col, inspector_col = st.columns([5, 1.7])

    # =====================================================
    # GRAPH
    # =====================================================

    with graph_col:

        st.markdown(
            '<div class="network-box">',
            unsafe_allow_html=True
        )

        st.subheader("Biological Pathway Workspace")

        selected = st_cytoscapejs(
            elements,
            stylesheet
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # =====================================================
    # INSPECTOR
    # =====================================================

    with inspector_col:

        st.markdown(
            '<div class="inspector-box">',
            unsafe_allow_html=True
        )

        st.subheader("Pathway Inspector")

        if selected:

            selected_id = None

            if isinstance(selected, dict):

                selected_id = selected.get("id")

            # =================================================
            # NODE
            # =================================================

            if selected_id in node_metadata:

                st.success("Node Selected")

                st.code(
                    json.dumps(
                        node_metadata[selected_id],
                        indent=2
                    ),
                    language="json"
                )

            # =================================================
            # EDGE
            # =================================================

            elif selected_id in edge_metadata:

                st.success("Edge Selected")

                st.code(
                    json.dumps(
                        edge_metadata[selected_id],
                        indent=2
                    ),
                    language="json"
                )

            else:

                st.info(
                    "Click a node or edge to inspect metadata."
                )

        else:

            st.info(
                "Click a node or edge to inspect metadata."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # =====================================================
    # TABLES
    # =====================================================

    with st.expander("Main Chain Relations Table"):

        st.dataframe(
            sheet1,
            use_container_width=True,
            height=450
        )

    with st.expander("Cross Pathway Connections Table"):

        st.dataframe(
            sheet2,
            use_container_width=True,
            height=450
        )
