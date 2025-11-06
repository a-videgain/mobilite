import hashlib
from datetime import datetime
import streamlit as st

# Génération des codes d'accès (50 groupes)
CODES_ACCES = {
    f"GROUPE{i:02d}": hashlib.md5(f"PB2050_G{i:02d}".encode()).hexdigest()[:8].upper() 
    for i in range(1, 51)
}
# ➕ AJOUT D'UN CODE SPÉCIAL POUR TEST
CODES_ACCES["TEST"] = "LOUVRE"

def verifier_login(code_groupe, mot_de_passe):
    """Vérifie si le code groupe et mot de passe sont valides"""
    if code_groupe in CODES_ACCES:
        return CODES_ACCES[code_groupe] == mot_de_passe.upper()
    return False

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
            'km_voiture': st.session_state.km_2025_territoire['voiture'],
            'km_bus': st.session_state.km_2025_territoire['bus'],
            'km_train': st.session_state.km_2025_territoire['train'],
            'part_ve_2025': st.session_state.parc_2025['part_ve']
        })
    elif type_validation == 'scenario_2050':
        data.update({
            'reduction_km': st.session_state.scenario['reduction_km'],
            'report_velo': st.session_state.scenario['report_velo'],
            'part_ve_2050': st.session_state.scenario['part_ve']
        })
    
    st.session_state.scenarios_log.append(data)
