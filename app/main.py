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
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #EDEEF2;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1D1D1F;
        font-weight: 600;
        letter-spacing: -0.02em;
    }

    p, div, span, label {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #FCFCFD;
        border-right: 1px solid #DADCE3;
    }

    .network-box {
        background-color: #FCFCFD;
        border-radius: 26px;
        padding: 18px;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.06);
    }

    .panel-box {
        background-color: #FCFCFD;
        border-radius: 26px;
        padding: 20px;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.06);
    }

    .metric-card {
        background-color: #FCFCFD;
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

UPSTREAM_DIR = Path("data/raw/upstream")
DOWNSTREAM_DIR = Path("data/raw/downstream")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Network Controls")

network_type = st.sidebar.radio(
    "Network Direction",
    ["Upstream", "Downstream"]
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
    # READ SHEETS
    # =====================================================

    sheet1 = pd.read_excel(file_path, sheet_name=0)
    sheet2 = pd.read_excel(file_path, sheet_name=1)

    # =====================================================
    # BUILD GRAPH
    # =====================================================

    G = nx.DiGraph()

    # =====================================================
    # MAIN CHAIN
    # =====================================================

    for _, row in sheet1.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

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
            interaction=interaction,
            edge_type="main_chain"
        )

    # =====================================================
    # CROSS PATHWAY CONNECTIONS
    # =====================================================

    for _, row in sheet2.iterrows():

        source = str(row["Chain_Node"])
        target = str(row["Connected_Node"])

        interaction = str(row["Interaction"])

        G.add_node(
            target,
            node_type="cross_pathway"
        )

        G.add_edge(
            source,
            target,
            relation_id=row["RelationID"],
            interaction=interaction,
            edge_type="cross_pathway"
        )

    # =====================================================
    # NETWORK STATS
    # =====================================================

    unique_nodes = len(G.nodes())
    unique_edges = len(G.edges())

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
        st.metric("Nodes", unique_nodes)

    with m2:
        st.metric("Edges", unique_edges)

    with m3:
        st.metric("Pathways", len(pathways))

    with m4:
        st.metric("Cross Links", len(sheet2))

    st.write("")

    # =====================================================
    # MAIN LAYOUT
    # =====================================================

    left_col, right_col = st.columns([4.5, 1.5])

    # =====================================================
    # LEFT PANEL
    # =====================================================

    with left_col:

        st.markdown(
            '<div class="network-box">',
            unsafe_allow_html=True
        )

        st.subheader("Biological Pathway Workspace")

        # =================================================
        # CYTOSCAPE ELEMENTS
        # =================================================

        nodes = []
        edges = []

        # =================================================
        # NODES
        # =================================================

        for node in G.nodes():

            node_data = G.nodes[node]

            degree = G.degree(node)

            if node_data["node_type"] == "main_chain":

                color = "#4F8EF7"
                size = 26 + (degree * 1.5)
                shape = "ellipse"

            else:

                color = "#D6E6FF"
                size = 16 + (degree * 0.5)
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

        # =================================================
        # EDGES
        # =================================================

        for source, target, data in G.edges(data=True):

            if data["edge_type"] == "main_chain":

                edge_color = "#4F8EF7"
                width = 3

            else:

                edge_color = "#BFD8FF"
                width = 1.3

            edges.append({
                "data": {
                    "source": source,
                    "target": target,
                    "label": data["relation_id"],
                    "color": edge_color,
                    "width": width
                }
            })

        # =================================================
        # CYTOSCAPE DATA
        # =================================================

        cytoscape_data = {
            "nodes": nodes,
            "edges": edges
        }

        # =================================================
        # HTML + CYTOSCAPE
        # =================================================

        html_code = f"""
        <!DOCTYPE html>
        <html>

        <head>

        <script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>

        <script src="https://unpkg.com/dagre@0.7.4/dist/dagre.js"></script>

        <script src="https://unpkg.com/cytoscape-dagre/cytoscape-dagre.js"></script>

        <style>

        body {{
            margin: 0;
            padding: 0;
            background: #F8F9FB;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        #cy {{
            width: 100%;
            height: 1100px;
            background: #F8F9FB;
            border-radius: 20px;
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
                        'font-size': '11px',
                        'font-weight': '500',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#1D1D1F',
                        'border-width': 2,
                        'border-color': '#FFFFFF',
                        'text-wrap': 'wrap',
                        'overlay-opacity': 0,
                        'shadow-blur': 8,
                        'shadow-opacity': 0.12,
                        'shadow-color': '#A0A0A0'
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
                        'arrow-scale': 1.1,
                        'opacity': 0.75,
                        'label': 'data(label)',
                        'font-size': '7px',
                        'text-background-color': '#FFFFFF',
                        'text-background-opacity': 1,
                        'text-background-padding': '2px',
                        'color': '#6E6E73'
                    }}
                }}

            ],

            layout: {{
                name: 'dagre',
                rankDir: 'LR',
                spacingFactor: 2.8,
                nodeSep: 120,
                edgeSep: 80,
                rankSep: 180,
                animate: true,
                fit: false,
                padding: 80
            }}

        }});

        </script>

        </body>

        </html>
        """

        html(
            html_code,
            height=1120
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    with right_col:

        st.markdown(
            '<div class="panel-box">',
            unsafe_allow_html=True
        )

        st.subheader("Pathway Inspector")

        st.write("### Selected Pathway")

        for pathway in pathways:
            st.write(f"• {pathway}")

        st.write("### Interaction Types")

        interaction_types = (
            sheet1["Interaction"]
            .dropna()
            .unique()
        )

        for interaction in interaction_types[:15]:
            st.write(f"• {interaction}")

        st.write("### Network Summary")

        st.write(
            f"""
            Nodes: {unique_nodes}

            Edges: {unique_edges}

            Cross pathway links: {len(sheet2)}
            """
        )

        st.write("### Main Chain Preview")

        preview_cols = [
            "Source_NodeID",
            "Target_NodeID",
            "Interaction"
        ]

        st.dataframe(
            sheet1[preview_cols],
            use_container_width=True,
            height=450
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

# =========================================================
# FOOTER
# =========================================================

st.write("")

st.caption(
    "BCL2 Network Explorer • Interactive Biological Pathway Visualization"
)
