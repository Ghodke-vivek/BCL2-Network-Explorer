import streamlit as st


# =========================================
# RELATION VIEWER
# =========================================

def render_relation_explorer(
    selected_node,
    df_main,
    df_cross
):

  st.markdown("## Relation Explorer")

    # =====================================
    # MAIN RELATIONS
    # =====================================

    related_main = df_main[
        (
            df_main["Source_NodeID"]
            == selected_node
        )
        |
        (
            df_main["Target_NodeID"]
            == selected_node
        )
    ]

    st.markdown(
        "### Main Chain Relations"
    )

    if len(related_main) > 0:

        st.dataframe(
            related_main,
            use_container_width=True
        )
   else:

        st.info(
            "No main-chain relations"
        )

    # =====================================
    # CROSS RELATIONS
    # =====================================

    related_cross = df_cross[
        (
            df_cross["Chain_Node"]
            == selected_node
        )
        |
        (
            df_cross["Connected_Node"]
            == selected_node
        )
    ]

    st.markdown(
        "### Cross Pathway Relations"
    )

    if len(related_cross) > 0:

        st.dataframe(
            related_cross,
            use_container_width=True
        )
     else:

        st.info(
            "No cross-pathway relations"
        )     
