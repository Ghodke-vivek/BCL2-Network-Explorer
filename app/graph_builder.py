import networkx as nx
from pyvis.network import Network
import tempfile

from node_metadata import build_node_metadata

from styles import (
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
# TOOLTIP
# =========================================

def generate_tooltip(node, info):

    tooltip = f"""
    <h3>{node}</h3>

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
    # BUILD MAIN CHAIN
    # =====================================

    main_chain_nodes = set()

    for _, row in df_main.iterrows():

        source = str(
            row["Source_NodeID"]
        )

        target = str(
            row["Target_NodeID"]
        )

        interaction = str(
            row["Interaction"]
        )

        main_chain_nodes.add(source)
        main_chain_nodes.add(target)

        G.add_edge(
            source,
            target,

            interaction=interaction,

            color=get_edge_color(
                interaction
            ),

            width=5,

            contextual=False
        )

    # =====================================
    # ADD CONTEXTUAL CROSS NODES
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

            chain_node = str(
                row["Chain_Node"]
            )

            connected_node = str(
                row["Connected_Node"]
            )

            # ONLY contextual attachment
            # NO recursive expansion

            G.add_edge(
                chain_node,
                connected_node,

                interaction="Cross Pathway",

                color="#777777",

                width=1,

                contextual=True
            )

    # =====================================
    # CREATE NETWORK
    # =====================================

    net = Network(
        height="950px",
        width="100%",
        directed=True,
        bgcolor="#0B0F1A",
        font_color="white"
    )

    # =====================================
    # STABLE PROFESSIONAL PHYSICS
    # =====================================

    net.force_atlas_2based(
        gravity=-45,
        central_gravity=0.003,
        spring_length=220,
        spring_strength=0.01,
        damping=0.9,
        overlap=0.1
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

        # =================================
        # MAIN CHAIN NODES
        # =================================

        if node in main_chain_nodes:

            size = 28 + (degree * 2)

            color = "#4DA6FF"

            shape = "dot"

            opacity = 1.0

            border_width = 3

            border_color = "#FFFFFF"

            # Gene nodes
            if info["type"] == "Gene":

                color = "#00FFAA"

                shape = "star"

            # Hub nodes
            if degree >= 6:

                border_width = 6

                border_color = "#FFAA00"

        # =================================
        # CROSS PATHWAY NODES
        # =================================

        else:

            size = 10

            color = "#8C7AE6"

            shape = "dot"

            opacity = 0.35

            border_width = 1

            border_color = "#AAAAAA"

        # =================================
        # SELECTED NODE
        # =================================

        if selected_node == node:

            size += 10

            border_width = 8

            border_color = "#FFFF00"

        # =================================
        # ADD NODE
        # =================================

        net.add_node(
            node,

            label=node,

            title=generate_tooltip(
                node,
                info
            ),

            color={
                "background": color,
                "border": border_color
            },

            shape=shape,

            size=size,

            borderWidth=border_width,

            opacity=opacity,

            font={
                "size": 15,
                "face": "arial",
                "color": "white"
            }
        )

    # =====================================
    # ADD EDGES
    # =====================================

    for source, target, data in G.edges(data=True):

        contextual = data["contextual"]

        dashes = False

        smooth_type = "continuous"

        if contextual:

            dashes = True

            smooth_type = "curvedCW"

        net.add_edge(
            source,
            target,

            color=data["color"],

            width=data["width"],

            title=data["interaction"],

            arrows="to",

            dashes=dashes,

            smooth={
                "enabled": True,
                "type": smooth_type,
                "roundness": 0.15
            }
        )

    # =====================================
    # ADVANCED OPTIONS
    # =====================================

    net.set_options("""
    {
      "layout": {

        "improvedLayout": true
      },

      "interaction": {

        "hover": true,

        "tooltipDelay": 120,

        "navigationButtons": true,

        "keyboard": true,

        "dragNodes": true,

        "dragView": true,

        "zoomView": true
      },

      "physics": {

        "enabled": true,

        "solver": "forceAtlas2Based",

        "forceAtlas2Based": {

          "gravitationalConstant": -45,

          "centralGravity": 0.003,

          "springLength": 220,

          "springConstant": 0.01,

          "damping": 0.9,

          "avoidOverlap": 0.15
        },

        "stabilization": {

          "enabled": true,

          "iterations": 250
        }
      },

      "nodes": {

        "shadow": false,

        "font": {

          "size": 16
        }
      },

      "edges": {

        "smooth": {

          "enabled": true,

          "type": "continuous",

          "roundness": 0.15
        },

        "shadow": false
      }
    }
    """)

    # =====================================
    # SAVE HTML
    # =====================================

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html"
    )

    net.save_graph(
        temp_file.name
    )

    return open(
        temp_file.name,
        "r",
        encoding="utf-8"
    ).read()
