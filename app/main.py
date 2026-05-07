import streamlit as st
import pandas as pd
import networkx as nx
from pathlib import Path
import json

from streamlit_agraph import (
    agraph,
    Node,
    Edge,
    Config
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BCL2 Network Explorer",
    layout="wide"
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
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    h1, h2, h3 {
        color: #1D1D1F !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
    }

    p, div, span, label {
        color: #1D1D1F;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 14px !important;
    }

    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 14px !important;
    }

    div[role="listbox"] {
        background-color: #FFFFFF !important;
    }

    div[role="option"] {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
    }

    div[role="option"]:hover {
        background-color: #E9EEF9 !important;
    }

    .stCodeBlock {
        border-radius: 16px;
        overflow: hidden;
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
# DATA PATHS
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

    metadata_lookup[str(row["KEGG_ID"])] = {
        "Names": row.get("Names", ""),
        "HSA Symbols": row.get("HSA_Symbols", ""),
        "HSA Biological Names": row.get(
            "HSA_Biological_Names", ""
        ),
        "UniProt IDs": row.get("UniProt_IDs", ""),
        "GO IDs": row.get("GO_IDs", ""),
        "GO Labels": row.get("GO_Labels", "")
    }

# =========================================================
# NETWORK TYPE
# =========================================================

network_type_default = "Upstream"

network_type = st.session_state.get(
    "network_direction_main",
    network_type_default
)

if network_type == "Upstream":
    files = sorted(UPSTREAM_DIR.glob("*.xlsx"))
else:
    files = sorted(DOWNSTREAM_DIR.glob("*.xlsx"))

file_names = [f.name for f in files]

# =========================================================
# LOAD FILE
# =========================================================

selected_file_default = file_names[0]

if "pathway_selector" not in st.session_state:
    st.session_state["pathway_selector"] = selected_file_default

if network_type == "Upstream":
    file_path = UPSTREAM_DIR / st.session_state["pathway_selector"]
else:
    file_path = DOWNSTREAM_DIR / st.session_state["pathway_selector"]

sheet1 = pd.read_excel(file_path, sheet_name=0)
sheet2 = pd.read_excel(file_path, sheet_name=1)

# =========================================================
# BUILD GRAPH
# =========================================================

G = nx.DiGraph()

node_metadata = {}
edge_metadata = {}

# =========================================================
# MAIN CHAIN
# =========================================================

for _, row in sheet1.iterrows():

    source = str(row["Source_NodeID"])
    target = str(row["Target_NodeID"])

    source_kegg = str(row["Source"])
    target_kegg = str(row["Target"])

    interaction = str(row["Interaction"])

    source_class = "gene" if "GErel" in interaction else "protein"
    target_class = "gene" if "GErel" in interaction else "protein"

    G.add_node(source)
    G.add_node(target)

    G.add_edge(
        source,
        target,
        relation=row["RelationID"]
    )

    source_meta = metadata_lookup.get(source_kegg, {})

    node_metadata[source] = {
        "Node ID": source,
        "KEGG IDs": source_kegg,
        "Names": source_meta.get("Names", ""),
        "HSA Symbols": source_meta.get("HSA Symbols", ""),
        "HSA Biological Names": source_meta.get(
            "HSA Biological Names", ""
        ),
        "UniProt IDs": source_meta.get("UniProt IDs", ""),
        "GO IDs": str(row.get("Source_GO_IDs", "")),
        "GO Labels": str(row.get("Source_GO_Labels", "")),
        "Classification": source_class,
        "Degree": G.degree(source)
    }

    target_meta = metadata_lookup.get(target_kegg, {})

    node_metadata[target] = {
        "Node ID": target,
        "KEGG IDs": target_kegg,
        "Names": target_meta.get("Names", ""),
        "HSA Symbols": target_meta.get("HSA Symbols", ""),
        "HSA Biological Names": target_meta.get(
            "HSA Biological Names", ""
        ),
        "UniProt IDs": target_meta.get("UniProt IDs", ""),
        "GO IDs": str(row.get("Target_GO_IDs", "")),
        "GO Labels": str(row.get("Target_GO_Labels", "")),
        "Classification": target_class,
        "Degree": G.degree(target)
    }

    edge_metadata[str(row["RelationID"])] = {
        "Relation ID": str(row["RelationID"]),
        "Cluster ID": str(row["ClusterID"]),
        "Interaction": interaction,
        "Source Node": source,
        "Target Node": target,
        "Pathway": str(row["Pathway_Name"]),
        "Source KEGG": source_kegg,
        "Target KEGG": target_kegg
    }

# =========================================================
# PRESERVE MAIN CHAIN NODES
# =========================================================

main_chain_nodes = set(G.nodes())

# =========================================================
# CROSS PATHWAY
# =========================================================

show_cross_pathway = True

for _, row in sheet2.iterrows():

    source = str(row["Chain_Node"])
    target = str(row["Connected_Node"])

    if source not in main_chain_nodes:
        continue

    if target in main_chain_nodes:
        continue

    G.add_node(target)

    G.add_edge(
        source,
        target,
        relation=row["RelationID"]
    )

    target_kegg = str(row.get("Target_KEGG_IDs", ""))

    target_meta = metadata_lookup.get(target_kegg, {})

    node_metadata[target] = {
        "Node ID": target,
        "KEGG IDs": target_kegg,
        "Names": target_meta.get("Names", ""),
        "HSA Symbols": target_meta.get("HSA Symbols", ""),
        "HSA Biological Names": target_meta.get(
            "HSA Biological Names", ""
        ),
        "UniProt IDs": target_meta.get("UniProt IDs", ""),
        "GO IDs": str(row.get("Target_GO_IDs", "")),
        "GO Labels": str(row.get("Target_GO_Labels", "")),
        "Classification": "cross_pathway",
        "Degree": G.degree(target)
    }

    edge_metadata[str(row["RelationID"])] = {
        "Relation ID": str(row["RelationID"]),
        "Interaction": str(row["Interaction"]),
        "Source Node": source,
        "Target Node": target,
        "Pathway": str(row["Connected_Pathway"]),
        "Source KEGG": str(row.get("Source_KEGG_IDs", "")),
        "Target KEGG": target_kegg
    }

# =========================================================
# UPDATE FINAL NODE DEGREES
# =========================================================

for node in G.nodes():

    if node in node_metadata:
        node_metadata[node]["Degree"] = G.degree(node)

# =========================================================
# MAIN LAYOUT
# =========================================================

left_col, center_col, right_col = st.columns(
    [1.1, 3.8, 1.5]
)

# =========================================================
# LEFT PANEL
# =========================================================

with left_col:

    st.subheader("Network Controls")

    st.markdown("### Network Direction")

    network_type = st.radio(
        " ",
        ["Upstream", "Downstream"],
        key="network_direction_main"
    )

    show_cross_pathway = st.toggle(
        "Show Cross Pathway Nodes",
        value=True
    )

    st.markdown("### Search Node")

    search_options = []

    for node_id, meta in node_metadata.items():

        hsa_symbol = meta.get("HSA Symbols", "")
        kegg_id = meta.get("KEGG IDs", "")

        label = (
            f"{node_id} | "
            f"{hsa_symbol} | "
            f"{kegg_id}"
        )

        search_options.append(label)

    selected_search = st.selectbox(
        "Search by Node / HSA / KEGG",
        [""] + sorted(search_options),
        key="node_search"
    )

    searched_node = None

    if selected_search:
        searched_node = selected_search.split("|")[0].strip()

    st.markdown("### Select Pathway")

    selected_file = st.selectbox(
        " ",
        file_names,
        key="pathway_selector"
    )

# =========================================================
# GRAPH NODES
# =========================================================

nodes = []

for node in G.nodes():

    degree = G.degree(node)

    if node_metadata[node]["Classification"] == "cross_pathway":

        color = "#D6E6FF"
        size = 18

    else:

        color = "#4F8EF7"
        size = 25 + degree

    if searched_node == node:
        color = "#FF6B6B"
        size = size + 15

    nodes.append(
        Node(
            id=node,
            label=node,
            size=size,
            color=color
        )
    )

# =========================================================
# GRAPH EDGES
# =========================================================

edges = []

for source, target, data in G.edges(data=True):

    relation = data["relation"]

    edges.append(
        Edge(
            source=source,
            target=target,
            label=relation
        )
    )

# =========================================================
# GRAPH CONFIG
# =========================================================

config = Config(
    width="100%",
    height=850,
    directed=True,
    physics=True,
    hierarchical=False,
    nodeHighlightBehavior=True,
    highlightColor="#4F8EF7",
    collapsible=False
)

# =========================================================
# CENTER PANEL
# =========================================================

with center_col:

    st.subheader("Biological Pathway Workspace")

    clicked_node = agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )

    selected_node = clicked_node

    if searched_node:
        selected_node = searched_node

