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
                    
                    # Charger données sauvegardées si elles existent
                    from utils.persistence import charger_donnees
                    donnees_sauvegardees = charger_donnees(code_groupe)
                    
                    if donnees_sauvegardees:
                        # Restaurer les données
                        st.session_state.update(donnees_sauvegardees)
                        st.success(f"✅ Connexion réussie ! Données restaurées.")
                    else:
                        # Initialiser avec valeurs par défaut
                        initialiser_session()
                        st.success(f"✅ Connexion réussie ! Nouvelle session.")
                    
                    st.rerun()
            else:
                st.error("❌ Identifiants incorrects")
    
    # Zone admin - MOT DE PASSE SÉCURISÉ
    with st.expander("👨‍🏫 Zone enseignant"):
        pwd = st.text_input("Mot de passe enseignant", type="password", key="admin_pwd")
        
        # Récupérer le mot de passe depuis les secrets Streamlit Cloud
        if "admin_password" in st.secrets:
            admin_password = st.secrets["admin_password"]
        else:
            admin_password = "ADMIN2050"
            st.caption("⚠️ Mode développement local - Configurez les secrets sur Streamlit Cloud")
        
        if pwd == admin_password:
            st.success("✅ Accès enseignant activé")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Codes", "🟢 Connectés", "📊 Connexions", "💾 Scénarios", "📈 Données Live"])
            
            with tab1:
                st.markdown("**📋 Codes d'accès groupes**")
                df = pd.DataFrame([{'Groupe': k, 'Mot de passe': v} for k, v in CODES_ACCES.items()])
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Télécharger les codes (CSV)",
                    csv,
                    "codes_acces.csv",
                    "text/csv"
                )
            
            with tab2:
                st.markdown("**🟢 Groupes actuellement connectés**")
                if 'groupes_connectes' in st.session_state and st.session_state.groupes_connectes:
                    for groupe in sorted(st.session_state.groupes_connectes):
                        st.write(f"- {groupe}")
                else:
                    st.info("Aucun groupe connecté")
            
            with tab3:
                st.markdown("**📊 Historique des connexions**")
                if 'connexions_log' in st.session_state and st.session_state.connexions_log:
                    df_cnx = pd.DataFrame(st.session_state.connexions_log)
                    st.dataframe(df_cnx, use_container_width=True)
                    
                    st.metric("Total connexions", len(df_cnx))
                    st.metric("Groupes uniques", df_cnx['groupe'].nunique())
                else:
                    st.info("Aucune connexion enregistrée")
            
            with tab4:
                st.markdown("**💾 Scénarios validés (session)**")
                if 'scenarios_log' in st.session_state and st.session_state.scenarios_log:
                    df_scen = pd.DataFrame(st.session_state.scenarios_log)
                    st.dataframe(df_scen, use_container_width=True)
                    
                    csv_scen = df_scen.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "⬇️ Télécharger les scénarios (CSV)",
                        csv_scen,
                        "scenarios_groupes.csv",
                        "text/csv"
                    )
                else:
                    st.info("Aucun scénario validé")



            with tab5:
                st.markdown("**📈 Données sauvegardées (Mémoire)**")
                
                if st.button("🔄 Actualiser"):
                    st.rerun()
                
                from utils.persistence import get_all_groups_data
                all_data = get_all_groups_data()
                
                if all_data:
                    df_live = pd.DataFrame(all_data)
                    st.dataframe(df_live, use_container_width=True)
                    
                    st.metric("Groupes ayant sauvegardé", len(df_live))
                    
                    csv_live = df_live.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "⬇️ Télécharger (CSV)",
                        csv_live,
                        f"donnees_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv"
                    )
                    
                    st.warning("⚠️ Données en mémoire - Perdues au redémarrage app")
                else:
                    st.info("Aucune donnée sauvegardée")


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
