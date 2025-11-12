import hashlib
from datetime import datetime
import streamlit as st

# Génération des codes d'accès (50 groupes)
CODES_ACCES = {
    f"GROUPE{i:02d}": hashlib.md5(f"PB2050_G{i:02d}".encode()).hexdigest()[:8].upper() 
    for i in range(1, 51)
}
# Codes spéciaux
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
    if 'all_groups_data' not in st.session_state:
        st.session_state.all_groups_data = {}
    return code_groupe in st.session_state.all_groups_data

def marquer_connecte(code_groupe):
    if 'all_groups_data' not in st.session_state:
        st.session_state.all_groups_data = {}
    
    st.session_state.all_groups_data[code_groupe] = {
        'connexion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'statut': 'connecte'
    }

def marquer_deconnecte(code_groupe):
    if 'all_groups_data' in st.session_state:
        if code_groupe in st.session_state.all_groups_data:
            st.session_state.all_groups_data[code_groupe]['statut'] = 'deconnecte'
            
def enregistrer_connexion(code_groupe):
    """Enregistre la connexion d'un groupe"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log dans session_state
    if 'connexions_log' not in st.session_state:
        st.session_state.connexions_log = []
    st.session_state.connexions_log.append({
        'groupe': code_groupe,
        'timestamp': timestamp
    })
    
    # Log dans console (visible dans logs Streamlit Cloud)
    print(f"[CONNEXION] {timestamp} | Groupe: {code_groupe}")

def enregistrer_scenario(code_groupe, type_validation):
    """Enregistre les données du scénario"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if 'scenarios_log' not in st.session_state:
        st.session_state.scenarios_log = []
    
    data = {
        'groupe': code_groupe,
        'timestamp': timestamp,
        'type': type_validation
    }
    
    if type_validation == 'bilan_2025':
        data.update({
            'population': st.session_state.get('population', 0),
            'km_voiture_hab': st.session_state.km_2025_habitant.get('voiture', 0),
            'km_voiture_territoire': st.session_state.km_2025_territoire.get('voiture', 0),
            'part_ve_2025': st.session_state.parc_2025.get('part_ve', 0)
        })
        # Log console
        print(f"[BILAN_2025] {timestamp} | {code_groupe} | Pop: {data['population']} | VE: {data['part_ve_2025']}%")
        
    elif type_validation == 'scenario_2050':
        data.update({
            'reduction_km': st.session_state.scenario.get('reduction_km', 0),
            'report_velo': st.session_state.scenario.get('report_velo', 0),
            'part_ve_2050': st.session_state.scenario.get('part_ve', 0),
            'taux_remplissage': st.session_state.scenario.get('taux_remplissage', 0)
        })
        # Log console
        print(f"[SCENARIO_2050] {timestamp} | {code_groupe} | Sobriété: {data['reduction_km']}% | VE: {data['part_ve_2050']}%")
    
    st.session_state.scenarios_log.append(data)
