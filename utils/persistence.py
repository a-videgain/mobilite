import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

def get_sheet():
    """Connexion au Google Sheet"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Charger credentials depuis secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        client = gspread.authorize(creds)
        sheet_id = st.secrets["sheet_id"]
        spreadsheet = client.open_by_key(sheet_id)
        return spreadsheet.worksheet("Groupes")
    except Exception as e:
        st.error(f"❌ Erreur connexion Google Sheets : {e}")
        return None

def sauvegarder_donnees(code_groupe):
    """Sauvegarde les données du groupe dans Google Sheets"""
    sheet = get_sheet()
    if not sheet:
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Préparer les données
        row_data = [
            code_groupe,
            timestamp,
            st.session_state.get('population', 0),
            # Données 2025 par habitant
            st.session_state.km_2025_habitant.get('voiture', 0),
            st.session_state.km_2025_habitant.get('bus', 0),
            st.session_state.km_2025_habitant.get('train', 0),
            st.session_state.km_2025_habitant.get('velo', 0),
            st.session_state.km_2025_habitant.get('avion', 0),
            st.session_state.km_2025_habitant.get('marche', 0),
            # Parc 2025
            st.session_state.parc_2025.get('part_ve', 0),
            st.session_state.parc_bus_2025.get('part_elec', 0),
            st.session_state.parc_velo_2025.get('part_elec', 0),
            # Scénario 2050
            st.session_state.scenario.get('reduction_km', 0),
            st.session_state.scenario.get('report_velo', 0),
            st.session_state.scenario.get('report_bus', 0),
            st.session_state.scenario.get('report_train', 0),
            st.session_state.scenario.get('report_train_avion', 0),
            st.session_state.scenario.get('part_ve', 0),
            st.session_state.scenario.get('taux_remplissage', 0),
            st.session_state.scenario.get('reduction_poids', 0),
        ]
        
        # Ajouter résultats si disponibles
        if 'resultats_2050' in st.session_state:
            row_data.extend([
                st.session_state.resultats_2050.get('reduction_pct', 0),
                st.session_state.resultats_2050.get('objectif_atteint', False)
            ])
        else:
            row_data.extend([0, False])
        
        # Chercher si le groupe existe déjà
        all_records = sheet.get_all_records()
        row_index = None
        
        for idx, record in enumerate(all_records):
            if record.get('groupe') == code_groupe:
                row_index = idx + 2  # +2 car ligne 1 = header, index commence à 0
                break
        
        if row_index:
            # Mettre à jour la ligne existante
            for col_idx, value in enumerate(row_data, start=1):
                sheet.update_cell(row_index, col_idx, value)
        else:
            # Ajouter nouvelle ligne
            sheet.append_row(row_data)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erreur sauvegarde : {e}")
        return False

def charger_donnees(code_groupe):
    """Charge les données du groupe depuis Google Sheets"""
    sheet = get_sheet()
    if not sheet:
        return None
    
    try:
        all_records = sheet.get_all_records()
        
        for record in all_records:
            if record.get('groupe') == code_groupe:
                # Reconstituer les données en session_state
                return {
                    'population': record.get('population', 350000),
                    'km_2025_habitant': {
                        'voiture': record.get('km_voiture_hab', 9357),
                        'bus': record.get('km_bus_hab', 157),
                        'train': record.get('km_train_hab', 600),
                        'velo': record.get('km_velo_hab', 400),
                        'avion': record.get('km_avion_hab', 2571),
                        'marche': record.get('km_marche_hab', 200),
                    },
                    'parc_2025': {
                        'part_ve': record.get('part_ve_2025', 3),
                        'part_thermique': 100 - record.get('part_ve_2025', 3),
                        'emission_thermique': 218,
                        'taux_occupation': 1.1,
                        'temps_stationnement': 95
                    },
                    'parc_bus_2025': {
                        'part_elec': record.get('part_bus_elec_2025', 5),
                        'part_thermique': 100 - record.get('part_bus_elec_2025', 5),
                    },
                    'parc_velo_2025': {
                        'part_elec': record.get('part_velo_elec_2025', 15),
                        'part_classique': 100 - record.get('part_velo_elec_2025', 15),
                    },
                    'scenario': {
                        'reduction_km': record.get('reduction_km', 0),
                        'report_velo': record.get('report_velo', 0),
                        'report_bus': record.get('report_bus', 0),
                        'report_train': record.get('report_train', 0),
                        'report_train_avion': record.get('report_train_avion', 0),
                        'part_ve': record.get('part_ve_2050', 3),
                        'part_thermique': 100 - record.get('part_ve_2050', 3),
                        'taux_remplissage': record.get('taux_remplissage', 1.1),
                        'part_velo_elec': record.get('part_velo_elec_2025', 15),
                        'part_velo_classique': 100 - record.get('part_velo_elec_2025', 15),
                        'part_bus_elec': record.get('part_bus_elec_2025', 5),
                        'part_bus_thermique': 100 - record.get('part_bus_elec_2025', 5),
                        'reduction_poids': record.get('reduction_poids', 0),
                    },
                    'donnees_chargees': True
                }
        
        return None  # Groupe pas trouvé
        
    except Exception as e:
        st.error(f"❌ Erreur chargement : {e}")
        return None

def get_all_groups_data():
    """Récupère toutes les données pour l'admin"""
    sheet = get_sheet()
    if not sheet:
        return None
    
    try:
        return sheet.get_all_records()
    except Exception as e:
        st.error(f"❌ Erreur récupération données : {e}")
        return None
