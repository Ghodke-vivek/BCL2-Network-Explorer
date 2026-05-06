from metadata_loader import (
    load_metadata,
    extract_kegg_ids
)

metadata_lookup = load_metadata()


# =========================================
# BUILD NODE METADATA
# =========================================

def build_node_metadata(df_main, df_cross):

    metadata = {}

    # =====================================
    # MAIN NETWORK
    # =====================================

    for _, row in df_main.iterrows():

        source = str(row["Source_NodeID"])
        target = str(row["Target_NodeID"])

        interaction = str(row["Interaction"])

        source_kegg = extract_kegg_ids(
            row.get("Source", "")
        )

        target_kegg = extract_kegg_ids(
            row.get("Target", "")
        )

        # =================================
        # SOURCE NODE
        # =================================

        if source not in metadata:

            metadata[source] = {
                "type": "Protein",
                "cross_node": False,
                "connections": 0,
                "kegg_ids": source_kegg
            }

        # =================================
        # TARGET NODE
        # =================================

        if target not in metadata:

            metadata[target] = {
                "type": "Protein",
                "cross_node": False,
                "connections": 0,
                "kegg_ids": target_kegg
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

        target_kegg = extract_kegg_ids(
            row.get("Target_KEGG_IDs", "")
        )

        if node not in metadata:

            metadata[node] = {
                "type": "Protein",
                "cross_node": True,
                "connections": 1,
                "kegg_ids": target_kegg
            }

        metadata[node]["cross_node"] = True

    # =====================================
    # ATTACH BIOLOGICAL METADATA
    # =====================================

    for node, info in metadata.items():

        biological_data = []

        for kid in info["kegg_ids"]:

            if kid in metadata_lookup:

                biological_data.append(
                    metadata_lookup[kid]
                )

        metadata[node]["biological_data"] = biological_data

    return metadata
