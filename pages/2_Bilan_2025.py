# pages/2_📊_Bilan_2025.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import POPULATION_PB, DISTANCE_TERRE_SOLEIL
from utils.calculations import calculer_bilan_territoire, calculer_parts_modales, format_nombre
from utils.auth import enregistrer_scenario

# ==================== PAGE 2 : BILAN 2025 ====================

st.set_page_config(page_title="📊 Bilan 2025", page_icon="📊", layout="wide")

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
co2_par_hab = (bilan_2025['co2_total_territoire'] * 1000) / POPULATION_PB
km_par_hab_jour = (bilan_2025['km_total_territoire'] * 1e6) / POPULATION_PB / 365
depl_par_hab_jour = sum(st.session_state.nb_depl_hab.values()) / 365

# Calcul équivalent Terre-Soleil
nb_terre_soleil = (bilan_2025['km_total_territoire'] * 1e6) / DISTANCE_TERRE_SOLEIL

# ==================== MÉTRIQUES ====================

st.subheader("🌍 Échelle territoire (350 000 habitants)")
col1, col2 = st.columns(2)
with col1:
    st.metric("Km totaux/an", f"{format_nombre(bilan_2025['km_total_territoire'])} Mkm")
    st.caption(f"Soit {nb_terre_soleil:.1f} fois la distance Terre-Soleil")
with col2:
    st.metric("CO₂ total/an", f"{format_nombre(bilan_2025['co2_total_territoire'])} tonnes")

st.divider()

st.subheader("👤 Échelle habitant (moyennes)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("CO₂/habitant/an", f"{format_nombre(co2_par_hab)} kg")
with col2:
    st.metric("Km/habitant/jour", f"{format_nombre(km_par_hab_jour, 1)} km")
with col3:
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
    fig_parts = px.pie(df_parts, values='Part (%)', names='Mode', hole=0.4, title="Répartition des km parcourus")
    fig_parts.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_parts, use_container_width=True)

# Émissions par mode
with col2:
    st.subheader("🌍 Émissions par mode (kg/hab/an)")
    emissions_hab_an = {mode: (co2 * 1000) / POPULATION_PB for mode, co2 in bilan_2025['detail_par_mode'].items()}
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

# ==================== VALIDATION ====================

col_space1, col_btn, col_space2 = st.columns([1, 1, 1])
with col_btn:
    if st.button("➡️ Construire le scénario 2050", type="primary", use_container_width=True):
        enregistrer_scenario(st.session_state.code_groupe, 'bilan_2025')
        st.switch_page("pages/3_🎯_Scenario_2050.py")

