from streamlit_cytoscapejs import cytoscapejs


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
# BUILD CYTOSCAPE ELEMENTS
# =========================================

def build_cytoscape_elements(
    df_main,
    df_cross,
    metadata,
    include_cross_nodes
):

    elements = []

    main_chain_nodes = set()

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

        main_chain_nodes.add(source)
        main_chain_nodes.add(target)

        # =================================
        # SOURCE NODE
        # =================================

        if not any(
            el["data"]["id"] == source
            for el in elements
            if "id" in el["data"]
        ):

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
                    "label": source,
                    "type": node_type
                },

                "classes": "main"
            })

        # =================================
        # TARGET NODE
        # =================================

        if not any(
            el["data"]["id"] == target
            for el in elements
            if "id" in el["data"]
        ):

            node_info = metadata.get(
                target,
                {}
            )

            node_type = node_info.get(
                "type",
                "Protein"
            )

            elements.append({

                "data": {
                    "id": target,
                    "label": target,
                    "type": node_type
                },

                "classes": "main"
            })

        # =================================
        # EDGE
        # =================================

        elements.append({

            "data": {

                "source": source,
                "target": target,

                "interaction": interaction,

                "color": get_edge_color(
                    interaction
                )
            }
        })

    # =====================================
    # CROSS NODES
    # =====================================

    if include_cross_nodes:

        for _, row in df_cross.iterrows():

            chain_node = str(
                row["Chain_Node"]
            )

            connected_node = str(
                row["Connected_Node"]
            )

            # ONLY contextual node
            # NO expansion

            if not any(
                el["data"]["id"]
                == connected_node
                for el in elements
                if "id" in el["data"]
            ):

                elements.append({

                    "data": {

                        "id": connected_node,

                        "label": connected_node,

                        "type": "CrossPathway"
                    },

                    "classes": "cross"
                })

            elements.append({

                "data": {

                    "source": chain_node,

                    "target": connected_node,

                    "interaction": "Cross Pathway",

                    "color": "#777777"
                },

                "classes": "cross_edge"
            })

    return elements


# =========================================
# CYTOSCAPE STYLE
# =========================================

def get_stylesheet():

    return [

        # =================================
        # DEFAULT NODE
        # =================================

        {
            "selector": "node",

            "style": {

                "background-color": "#4DA6FF",

                "label": "data(label)",

                "color": "white",

                "font-size": "14px",

                "text-valign": "center",

                "text-halign": "center",

                "width": 35,

                "height": 35,

                "border-width": 2,

                "border-color": "#FFFFFF"
            }
        },

        # =================================
        # MAIN CHAIN
        # =================================

        {
            "selector": ".main",

            "style": {

                "background-color": "#4DA6FF"
            }
        },

        # =================================
        # CROSS PATHWAY
        # =================================

        {
            "selector": ".cross",

            "style": {

                "background-color": "#8C7AE6",

                "opacity": 0.45,

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

                "width": 4,

                "line-color": "data(color)",

                "target-arrow-color": "data(color)",

                "target-arrow-shape": "triangle"
            }
        },

        # =================================
        # CROSS EDGES
        # =================================

        {
            "selector": ".cross_edge",

            "style": {

                "width": 1,

                "line-style": "dashed",

                "opacity": 0.5
            }
        },

        # =================================
        # SELECTED NODE
        # =================================

        {
            "selector": ":selected",

            "style": {

                "border-width": 6,

                "border-color": "#FFFF00"
            }
        }
    ]


# =========================================
# BUILD CYTOSCAPE GRAPH
# =========================================

def render_cytoscape(
    df_main,
    df_cross,
    metadata,
    include_cross_nodes
):

    elements = build_cytoscape_elements(
        df_main,
        df_cross,
        metadata,
        include_cross_nodes
    )

    return cytoscapejs(

        elements=elements,

        stylesheet=get_stylesheet(),

        layout={
            "name": "cose"
        },

        style={
            "width": "100%",
            "height": "950px",
            "backgroundColor": "#0B0F1A"
        }
    )
