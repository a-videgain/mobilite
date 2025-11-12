import streamlit as st
import pandas as pd

# Masquer le menu hamburger et le footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.set_page_config(
    page_title="Mobilité Pays Basque 2050",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Mobilité Pays Basque 2050")
st.info("👈 Utilisez la navigation à gauche pour accéder aux différentes pages")

if st.button("🚀 Commencez ici!", use_container_width=True):
    st.switch_page("pages/1_📝_Donnees_2025.py")
    st.session_state.logged_in = False
    st.session_state.code_groupe = None
    st.rerun()
