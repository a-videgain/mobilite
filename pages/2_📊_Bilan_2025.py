# pages/2_📊_Bilan_2025.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import DISTANCE_TERRE_SOLEIL, initialiser_session
from utils.calculations import calculer_bilan_territoire, calculer_parts_modales, format_nombre

# Masquer le menu hamburger et le footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Initialisation
if 'initialized' not in st.session_state:
    initialiser_session()

# ⚠️ VÉRIFICATION DES ÉTAPES PRÉCÉDENTES
if not st.session_state.get('donnees_2025_validees', False):
    st.error("❌ Vous devez d'abord compléter l'étape 1 : Données 2025")
    if st.button("➡️ Aller à l'étape 1", type="primary"):
        st.switch_page("pages/1_📝_Donnees_2025.py")
    st.stop()


# ==================== PAGE 2 : BILAN 2025 ====================

st.set_page_config(page_title="📊 Bilan 2025", page_icon="", layout="wide")

st.title("🚗 Mobilité Pays Basque 2050")
st.header("📊 Bilan 2025")

# Vérification des données nécessaires
if 'km_2025_territoire' not in st.session_state:
    st.error("❌ Données 2025 manquantes. Veuillez d’abord compléter la page '📝 Données 2025'.")
    st.stop()

# Calcul du bilan 2025
bilan_2025 = calculer_bilan_territoire(
    st.session_state.km_2025_territoire,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    st.session_state.parc_2025,
    st.session_state.parc_velo_2025,
    st.session_state.parc_bus_2025,
    reduction_poids=0
)
parts_2025 = calculer_parts_modales(st.session_state.km_2025_territoire)

# Calculs par habitant
co2_par_hab = (bilan_2025['co2_total_territoire'] ) / st.session_state.population
km_par_hab_jour = (bilan_2025['km_total_territoire'] * 1e6) / st.session_state.population / 365
depl_par_hab_jour = sum(st.session_state.nb_depl_hab.values()) / 365

# Calcul équivalent Terre-Soleil
nb_terre_soleil = (bilan_2025['km_total_territoire'] * 1e6) / DISTANCE_TERRE_SOLEIL

# ==================== MÉTRIQUES ====================

st.subheader("🌍 Échelle territoire (Pays Basque français)")
col1, col2 = st.columns(2)
with col1:
    st.metric("Km totaux/an", f"{format_nombre(bilan_2025['km_total_territoire'])} millions de km")
    st.caption(f"Soit {nb_terre_soleil:.1f} fois la distance Terre-Soleil")
with col2:
    st.metric("CO₂ total/an", f"{format_nombre(bilan_2025['co2_total_territoire'])} tonnes")

st.divider()

st.subheader("👤 Échelle habitant (moyennes)")
col1, col2, col3 = st.columns(3)
with col3:
    st.metric("CO₂/habitant/an", f"{format_nombre(co2_par_hab,2)} tonnes")
with col1:
    st.metric("Km/habitant/jour", f"{format_nombre(km_par_hab_jour, 1)} km")
with col2:
    st.metric("Déplacements/habitant/jour", f"{depl_par_hab_jour:.2f}")

st.divider()

# ==================== GRAPHIQUES ====================

col1, col2 = st.columns(2)

# Parts modales
with col1:
    st.subheader("🥧 Parts modales 2025")
    df_parts = pd.DataFrame({
        'Mode': list(parts_2025.keys()),
        'Part (%)': list(parts_2025.values())
    })
    df_parts['Mode'] = df_parts['Mode'].map({
        'voiture': '🚗 Voiture',
        'bus': '🚌 Bus',
        'train': '🚆 Train',
        'velo': '🚴 Vélo',
        'avion': '✈️ Avion',
        'marche': '🚶 Marche'
    })
    fig_parts = px.pie(df_parts, values='Part (%)', names='Mode', hole=0.4, title="Répartition des km parcourus en 2025")
    fig_parts.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_parts, use_container_width=True)

