import streamlit as st
from utils.auth import verifier_login, enregistrer_connexion, est_deja_connecte, marquer_connecte, marquer_deconnecte, CODES_ACCES
from utils.constants import initialiser_session
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

# Init session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.code_groupe = None

# Gérer la déconnexion propre
if st.session_state.logged_in and st.session_state.code_groupe:
    # Ajouter un callback de déconnexion en cas de fermeture
    if 'deconnexion_enregistree' not in st.session_state:
        st.session_state.deconnexion_enregistree = False

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
                # ⚠️ VÉRIFICATION : Groupe déjà connecté ?
                if est_deja_connecte(code_groupe):
                    st.error("❌ Ce groupe est déjà connecté sur une autre session !")
                    st.warning("⚠️ Un seul ordinateur par groupe. Si vous avez fermé la session précédente, attendez 30 secondes et réessayez.")
                else:
                    # Connexion réussie
                    st.session_state.logged_in = True
                    st.session_state.code_groupe = code_groupe
                    marquer_connecte(code_groupe)
                    enregistrer_connexion(code_groupe)
                    initialiser_session()
                    st.success(f"✅ Connexion réussie !")
                    st.rerun()
            else:
                st.error("❌ Identifiants incorrects")
    
    # Zone admin - MOT DE PASSE SÉCURISÉ
    with st.expander("👨‍🏫 Zone enseignant"):
        pwd = st.text_input("Mot de passe enseignant", type="password", key="admin_pwd")
        
        # Récupérer le mot de passe depuis les secrets Streamlit Cloud
        # OU utiliser une valeur par défaut pour le développement local
        if "admin_password" in st.secrets:
            admin_password = st.secrets["admin_password"]
        else:
            # Mot de passe par défaut pour développement local uniquement
            admin_password = "ADMIN2025"
            st.caption("⚠️ Mode développement local - Configurez les secrets sur Streamlit Cloud")
        
        if pwd == admin_password:
            df = pd.DataFrame([{'Groupe': k, 'MDP': v} for k, v in CODES_ACCES.items()])
            st.dataframe(df)
            
            # Afficher les groupes connectés
            if 'groupes_connectes' in st.session_state:
                st.markdown("**🟢 Groupes actuellement connectés :**")
                if st.session_state.groupes_connectes:
                    for groupe in st.session_state.groupes_connectes:
                        st.write(f"- {groupe}")
                else:
                    st.write("Aucun groupe connecté")
    
    st.stop()

# Une fois connecté
else:
    st.title("🚗 Mobilité Pays Basque 2050")
    st.success(f"✅ Connecté : **{st.session_state.code_groupe}**")
    st.info("👈 Utilisez la navigation à gauche pour accéder aux différentes pages")

    if st.button("🚀 Commencez ici!", use_container_width=True):
        st.switch_page("pages/1_📝_Donnees_2025.py")
        
    if st.button("🚪 Se déconnecter"):
        # Marquer comme déconnecté
        if st.session_state.code_groupe:
            marquer_deconnecte(st.session_state.code_groupe)
        st.session_state.logged_in = False
        st.session_state.code_groupe = None
        st.rerun()
