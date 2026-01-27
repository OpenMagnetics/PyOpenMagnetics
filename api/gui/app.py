"""
PyOpenMagnetics Design Tool - Streamlit GUI

A user-friendly interface for magnetic component design.

Run: streamlit run api/gui/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="PyOpenMagnetics Designer",
    page_icon="magnet",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Design", "Database", "Analysis", "Compare"],
    index=0
)

if page == "Design":
    from api.gui.pages import design
    design.render()
elif page == "Database":
    from api.gui.pages import database
    database.render()
elif page == "Analysis":
    from api.gui.pages import analysis
    analysis.render()
elif page == "Compare":
    from api.gui.pages import compare
    compare.render()
