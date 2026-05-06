import networkx as nx
from pyvis.network import Network
import tempfile

from node_metadata import build_node_metadata

from styles import (
    GENE_COLOR,
    PROTEIN_COLOR,
    COMPOUND_COLOR,
    CROSS_NODE_COLOR,
    DEFAULT_NODE_COLOR,
    ACTIVATION_COLOR,
    INHIBITION_COLOR,
    EXPRESSION_COLOR,
    DEFAULT_EDGE_COLOR
)


# =========================================
# EDGE COLOR LOGIC
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
# NODE COLOR LOGIC
# =========================================

def get_node_color(node_info):

    if node_info["cross_node"]:
        return CROSS_NODE_COLOR

    if node_info["type"] == "Gene":
        return GENE_COLOR

    return PROTEIN_COLOR


# =========================================
# BUILD NETWORK
# =========================================

def build_network(df_main, df_cross, include_cross_nodes):

    G = nx.DiGraph()

    # =====================================
    # BUILD NODE METADATA
    # =====================================

    metadata = build_node_metadata(
        df_main,
        df_cross
    )

    # =====================================
    # MAIN CHAIN RELATIONS
    # =====================================

    for _, row in df_main.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

        G.add_edge(
            source,
            target,
            color=get_edge_color(interaction),
            title=interaction
        )

    # =====================================
    # CROSS PATHWAY RELATIONS
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

            source = str(row["Chain_Node"])
            target = str(row["Connected_Node"])

            pathway = str(row["Connected_Pathway"])

            G.add_edge(
                source,
                target,
                color="gray",
                title=f"Cross Pathway: {pathway}"
            )

    # =====================================
    # CREATE PYVIS NETWORK
    # =====================================

    net = Network(
        height="850px",
        width="100%",
        directed=True,
        bgcolor="#111111",
        font_color="white"
    )

    # =====================================
    # PHYSICS SETTINGS
    # =====================================

    net.barnes_hut(
        gravity=-5000,
        central_gravity=0.2,
        spring_length=180,
        spring_strength=0.03,
        damping=0.09
    )

    # =====================================
    # ADD NODES
    # =====================================

    for node in G.nodes():

        node_info = metadata.get(
            node,
            {
                "type": "Unknown",
                "cross_node": False,
                "connections": 1
            }
        )

        degree = node_info["connections"]

        node_type = node_info["type"]

        is_cross = node_info["cross_node"]

        # =================================
        # NODE LABEL
        # =================================

        label = f"{node} ({degree})"

        # =================================
        # NODE SIZE
        # =================================

        size = 15 + (degree * 2)

        # =================================
        # TOOLTIP
        # =================================

        tooltip = f"""
        <b>Node ID:</b> {node}<br>
        <b>Type:</b> {node_type}<br>
        <b>Connections:</b> {degree}<br>
        <b>Cross Pathway Node:</b> {is_cross}
        """

        # =================================
        # NODE ADDITION
        # =================================

        net.add_node(
            node,
            label=label,
            title=tooltip,
            color=get_node_color(node_info),
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
            arrows="to"
        )

    # =====================================
    # INTERACTION OPTIONS
    # =====================================

    net.set_options("""
    {
      "nodes": {
        "shape": "dot",
        "font": {
          "size": 14
        }
      },
      "edges": {
        "smooth": {
          "type": "dynamic"
        }
      },
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
    # SAVE TEMP HTML
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