# =========================================================
# RIGHT PANEL
# =========================================================

with right_col:

    st.subheader("Pathway Inspector")

    st.markdown("### Network Summary")

    st.write(f"**Nodes:** {len(G.nodes())}")
    st.write(f"**Edges:** {len(G.edges())}")
    st.write(f"**Main Chain Relations:** {len(sheet1)}")
    st.write(f"**Cross Pathway Relations:** {len(sheet2)}")

    st.markdown("---")

    # =====================================================
    # NODE METADATA
    # =====================================================

    st.markdown("### Node Metadata")

    if selected_node:

        if selected_node in node_metadata:

            st.success(
                f"Node Selected: {selected_node}"
            )

            st.code(
                json.dumps(
                    node_metadata[selected_node],
                    indent=2
                ),
                language="json"
            )

        else:

            st.info(
                "Node metadata unavailable."
            )

    else:

        st.info(
            "Click a node in the graph."
        )

    st.markdown("---")

    # =====================================================
    # EDGE INSPECTOR
    # =====================================================

    st.markdown("### Edge Inspector")

    all_relation_ids = sorted(
        list(edge_metadata.keys())
    )

    connected_edges = []

    if selected_node:

        st.info(
            f"Relations connected to node: {selected_node}"
        )

        for edge_id, edge_info in edge_metadata.items():

            source_match = (
                edge_info.get("Source Node") == selected_node
            )

            target_match = (
                edge_info.get("Target Node") == selected_node
            )

            if source_match or target_match:
                connected_edges.append(edge_id)

    else:

        connected_edges = all_relation_ids

    interaction_options = sorted(
        list(
            set(
                [
                    edge_metadata[e]["Interaction"]
                    for e in connected_edges
                    if "Interaction" in edge_metadata[e]
                ]
            )
        )
    )

    interaction_filter = st.multiselect(
        "Filter Interaction Types",
        interaction_options,
        key="interaction_filter"
    )

    filtered_edges = []

    for edge_id in connected_edges:

        edge_info = edge_metadata[edge_id]

        include_edge = True

        if interaction_filter:

            if edge_info.get("Interaction") not in interaction_filter:
                include_edge = False

        if include_edge:
            filtered_edges.append(edge_id)

    edge_options = []

    for edge_id in filtered_edges:

        edge_info = edge_metadata[edge_id]

        edge_options.append(
            f"{edge_id} | "
            f"{edge_info['Source Node']} → "
            f"{edge_info['Target Node']}"
        )

    if edge_options:

        selected_edge_label = st.selectbox(
            "Select Relation ID",
            edge_options,
            key="edge_selector"
        )

        selected_edge = selected_edge_label.split("|")[0].strip()

        st.markdown("---")

        # =====================================================
        # EDGE METADATA
        # =====================================================

        st.markdown("### Edge Metadata")

        edge_info = edge_metadata.get(selected_edge)

        if edge_info:

            st.success(
                f"Edge Selected: {edge_info['Relation ID']}"
            )

            st.code(
                json.dumps(
                    edge_info,
                    indent=2
                ),
                language="json"
            )

    else:

        st.info("No connected edges found.")

# =========================================================
# TABLES
# =========================================================

with st.expander("Main Chain Relations Table"):

    st.dataframe(
        sheet1,
        use_container_width=True,
        height=400
    )

with st.expander("Cross Pathway Connections Table"):

    st.dataframe(
        sheet2,
        use_container_width=True,
        height=400
    )
