import streamlit as st
import pandas as pd
import networkx as nx
from pathlib import Path
from streamlit.components.v1 import html
import json

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BCL2 Network Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# LIGHT UI CSS
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

    .metric-box {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
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
# LOAD DATA
# =========================================================

if selected_file:

    if network_type == "Upstream":
        file_path = UPSTREAM_DIR / selected_file
    else:
        file_path = DOWNSTREAM_DIR / selected_file

    # =====================================================
    # READ EXCEL
    # =====================================================

    sheet1 = pd.read_excel(file_path, sheet_name=0)
    sheet2 = pd.read_excel(file_path, sheet_name=1)

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    G = nx.DiGraph()

    # MAIN CHAIN
    for _, row in sheet1.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

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
            relation_id=row["RelationID"],
            interaction=row["Interaction"],
            edge_type="main_chain"
        )

    # CROSS PATHWAY
    if show_cross_pathway:

        for _, row in sheet2.iterrows():

            source = str(row["Chain_Node"])
            target = str(row["Connected_Node"])

            G.add_node(
                target,
                node_type="cross_pathway"
            )

            G.add_edge(
                source,
                target,
                relation_id=row["RelationID"],
                interaction=row["Interaction"],
                edge_type="cross_pathway"
            )

    # =====================================================
    # STATS
    # =====================================================

    node_count = len(G.nodes())
    edge_count = len(G.edges())

    pathways = (
        sheet1["Pathway_Name"]
        .dropna()
        .unique()
    )

    # =====================================================
    # METRICS
    # =====================================================

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Nodes", node_count)

    with m2:
        st.metric("Edges", edge_count)

    with m3:
        st.metric("Pathways", len(pathways))

    with m4:
        st.metric("Cross Links", len(sheet2))

    st.write("")

    # =====================================================
    # MAIN GRAPH PANEL
    # =====================================================

    st.markdown(
        '<div class="network-box">',
        unsafe_allow_html=True
    )

    st.subheader("Biological Pathway Workspace")

    # =====================================================
    # CYTOSCAPE ELEMENTS
    # =====================================================

    nodes = []
    edges = []

    # NODES
    for node in G.nodes():

        node_data = G.nodes[node]

        degree = G.degree(node)

        if node_data["node_type"] == "main_chain":

            color = "#4F8EF7"
            size = 22 + (degree * 1.2)
            shape = "ellipse"

        else:

            color = "#D6E6FF"
            size = 14 + (degree * 0.4)
            shape = "round-rectangle"

        nodes.append({
            "data": {
                "id": node,
                "label": node,
                "color": color,
                "size": size,
                "shape": shape,
                "degree": degree
            }
        })

    # EDGES
    for source, target, data in G.edges(data=True):

        if data["edge_type"] == "main_chain":

            edge_color = "#4F8EF7"
            width = 2.5

        else:

            edge_color = "#C8DBFF"
            width = 1

        edges.append({
            "data": {
                "source": source,
                "target": target,
                "label": data["relation_id"],
                "color": edge_color,
                "width": width
            }
        })

    cytoscape_data = {
        "nodes": nodes,
        "edges": edges
    }

    # =====================================================
    # CYTOSCAPE HTML
    # =====================================================

    html_code = f"""
    <!DOCTYPE html>
    <html>

    <head>

    <script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>

    <style>

    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background: #F8F9FB;
    }}

    #cy {{
        width: 100%;
        height: 950px;
        background: #F8F9FB;
        border-radius: 18px;
    }}

    </style>

    </head>

    <body>

    <div id="cy"></div>

    <script>

    const elements = {json.dumps(cytoscape_data["nodes"] + cytoscape_data["edges"])};

    const cy = cytoscape({{

        container: document.getElementById('cy'),

        elements: elements,

        style: [

            {{
                selector: 'node',
                style: {{
                    'background-color': 'data(color)',
                    'label': 'data(label)',
                    'width': 'data(size)',
                    'height': 'data(size)',
                    'shape': 'data(shape)',
                    'font-size': '10px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'color': '#1D1D1F',
                    'border-width': 2,
                    'border-color': '#FFFFFF',
                    'overlay-opacity': 0
                }}
            }},

            {{
                selector: 'edge',
                style: {{
                    'width': 'data(width)',
                    'line-color': 'data(color)',
                    'target-arrow-color': 'data(color)',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'opacity': 0.7
                }}
            }}

        ],

        layout: {{
            name: 'cose',
            animate: true,
            fit: true,
            padding: 60,
            nodeRepulsion: 900000,
            idealEdgeLength: 120,
            edgeElasticity: 100,
            gravity: 0.25
        }}

    }});

    </script>

    </body>

    </html>
    """

    html(
        html_code,
        height=980
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # =====================================================
    # TABLE SECTION
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
