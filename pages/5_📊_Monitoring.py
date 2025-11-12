import streamlit as st
import psutil
import os

st.set_page_config(page_title="📊 Monitoring", layout="wide")

# Masquer le menu hamburger et le footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("📊 Ressources système")

# Mémoire
mem = psutil.virtual_memory()
col1, col2 = st.columns(2)
with col1:
    st.metric("Mémoire utilisée", f"{mem.used / 1024**3:.2f} GB")
with col2:
    st.metric("Mémoire totale", f"{mem.total / 1024**3:.2f} GB")
st.progress(mem.percent / 100)

st.divider()

# CPU
cpu_percent = psutil.cpu_percent(interval=1)
st.metric("CPU", f"{cpu_percent}%")
st.progress(cpu_percent / 100)

st.divider()

# Processus actuel
process = psutil.Process(os.getpid())
st.metric("Mémoire de cette app", f"{process.memory_info().rss / 1024**2:.1f} MB")

st.divider()

# Session state
if st.checkbox("Voir détails session_state"):
    st.json(dict(st.session_state))
    st.metric("Taille session_state", f"{len(str(st.session_state))} caractères")
