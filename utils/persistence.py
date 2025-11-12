import streamlit as st
from datetime import datetime

def sauvegarder_donnees(code_groupe):
    """Sauvegarde les données du groupe en mémoire globale"""
    try:
        # Créer stockage global si inexistant
        if 'all_groups_data' not in st.session_state:
            st.session_state.all_groups_data = {}
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Sauvegarder snapshot complet de la session du groupe
        st.session_state.all_groups_data[code_groupe] = {
            'timestamp': timestamp,
            'population': st.session_state.get('population', 350000),
            'km_2025_habitant': st.session_state.get('km_2025_habitant', {}).copy(),
            'nb_depl_hab': st.session_state.get('nb_depl_hab', {}).copy(),
            'km_2025_territoire': st.session_state.get('km_2025_territoire', {}).copy(),
            'parc_2025': st.session_state.get('parc_2025', {}).copy(),
            'parc_bus_2025': st.session_state.get('parc_bus_2025', {}).copy(),
            'parc_velo_2025': st.session_state.get('parc_velo_2025', {}).copy(),
            'emissions': st.session_state.get('emissions', {}).copy(),
            'scenario': st.session_state.get('scenario', {}).copy(),
            'resultats_2050': st.session_state.get('resultats_2050', {}).copy() if 'resultats_2050' in st.session_state else {},
            'donnees_2025_validees': st.session_state.get('donnees_2025_validees', False),
            'bilan_2025_valide': st.session_state.get('bilan_2025_valide', False),
            'scenario_2050_valide': st.session_state.get('scenario_2050_valide', False),
        }
        
        print(f"✅ Données sauvegardées en mémoire pour {code_groupe}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde {code_groupe}: {e}")
        return False

def charger_donnees(code_groupe):
    """Charge les données du groupe depuis la mémoire globale"""
    try:
        if 'all_groups_data' not in st.session_state:
            return None
        
        if code_groupe in st.session_state.all_groups_data:
            donnees = st.session_state.all_groups_data[code_groupe].copy()
            donnees['initialized'] = True
            print(f"✅ Données chargées depuis mémoire pour {code_groupe}")
            return donnees
        
        return None  # Pas de données pour ce groupe
        
    except Exception as e:
        print(f"❌ Erreur chargement {code_groupe}: {e}")
        return None

def get_all_groups_data():
    """Récupère toutes les données pour l'admin"""
    if 'all_groups_data' not in st.session_state:
        return []
    
    # Convertir en liste de dicts pour affichage tableau
    data_list = []
    for groupe, data in st.session_state.all_groups_data.items():
        row = {
            'groupe': groupe,
            'timestamp': data.get('timestamp', ''),
            'population': data.get('population', 0),
            'km_voiture_hab': data.get('km_2025_habitant', {}).get('voiture', 0),
            'part_ve_2025': data.get('parc_2025', {}).get('part_ve', 0),
            'reduction_km': data.get('scenario', {}).get('reduction_km', 0),
            'part_ve_2050': data.get('scenario', {}).get('part_ve', 0),
            'reduction_pct': data.get('resultats_2050', {}).get('reduction_pct', 0),
            'objectif_atteint': data.get('resultats_2050', {}).get('objectif_atteint', False),
        }
        data_list.append(row)
    
    return data_list
