import streamlit as st

# Constantes globales
POPULATION_PB = 350000
DISTANCE_TERRE_SOLEIL = 149.6e6

def initialiser_session():
    """Initialise toutes les variables de session"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        
        st.session_state.km_2025_territoire = {
            'voiture': 3275, 'bus': 55, 'train': 210,
            'velo': 140, 'avion': 900, 'marche': 70
        }
        
        st.session_state.nb_depl_hab = {
            'voiture': 401.5, 'bus': 219.0, 'train': 54.75,
            'velo': 255.5, 'avion': 5.11, 'marche': 511.0
        }
        
        st.session_state.parc_2025 = {
            'part_ve': 3, 'part_thermique': 97,
            'emission_thermique': 218, 'taux_occupation': 1.1,
            'temps_stationnement': 95
        }
        
        st.session_state.parc_velo_2025 = {
            'part_elec': 15, 'part_classique': 85
        }
        
        st.session_state.parc_bus_2025 = {
            'part_elec': 5, 'part_thermique': 95
        }
        
        st.session_state.emissions = {
            'voiture_electrique': 103, 'bus_thermique': 127,
            'bus_electrique': 25, 'train': 5.1,
            'velo_elec': 22, 'velo_classique': 5,
            'avion': 225, 'marche': 0
        }
        
        st.session_state.scenario = {
            'reduction_km': 0, 'report_velo': 0, 'report_bus': 0,
            'report_train': 0, 'report_train_avion': 0,
            'taux_remplissage': 1.1, 'part_ve': 3, 'part_thermique': 97,
            'part_velo_elec': 15, 'part_velo_classique': 85,
            'part_bus_elec': 5, 'part_bus_thermique': 95,
            'reduction_poids': 0
        }

def format_nombre(n, decimales=0):
    """Formate un nombre avec espaces entre milliers"""
    if decimales == 0:
        return f"{n:,.0f}".replace(',', ' ')
    else:
        return f"{n:,.{decimales}f}".replace(',', ' ')
