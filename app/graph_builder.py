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
# EDGE COLOR
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
# NODE COLOR
# =========================================

def get_node_color(info):

    # Cross pathway nodes
    if info["cross_node"]:
        return "#AA88FF"

    # Gene nodes
    if info["type"] == "Gene":
        return "#00FFAA"

    # Protein/general nodes
    return "#3FA7FF"


# =========================================
# GET DISPLAY LABEL
# =========================================

def get_display_label(node, info):

    biological_data = info.get(
        "biological_data",
        []
    )

    # Try HSA Symbols first
    for item in biological_data:

        symbol = str(
            item.get("HSA_Symbols", "")
        ).strip()

        if symbol and symbol != "nan":

            # Multiple symbols
            symbol = symbol.split("|")[0]

            return symbol

    # Fallback = NodeID
    return node


# =========================================
# TOOLTIP
# =========================================

def generate_tooltip(node, info):

    label = get_display_label(
        node,
        info
    )

    tooltip = f"""
    <h3>{label}</h3>

    <b>Node ID:</b> {node}<br>
    <b>Type:</b> {info['type']}<br>
    <b>Connections:</b> {info['connections']}<br>
    <b>Cross Pathway:</b> {info['cross_node']}<br>
    """

    biological_data = info.get(
        "biological_data",
        []
    )

    if biological_data:

        item = biological_data[0]

        tooltip += f"""

        <hr>

        <b>KEGG Name:</b><br>
        {item.get('Names', '')}<br><br>

        <b>HSA Symbol:</b><br>
        {item.get('HSA_Symbols', '')}<br>
        """

    return tooltip


# =========================================
# BUILD NETWORK
# =========================================

def build_network(
    df_main,
    df_cross,
    include_cross_nodes,
    selected_node=None
):

    G = nx.DiGraph()

    metadata = build_node_metadata(
        df_main,
        df_cross
    )

    # =====================================
    # MAIN CHAIN EDGES
    # =====================================

    for _, row in df_main.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

        G.add_edge(
            source,
            target,
            interaction=interaction,
            color=get_edge_color(interaction),
            width=4
        )

    # =====================================
    # CROSS PATHWAY EDGES
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

            source = str(row["Chain_Node"])
            target = str(row["Connected_Node"])

            G.add_edge(
                source,
                target,
                interaction="Cross Pathway",
                color="#777777",
                width=1
            )

    # =====================================
    # CREATE PYVIS NETWORK
    # =====================================

    net = Network(
        height="950px",
        width="100%",
        directed=True,
        bgcolor="#0B0F1A",
        font_color="white"
    )

    # =====================================
    # PHYSICS OPTIONS
    # =====================================

    net.barnes_hut(
        gravity=-2500,
        central_gravity=0.15,
        spring_length=180,
        spring_strength=0.02,
        damping=0.12
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

        label = get_display_label(
            node,
            info
        )

        degree = info["connections"]

        # =================================
        # NODE SIZE
        # =================================

        if info["cross_node"]:

            size = 10

        else:

            size = 20 + (degree * 2)

        # =================================
        # HUB DETECTION
        # =================================

        border_width = 2
        border_color = "#FFFFFF"

        if degree >= 8:

            border_width = 5
            border_color = "#FFAA00"

        # =================================
        # SELECTED NODE
        # =================================

        if selected_node == node:

            size += 12
            border_width = 8
            border_color = "#FFFF00"

        # =================================
        # NODE SHAPE
        # =================================

        shape = "dot"

        if info["type"] == "Gene":

            shape = "star"

        # =================================
        # NODE OPACITY
        # =================================

        opacity = 1.0

        if info["cross_node"]:

            opacity = 0.55

        # =================================
        # ADD NODE
        # =================================

        net.add_node(
            node,

            label=label,

            title=generate_tooltip(
                node,
                info
            ),

            color={
                "background": get_node_color(info),
                "border": border_color
            },

            shape=shape,

            size=size,

            borderWidth=border_width,

            font={
                "size": 18,
                "face": "arial",
                "color": "white"
            },

            opacity=opacity
        )

    # =====================================
    # ADD EDGES
    # =====================================

    for source, target, data in G.edges(data=True):

        interaction = data["interaction"]

        # Dashed for contextual edges
        dashes = False

        if interaction == "Cross Pathway":

            dashes = True

        net.add_edge(
            source,
            target,

            color=data["color"],

            width=data["width"],

            title=interaction,

            arrows="to",

            smooth={
                "type": "dynamic"
            },

            dashes=dashes
        )

    # =====================================
    # ADVANCED OPTIONS
    # =====================================

    net.set_options("""
    {
      "interaction": {

        "hover": true,

        "tooltipDelay": 200,

        "navigationButtons": true,

        "keyboard": true,

        "multiselect": true
      },

      "physics": {

        "enabled": true,

        "stabilization": {

          "enabled": true,

          "iterations": 120
        }
      },

      "edges": {

        "smooth": {

          "enabled": true,

          "type": "dynamic"
        }
      },

      "nodes": {

        "shadow": true
      }
    }
    """)

    # =====================================
    # SAVE GRAPH
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
