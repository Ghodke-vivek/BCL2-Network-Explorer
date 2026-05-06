from st_cytoscape import cytoscape


# =========================================
# EDGE COLOR
# =========================================

def get_edge_color(interaction):

    interaction = str(interaction).lower()

    if "activation" in interaction:
        return "#00FF66"

    elif "inhibition" in interaction:
        return "#FF4444"

    elif "expression" in interaction:
        return "#00CCFF"

    else:
        return "#999999"


# =========================================
# BUILD ELEMENTS
# =========================================

def build_elements(
    df_main,
    df_cross,
    metadata,
    include_cross_nodes
):

    elements = []

    added_nodes = set()

    gene_nodes = set()

    # =====================================
    # IDENTIFY GENE NODES
    # =====================================

    for _, row in df_main.iterrows():

        interaction = str(
            row["Interaction"]
        )

        target = str(
            row["Target_NodeID"]
        )

        if "GErel" in interaction:
            gene_nodes.add(target)

    # =====================================
    # MAIN CHAIN
    # =====================================

    for _, row in df_main.iterrows():

        relation_id = str(
            row["RelationID"]
        )

        source = str(
            row["Source_NodeID"]
        )

        target = str(
            row["Target_NodeID"]
        )

        interaction = str(
            row["Interaction"]
        )

        pathway_name = str(
            row.get("Pathway_Name", "")
        )

        edge_color = get_edge_color(
            interaction
        )

        # =================================
        # SOURCE NODE
        # =================================

        if source not in added_nodes:

            node_type = "Protein"

            if source in gene_nodes:
                node_type = "Gene"

            node_color = "#4DA6FF"

            if node_type == "Gene":
                node_color = "#00FFAA"

            elements.append({

                "data": {

                    "id": source,

                    "label": source,

                    "node_type": node_type,

                    "node_color": node_color
                },

                "classes": "main"
            })

            added_nodes.add(source)

        # =================================
        # TARGET NODE
        # =================================

        if target not in added_nodes:

            node_type = "Protein"

            if target in gene_nodes:
                node_type = "Gene"

            node_color = "#4DA6FF"

            if node_type == "Gene":
                node_color = "#00FFAA"

            elements.append({

                "data": {

                    "id": target,

                    "label": target,

                    "node_type": node_type,

                    "node_color": node_color
                },

                "classes": "main"
            })

            added_nodes.add(target)

        # =================================
        # EDGE
        # =================================

        elements.append({

            "data": {

                "id": relation_id,

                "source": source,

                "target": target,

                "label": interaction,

                "interaction": interaction,

                "pathway": pathway_name,

                "edge_color": edge_color
            }
        })

    # =====================================
    # CROSS PATHWAY NODES
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

            relation_id = str(
                row["RelationID"]
            )

            chain_node = str(
                row["Chain_Node"]
            )

            connected_node = str(
                row["Connected_Node"]
            )

            # =================================
            # CONTEXT NODE
            # =================================

            if connected_node not in added_nodes:

                elements.append({

                    "data": {

                        "id": connected_node,

                        "label": connected_node,

                        "node_type": "CrossPathway",

                        "node_color": "#8C7AE6"
                    },

                    "classes": "cross"
                })

                added_nodes.add(
                    connected_node
                )

            # =================================
            # CONTEXT EDGE
            # =================================

            elements.append({

                "data": {

                    "id": f"cross_{relation_id}",

                    "source": chain_node,

                    "target": connected_node,

                    "label": "Cross Pathway",

                    "edge_color": "#AAAAAA"
                },

                "classes": "cross_edge"
            })

    return elements


# =========================================
# STYLESHEET
# =========================================

def get_stylesheet():

    return [

        # =================================
        # DEFAULT NODES
        # =================================

        {
            "selector": "node",

            "style": {

                "label": "data(label)",

                "color": "white",

                "font-size": "10px",

                "text-valign": "center",

                "text-halign": "center",

                "background-color": "data(node_color)",

                "border-width": 2,

                "border-color": "#FFFFFF",

                "width": 35,

                "height": 35
            }
        },

        # =================================
        # CROSS NODES
        # =================================

        {
            "selector": ".cross",

            "style": {

                "opacity": 0.7,

                "width": 22,

                "height": 22
            }
        },

        # =================================
        # DEFAULT EDGES
        # =================================

        {
            "selector": "edge",

            "style": {

                "curve-style": "bezier",

                "target-arrow-shape": "triangle",

                "line-color": "data(edge_color)",

                "target-arrow-color": "data(edge_color)",

                "width": 3,

                "arrow-scale": 1.2
            }
        },

        # =================================
        # CROSS EDGES
        # =================================

        {
            "selector": ".cross_edge",

            "style": {

                "line-style": "dashed",

                "opacity": 0.5,

                "width": 1.5
            }
        },

        # =================================
        # SELECTED NODE
        # =================================

        {
            "selector": ":selected",

            "style": {

                "border-width": 5,

                "border-color": "#FFD700"
            }
        }
    ]


# =========================================
# RENDER CYTOSCAPE
# =========================================

def render_cytoscape(
    df_main,
    df_cross,
    metadata,
    include_cross_nodes
):

    elements = build_elements(
        df_main,
        df_cross,
        metadata,
        include_cross_nodes
    )

    selected = cytoscape(

        elements=elements,

        stylesheet=get_stylesheet(),

        layout={
            "name": "breadthfirst",
            "directed": True,
            "padding": 10
        },

        key="bcl2_network"
    )

    return selected
