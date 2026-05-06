import streamlit as st


# =========================================
# HEADER
# =========================================

def render_header():

    st.title(
        "BCL2 Biological Pathway Explorer"
    )

    st.markdown(
        """
        Interactive upstream and downstream
        BCL2 pathway exploration platform.
        """
    )

# =========================================
# LEGEND
# =========================================

def render_legend():

    st.markdown(
        """
        ### Network Legend

        🟢 Gene Nodes

        🔵 Protein Nodes

        🟣 Cross Pathway Nodes

        🟠 Hub Nodes

        ---

        Green Edge → Activation

        Red Edge → Inhibition

        Cyan Edge → Expression

        Gray Dashed Edge → Cross Pathway
        """
    )
