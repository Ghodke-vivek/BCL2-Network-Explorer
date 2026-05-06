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

                "style": {

                    "background-color": color,

                    "label": source,

                    "color": "white",

                    "font-size": "12px",

                    "border-width": 2,

                    "border-color": "#FFFFFF"
                }
            })

            added_nodes.add(source)

        # =================================
        # TARGET NODE
        # =====================================

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

                "style": {

                    "background-color": color,

                    "label": target,

                    "color": "white",

                    "font-size": "12px",

                    "border-width": 2,

                    "border-color": "#FFFFFF"
                }
            })

            added_nodes.add(target)

        # =================================
        # EDGE
        # =====================================

        elements.append({

            "data": {

                "source": source,

                "target": target,

                "label": interaction
            },

            "style": {

                "line-color": get_edge_color(
                    interaction
                ),

                "target-arrow-color": get_edge_color(
                    interaction
                ),

                "target-arrow-shape": "triangle",

                "curve-style": "bezier",

                "width": 4
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

                    "style": {

                        "background-color": "#8C7AE6",

                        "label": connected_node,

                        "color": "white",

                        "font-size": "10px",

                        "opacity": 0.5,

                        "width": 20,

                        "height": 20
                    }
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

                "style": {

                    "line-color": "#777777",

                    "target-arrow-color": "#777777",

                    "target-arrow-shape": "triangle",

                    "line-style": "dashed",

                    "opacity": 0.5,

                    "width": 1
                }
            })

    return elements


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

        elements,

        layout_name="cose",

        stylesheet=[],

        height="950px",

        key="bcl2_network"
    )

    return selected
