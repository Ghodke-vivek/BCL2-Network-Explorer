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

    # =====================================
    # MAIN CHAIN
    # =====================================

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

        # =================================
        # SOURCE NODE
        # =================================

        if source not in added_nodes:

            node_info = metadata.get(
                source,
                {}
            )

            node_type = node_info.get(
                "type",
                "Protein"
            )

            color = "#4DA6FF"

            if node_type == "Gene":
                color = "#00FFAA"

            elements.append({

                "data": {

                    "id": source,

                    "label": source
                },

                "classes": "main"
            })

            added_nodes.add(source)

        # =================================
        # TARGET NODE
        # =================================

        if target not in added_nodes:

            node_info = metadata.get(
                target,
                {}
            )

            node_type = node_info.get(
                "type",
                "Protein"
            )

            color = "#4DA6FF"

            if node_type == "Gene":
                color = "#00FFAA"

            elements.append({

                "data": {

                    "id": target,

                    "label": target
                },

                "classes": "main"
            })

            added_nodes.add(target)

        # =================================
        # EDGE
        # =================================

        elements.append({

            "data": {

                "source": source,

                "target": target,

                "label": interaction
            }
        })

    # =====================================
    # CROSS PATHWAY NODES
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

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

                        "label": connected_node
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

                    "source": chain_node,

                    "target": connected_node,

                    "label": "Cross Pathway"
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

                "font-size": "12px",

                "background-color": "#4DA6FF",

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

                "background-color": "#8C7AE6",

                "opacity": 0.5,

                "width": 20,

                "height": 20
            }
        },

        # =================================
        # EDGES
        # =================================

        {
            "selector": "edge",

            "style": {

                "curve-style": "bezier",

                "target-arrow-shape": "triangle",

                "line-color": "#999999",

                "target-arrow-color": "#999999",

                "width": 3
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

                "width": 1
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
            "name": "cose"
        },

        key="bcl2_network"
    )

    return selected
