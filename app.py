import streamlit as st
from utils.auth import verifier_login, enregistrer_connexion, CODES_ACCES
from utils.constants import initialiser_session
import pandas as pd

st.set_page_config(
    page_title="Mobilité Pays Basque 2050",
    page_icon="🚗",
    layout="wide"
)

# Init session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.code_groupe = None

# Page de login
if not st.session_state.logged_in:
    st.title("🚗 Mobilité Pays Basque 2050")
    st.markdown("### 🔐 Connexion")
    
    st.info("**Bienvenue** - Entrez vos identifiants pour accéder à l'application.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        code_groupe = st.text_input("Code groupe", placeholder="GROUPE01")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        
        if st.button("🔓 Se connecter", type="primary", use_container_width=True):
            if verifier_login(code_groupe, mot_de_passe):
                st.session_state.logged_in = True
                st.session_state.code_groupe = code_groupe
                enregistrer_connexion(code_groupe)
                initialiser_session()
                st.success(f"✅ Connexion réussie !")
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")
    
    # Zone admin
    with st.expander("👨‍🏫 Zone enseignant"):
        pwd = st.text_input("Mot de passe enseignant", type="password")
        if pwd == "ADMIN2050":
            df = pd.DataFrame([{'Groupe': k, 'MDP': v} for k, v in CODES_ACCES.items()])
            st.dataframe(df)
    
    st.stop()

# Une fois connecté
else:
    st.title("🚗 Mobilité Pays Basque 2050")
    st.success(f"✅ Connecté : **{st.session_state.code_groupe}**")
    st.info("👈 Utilisez la navigation à gauche pour accéder aux différentes pages")

    if st.button("Commencez ici:", use_container_width=True):
        st.switch_page("pages/1_Donnees_2025.py")
        
    if st.button("🚪 Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()