# Émissions par mode
with col2:
    st.subheader("🌍 Émissions par mode (kg/hab/an)")
    emissions_hab_an = {mode: (co2 * 1000) / st.session_state.population for mode, co2 in bilan_2025['detail_par_mode'].items()}
    df_emissions = pd.DataFrame({
        'Mode': list(emissions_hab_an.keys()),
        'CO₂ (kg/hab/an)': list(emissions_hab_an.values())
    })
    df_emissions['Mode'] = df_emissions['Mode'].map({
        'voiture': '🚗 Voiture',
        'bus': '🚌 Bus',
        'train': '🚆 Train',
        'velo': '🚴 Vélo',
        'avion': '✈️ Avion',
        'marche': '🚶 Marche'
    })
    df_emissions = df_emissions.sort_values('CO₂ (kg/hab/an)', ascending=False)
    fig_emissions = px.bar(
        df_emissions,
        x='Mode',
        y='CO₂ (kg/hab/an)',
        text='CO₂ (kg/hab/an)',
        color='CO₂ (kg/hab/an)',
        color_continuous_scale='Reds',
        title="Contribution aux émissions"
    )
    fig_emissions.update_traces(texttemplate='%{text:.0f} kg', textposition='outside')
    fig_emissions.update_layout(showlegend=False)
    st.plotly_chart(fig_emissions, use_container_width=True)

st.divider()

# ==================== EXPORT DONNÉES DIAGNOSTIC 2025 ====================
st.subheader("💾 Export du diagnostic 2025")
st.info("📥 Sauvegardez vos données avant de passer à l'étape suivante")

# Préparer les données pour export CSV
data_export = []

# Territoire
data_export.append(['TERRITOIRE', ''])
data_export.append(['Population (habitants)', st.session_state.population])
data_export.append(['', ''])

# Mobilités par habitant
data_export.append(['MOBILITÉS PAR HABITANT (km/an/hab)', ''])
for mode, km in st.session_state.km_2025_habitant.items():
    data_export.append([mode.capitalize(), km])
data_export.append(['TOTAL', sum(st.session_state.km_2025_habitant.values())])
data_export.append(['', ''])

# Déplacements par habitant
data_export.append(['DÉPLACEMENTS PAR HABITANT (dépl/an/hab)', ''])
for mode, nb in st.session_state.nb_depl_hab.items():
    data_export.append([mode.capitalize(), f"{nb:.1f}"])
data_export.append(['TOTAL', f"{sum(st.session_state.nb_depl_hab.values()):.1f}"])
data_export.append(['', ''])

# Parc automobile
data_export.append(['PARC AUTOMOBILE 2025', ''])
data_export.append(['Part véhicules électriques (%)', st.session_state.parc_2025['part_ve']])
data_export.append(['Part véhicules thermiques (%)', st.session_state.parc_2025['part_thermique']])
data_export.append(['Émission voiture thermique (gCO₂/km ACV)', st.session_state.parc_2025['emission_thermique']])
data_export.append(['Émission voiture électrique (gCO₂/km ACV)', st.session_state.emissions['voiture_electrique']])
data_export.append(['Taux d\'occupation moyen (pers/véh)', f"{st.session_state.parc_2025['taux_occupation']:.1f}"])  # CORRIGÉ
data_export.append(['Temps stationné (%)', st.session_state.parc_2025['temps_stationnement']])
data_export.append(['', ''])

# Parc vélo
data_export.append(['PARC VÉLO 2025', ''])
data_export.append(['Part vélos électriques (%)', st.session_state.parc_velo_2025['part_elec']])
data_export.append(['Part vélos classiques (%)', st.session_state.parc_velo_2025['part_classique']])
data_export.append(['Émission vélo électrique (gCO₂/km ACV)', st.session_state.emissions['velo_elec']])
data_export.append(['Émission vélo classique (gCO₂/km ACV)', st.session_state.emissions['velo_classique']])
data_export.append(['', ''])

