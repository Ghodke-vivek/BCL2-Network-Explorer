import pandas as pd


def build_node_metadata(df_main, df_cross):

    metadata = {}

    # =====================================
    # MAIN NETWORK
    # =====================================

    for _, row in df_main.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

        # ---------------------------------
        # SOURCE
        # ---------------------------------

        if source not in metadata:

            metadata[source] = {
                "type": "Unknown",
                "cross_node": False,
                "connections": 0
            }

        # ---------------------------------
        # TARGET
        # ---------------------------------

        if target not in metadata:

            metadata[target] = {
                "type": "Unknown",
                "cross_node": False,
                "connections": 0
            }

        # =================================
        # GENE DETECTION
        # =================================

        if "GErel" in interaction:

            metadata[target]["type"] = "Gene"

        # =================================
        # CONNECTION COUNTS
        # =================================

        metadata[source]["connections"] += 1
        metadata[target]["connections"] += 1

    # =====================================
    # CROSS NODES
    # =====================================

    for _, row in df_cross.iterrows():

        node = str(row["Connected_Node"])

        if node not in metadata:

            metadata[node] = {
                "type": "Unknown",
                "cross_node": True,
                "connections": 1
            }

        metadata[node]["cross_node"] = True

    return metadata
