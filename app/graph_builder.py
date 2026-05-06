import networkx as nx
from pyvis.network import Network
import tempfile

from node_metadata import build_node_metadata

from styles import (
    GENE_COLOR,
    PROTEIN_COLOR,
    CROSS_NODE_COLOR,
    ACTIVATION_COLOR,
    INHIBITION_COLOR,
    EXPRESSION_COLOR,
    DEFAULT_EDGE_COLOR
)


# =========================================
# EDGE COLORS
# =========================================

def get_edge_color(interaction):

    interaction = str(interaction).lower()

    if "activation" in interaction:
        return ACTIVATION_COLOR

    elif "inhibition" in interaction:
        return INHIBITION_COLOR

    elif "expression" in interaction:
        return EXPRESSION_COLOR

    else:
        return DEFAULT_EDGE_COLOR


# =========================================
# NODE COLORS
# =========================================

def get_node_color(info):

    if info["cross_node"]:
        return CROSS_NODE_COLOR

    if info["type"] == "Gene":
        return GENE_COLOR

    return PROTEIN_COLOR


# =========================================
# TOOLTIP GENERATION
# =========================================

def generate_tooltip(node, info):

    tooltip = f"""
    <h3>{node}</h3>

    <b>Type:</b> {info['type']}<br>
    <b>Connections:</b> {info['connections']}<br>
    <b>Cross Pathway:</b> {info['cross_node']}<br><br>
    """

    for item in info["biological_data"][:3]:

        tooltip += f"""
        <hr>

        <b>Names:</b> {item.get('Names', '')}<br>

        <b>HSA Symbols:</b>
        {item.get('HSA_Symbols', '')}<br>

        <b>UniProt IDs:</b>
        {item.get('UniProt_IDs', '')}<br>

        <b>GO IDs:</b>
        {item.get('GO_IDs', '')}<br>

        <b>GO Labels:</b>
        {item.get('GO_Labels', '')}<br>
        """

    return tooltip


# =========================================
# BUILD NETWORK
# =========================================

def build_network(df_main, df_cross, include_cross_nodes):

    G = nx.DiGraph()

    metadata = build_node_metadata(
        df_main,
        df_cross
    )

    # =====================================
    # MAIN CHAIN
    # =====================================

    for _, row in df_main.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

        G.add_edge(
            source,
            target,
            color=get_edge_color(interaction),
            title=interaction,
            width=3
        )

    # =====================================
    # CROSS NODES
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

            source = str(row["Chain_Node"])
            target = str(row["Connected_Node"])

            G.add_edge(
                source,
                target,
                color="#777777",
                title="Cross Pathway Connection",
                width=1
            )

    # =====================================
    # PYVIS NETWORK
    # =====================================

    net = Network(
        height="900px",
        width="100%",
        directed=True,
        bgcolor="#111111",
        font_color="white"
    )

    # =====================================
    # ADD NODES
    # =====================================

    for node in G.nodes():

        info = metadata.get(
            node,
            {
                "type": "Protein",
                "cross_node": False,
                "connections": 1,
                "biological_data": []
            }
        )

        degree = info["connections"]

        label = f"{node}"

        # Smaller for cross nodes
        if info["cross_node"]:
            size = 10
        else:
            size = 18 + (degree * 2)

        net.add_node(
            node,
            label=label,
            title=generate_tooltip(node, info),
            color=get_node_color(info),
            size=size,
            borderWidth=2
        )

    # =====================================
    # ADD EDGES
    # =====================================

    for source, target, data in G.edges(data=True):

        net.add_edge(
            source,
            target,
            color=data["color"],
            title=data["title"],
            width=data["width"],
            arrows="to"
        )

    # =====================================
    # PHYSICS
    # =====================================

    net.barnes_hut(
        gravity=-3000,
        central_gravity=0.2,
        spring_length=140,
        spring_strength=0.03,
        damping=0.09
    )

    # =====================================
    # OPTIONS
    # =====================================

    net.set_options("""
    {
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      },
      "physics": {
        "enabled": true
      }
    }
    """)

    # =====================================
    # SAVE
    # =====================================

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html"
    )

    net.save_graph(temp_file.name)

    return open(
        temp_file.name,
        "r",
        encoding="utf-8"
    ).read()