# Parc bus
data_export.append(['PARC BUS 2025', ''])
data_export.append(['Part bus électriques (%)', st.session_state.parc_bus_2025['part_elec']])
data_export.append(['Part bus thermiques (%)', st.session_state.parc_bus_2025['part_thermique']])
data_export.append(['Émission bus thermique (gCO₂/km/pass ACV)', st.session_state.emissions['bus_thermique']])
data_export.append(['Émission bus électrique (gCO₂/km/pass ACV)', st.session_state.emissions['bus_electrique']])
data_export.append(['', ''])

# Autres modes
data_export.append(['AUTRES MODES', ''])
data_export.append(['Émission train (gCO₂/km/pass)', st.session_state.emissions['train']])
data_export.append(['Émission avion (gCO₂/km/pass)', st.session_state.emissions['avion']])
data_export.append(['Émission marche (gCO₂/km)', st.session_state.emissions['marche']])
data_export.append(['', ''])

# Bilan territoire
data_export.append(['BILAN TERRITOIRE 2025', ''])
data_export.append(['CO₂ total territoire (tonnes/an)', f"{bilan_2025['co2_total_territoire']:.0f}"])
data_export.append(['CO₂ par habitant (tonnes/an)', f"{co2_par_hab:.2f}"])
data_export.append(['Km totaux territoire (Mkm/an)', f"{bilan_2025['km_total_territoire']:.1f}"])
data_export.append(['Km par habitant par jour (km/jour)', f"{km_par_hab_jour:.1f}"])
data_export.append(['Déplacements par habitant/jour', f"{depl_par_hab_jour:.2f}"])
data_export.append(['', ''])

# Émissions par mode
data_export.append(['ÉMISSIONS PAR MODE', 'tonnes CO₂/an', 'kg/hab/an'])
for mode in ['voiture', 'bus', 'train', 'velo', 'avion', 'marche']:
    co2_mode = bilan_2025['detail_par_mode'][mode]
    co2_hab_mode = (co2_mode / st.session_state.population) * 1000
    data_export.append([mode.capitalize(), f"{co2_mode:.0f}", f"{co2_hab_mode:.1f}"])
data_export.append(['', ''])

# Parts modales
data_export.append(['PARTS MODALES 2025 (% des km)', ''])
for mode, part in parts_2025.items():
    data_export.append([mode.capitalize(), f"{part:.1f}"])

# Convertir en DataFrame et exporter
df_export = pd.DataFrame(data_export)

# Générer le CSV avec encodage robuste
csv = df_export.to_csv(
    index=False, 
    header=False,  # Pas d'en-tête auto
    sep=';', 
    decimal=',',
    encoding='utf-8-sig',
    line_terminator='\n'  # Standard Unix
)

st.download_button(
    label="📥 Télécharger le diagnostic 2025 (CSV)",
    data=csv,
    file_name=f"diagnostic_2025_PB.csv",
    mime="text/csv;charset=utf-8",  # MIME type explicite
    use_container_width=True,
    key="download_diagnostic_2025"  # Clé unique pour éviter conflits
)

st.divider()

# ==================== QUESTIONS PÉDAGOGIQUES ====================

st.info(""" 
- Quels enseignements tirez-vous de cette situation 2025? 
- A titre personnel, comment vous positionnez-vous par rapport à la moyenne du territoire? 
""")


st.divider()

# ==================== VALIDATION ====================

if 'bilan_2025_valide' not in st.session_state:
    st.session_state.bilan_2025_valide = False

col_space1, col_btn, col_space2 = st.columns([1, 1, 1])
with col_btn:
    if st.button("✅ Valider le bilan 2025", type="primary", use_container_width=True):
        st.session_state.bilan_2025_valide = True
        st.rerun()

# Si validé, afficher bouton navigation
if st.session_state.bilan_2025_valide:
    st.success("✅ Bilan validé !")
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("➡️ Construire le scénario 2050", type="primary", use_container_width=True):
            st.switch_page("pages/3_🎯_Scenario_2050.py")
