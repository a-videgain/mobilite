import hashlib
from datetime import datetime
import streamlit as st

# Génération des codes d'accès (50 groupes)
# Charger depuis les secrets si disponible
if "codes_acces" in st.secrets:
    CODES_ACCES = dict(st.secrets["codes_acces"])
else:
    # Fallback : génération automatique
    CODES_ACCES = {
        f"GROUPE{i:02d}": hashlib.md5(f"PB2050_G{i:02d}".encode()).hexdigest()[:8].upper() 
        for i in range(1, 51)
    }
# ➕ AJOUT D'UN CODE SPÉCIAL POUR TEST
CODES_ACCES["BENJAMIN"] = "LOREILLE"
CODES_ACCES["TEST"] = "LOUVRE"

# Variable globale pour tracker les sessions actives
if 'sessions_actives' not in st.session_state:
    st.session_state.sessions_actives = {}

def verifier_login(code_groupe, mot_de_passe):
    """Vérifie si le code groupe et mot de passe sont valides"""
    if code_groupe in CODES_ACCES:
        return CODES_ACCES[code_groupe] == mot_de_passe.upper()
    return False

def est_deja_connecte(code_groupe):
    """Vérifie si le groupe est déjà connecté"""
    # Initialiser le dictionnaire global si nécessaire
    if 'groupes_connectes' not in st.session_state:
        st.session_state.groupes_connectes = set()
    
    return code_groupe in st.session_state.groupes_connectes

def marquer_connecte(code_groupe):
    """Marque un groupe comme connecté"""
    if 'groupes_connectes' not in st.session_state:
        st.session_state.groupes_connectes = set()
    
    st.session_state.groupes_connectes.add(code_groupe)

def marquer_deconnecte(code_groupe):
    """Marque un groupe comme déconnecté"""
    if 'groupes_connectes' in st.session_state and code_groupe in st.session_state.groupes_connectes:
        st.session_state.groupes_connectes.discard(code_groupe)

def enregistrer_connexion(code_groupe):
    """Enregistre la connexion d'un groupe"""
    if 'connexions_log' not in st.session_state:
        st.session_state.connexions_log = []
    
    st.session_state.connexions_log.append({
        'groupe': code_groupe,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def enregistrer_scenario(code_groupe, type_validation):
    """Enregistre les données du scénario"""
    if 'scenarios_log' not in st.session_state:
        st.session_state.scenarios_log = []
    
    data = {
        'groupe': code_groupe,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': type_validation
    }
    
    if type_validation == 'bilan_2025':
        data.update({
            'km_voiture': st.session_state.km_2025_territoire.get('voiture', 0),
            'km_bus': st.session_state.km_2025_territoire.get('bus', 0),
            'km_train': st.session_state.km_2025_territoire.get('train', 0),
            'part_ve_2025': st.session_state.parc_2025.get('part_ve', 0)
        })
    elif type_validation == 'scenario_2050':
        data.update({
            'reduction_km': st.session_state.scenario.get('reduction_km', 0),
            'report_velo': st.session_state.scenario.get('report_velo', 0),
            'part_ve_2050': st.session_state.scenario.get('part_ve', 0)
        })
    
    st.session_state.scenarios_log.append(data)
