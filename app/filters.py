# Placeholder for future filtering system


def filter_nodes_by_type(
    metadata,
    node_type
):

    return {
        k: v
        for k, v in metadata.items()
        if v["type"] == node_type
    }
