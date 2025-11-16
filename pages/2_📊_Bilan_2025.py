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

# Calcul km par habitant par mode
km_hab_2025 = {mode: (km_mkm * 1e6) / st.session_state.population for mode, km_mkm in st.session_state.km_2025_territoire.items()}

# Préparer le contenu texte
export_diagnostic = f"""==============================================
MOBILITÉ PAYS BASQUE - DIAGNOSTIC 2025
Date export ; {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
==============================================

--- TERRITOIRE ---
Population ; {format_nombre(st.session_state.population)} habitants

--- MOBILITÉS PAR HABITANT (km/an/hab) ---
Voiture ;      {st.session_state.km_2025_habitant['voiture']:>6} km/an
Bus/TC ;       {st.session_state.km_2025_habitant['bus']:>6} km/an
Train ;        {st.session_state.km_2025_habitant['train']:>6} km/an
Vélo ;         {st.session_state.km_2025_habitant['velo']:>6} km/an
Avion ;        {st.session_state.km_2025_habitant['avion']:>6} km/an
Marche ;       {st.session_state.km_2025_habitant['marche']:>6} km/an
TOTAL ;        {sum(st.session_state.km_2025_habitant.values()):>6} km/an

--- DÉPLACEMENTS PAR HABITANT (dépl/an/hab) ---
Voiture ;      {st.session_state.nb_depl_hab['voiture']:>6.1f} dépl/an
Bus/TC ;       {st.session_state.nb_depl_hab['bus']:>6.1f} dépl/an
Train ;        {st.session_state.nb_depl_hab['train']:>6.1f} dépl/an
Vélo ;         {st.session_state.nb_depl_hab['velo']:>6.1f} dépl/an
Avion ;        {st.session_state.nb_depl_hab['avion']:>6.1f} dépl/an
Marche ;       {st.session_state.nb_depl_hab['marche']:>6.1f} dépl/an
TOTAL ;        {sum(st.session_state.nb_depl_hab.values()):>6.1f} dépl/an

--- PARC AUTOMOBILE 2025 ---
Part véhicules électriques ;     {st.session_state.parc_2025['part_ve']}%
Part véhicules thermiques ;      {st.session_state.parc_2025['part_thermique']}%
Émission voiture thermique ;     {st.session_state.parc_2025['emission_thermique']} gCO₂/km ACV
Émission voiture électrique ;    {st.session_state.emissions['voiture_electrique']} gCO₂/km ACV
Taux d'occupation moyen ;        {st.session_state.parc_2025['taux_occupation']} pers/véh
Temps stationné ;                {st.session_state.parc_2025['temps_stationnement']}%

--- PARC VÉLO 2025 ---
Part vélos électriques ;         {st.session_state.parc_velo_2025['part_elec']}%
Part vélos classiques ;          {st.session_state.parc_velo_2025['part_classique']}%
Émission vélo électrique ;       {st.session_state.emissions['velo_elec']} gCO₂/km ACV
Émission vélo classique ;        {st.session_state.emissions['velo_classique']} gCO₂/km ACV

--- PARC BUS 2025 ---
Part bus électriques ;           {st.session_state.parc_bus_2025['part_elec']}%
Part bus thermiques ;            {st.session_state.parc_bus_2025['part_thermique']}%
Émission bus thermique ;         {st.session_state.emissions['bus_thermique']} gCO₂/km/passager ACV
Émission bus électrique ;        {st.session_state.emissions['bus_electrique']} gCO₂/km/passager ACV

--- AUTRES MODES ---
Émission train ;                 {st.session_state.emissions['train']} gCO₂/km/passager
Émission avion ;                 {st.session_state.emissions['avion']} gCO₂/km/passager
Émission marche ;                {st.session_state.emissions['marche']} gCO₂/km

--- BILAN TERRITOIRE 2025 ---
CO₂ total territoire ;           {format_nombre(bilan_2025['co2_total_territoire'])} tonnes/an
CO₂ par habitant ;               {format_nombre(co2_par_hab, 2)} tonnes/an
Km totaux territoire ;           {format_nombre(bilan_2025['km_total_territoire'])} millions km/an
Km par habitant par jour ;       {format_nombre(km_par_hab_jour, 1)} km/jour
Déplacements par habitant/jour ; {depl_par_hab_jour:.2f} dépl/jour

--- ÉMISSIONS PAR MODE (tonnes CO₂/an) ---
Voiture ;      {format_nombre(bilan_2025['detail_par_mode']['voiture']):>10} tonnes/an ;{format_nombre((bilan_2025['detail_par_mode']['voiture']/st.session_state.population)*1000, 1):>8} kg/hab/an
Bus ;          {format_nombre(bilan_2025['detail_par_mode']['bus']):>10} tonnes/an ;{format_nombre((bilan_2025['detail_par_mode']['bus']/st.session_state.population)*1000, 1):>8} kg/hab/an
Train ;        {format_nombre(bilan_2025['detail_par_mode']['train']):>10} tonnes/an ;{format_nombre((bilan_2025['detail_par_mode']['train']/st.session_state.population)*1000, 1):>8} kg/hab/an
Vélo ;         {format_nombre(bilan_2025['detail_par_mode']['velo']):>10} tonnes/an ;{format_nombre((bilan_2025['detail_par_mode']['velo']/st.session_state.population)*1000, 1):>8} kg/hab/an
Avion ;        {format_nombre(bilan_2025['detail_par_mode']['avion']):>10} tonnes/an ;{format_nombre((bilan_2025['detail_par_mode']['avion']/st.session_state.population)*1000, 1):>8} kg/hab/an
Marche ;       {format_nombre(bilan_2025['detail_par_mode']['marche']):>10} tonnes/an ;{format_nombre((bilan_2025['detail_par_mode']['marche']/st.session_state.population)*1000, 1):>8} kg/hab/an

--- PARTS MODALES 2025 (% des km parcourus) ---
Voiture ;      {parts_2025['voiture']:>6.1f}%
Bus ;          {parts_2025['bus']:>6.1f}%
Train ;        {parts_2025['train']:>6.1f}%
Vélo ;         {parts_2025['velo']:>6.1f}%
Avion ;        {parts_2025['avion']:>6.1f}%
Marche ;       {parts_2025['marche']:>6.1f}%

==============================================
"""

st.download_button(
    label="📥 Télécharger le diagnostic 2025 (TXT)",
    data=export_diagnostic,
    file_name=f"diagnostic_2025_PB.txt",
    mime="text/plain",
    use_container_width=True
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
