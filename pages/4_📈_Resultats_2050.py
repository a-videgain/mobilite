# pages/4_📈_Resultats_2050.py

import streamlit as st
from utils.constants import initialiser_session
from utils.calculations import calculer_2050, format_nombre, calculer_parts_modales
import plotly.graph_objects as go
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

st.set_page_config(page_title="📈 Résultats 2050", page_icon="📈", layout="wide")

# Initialisation
if 'initialized' not in st.session_state:
    initialiser_session()

# Vérification des étapes précédentes
if not st.session_state.get('donnees_2025_validees', False):
    st.error("❌ Vous devez d'abord compléter l'étape 1 : Données 2025")
    if st.button("➡️ Aller à l'étape 1", type="primary"):
        st.switch_page("pages/1_📝_Donnees_2025.py")
    st.stop()

if not st.session_state.get('bilan_2025_valide', False):
    st.error("❌ Vous devez d'abord valider l'étape 2 : Bilan 2025")
    if st.button("➡️ Aller à l'étape 2", type="primary"):
        st.switch_page("pages/2_📊_Bilan_2025.py")
    st.stop()

if not st.session_state.get('scenario_2050_valide', False):
    st.error("❌ Vous devez d'abord valider l'étape 3 : Scénario 2050")
    if st.button("➡️ Aller à l'étape 3", type="primary"):
        st.switch_page("pages/3_🎯_Scenario_2050.py")
    st.stop()

# Calcul des résultats
resultats = calculer_2050()
st.session_state.resultats_2050 = resultats

st.title("📈 Résultats du scénario 2050")

# ==================== RÉSUMÉ DU SCÉNARIO ====================

st.header("📋 Résumé de votre scénario")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔧 Électrification")
    st.metric("🚗 Voitures électriques", f"{st.session_state.scenario['part_ve']}%")
    st.metric("🚌 Bus électriques", f"{st.session_state.scenario['part_bus_elec']}%")
    st.metric("🚴 Vélos électriques", f"{st.session_state.scenario['part_velo_elec']}%")

with col2:
    st.markdown("### 🌱 Sobriété")
    reduction_voiture = st.session_state.scenario.get('reduction_km_voiture', 0)
    reduction_avion = st.session_state.scenario.get('reduction_km_avion', 0)
    
    if reduction_voiture != 0:
        st.metric("🚗 Km voiture", f"{reduction_voiture:+.0f}%")
    else:
        st.metric("🚗 Km voiture", "Stable")
    
    if reduction_avion != 0:
        st.metric("✈️ Km avion", f"{reduction_avion:+.0f}%")
    else:
        st.metric("✈️ Km avion", "Stable")

with col3:
    st.markdown("### 🔄 Report modal")
    report_total_voiture = (st.session_state.scenario['report_velo'] + 
                           st.session_state.scenario['report_bus'] + 
                           st.session_state.scenario['report_train'])
    st.metric("Depuis voiture", f"{report_total_voiture}%")
    st.metric("Depuis avion", f"{st.session_state.scenario['report_train_avion']}%")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 👥 Taux de remplissage")
    st.metric("Occupation voiture", f"{st.session_state.scenario['taux_remplissage']:.1f} pers/véh")

with col2:
    st.markdown("### ⚖️ Allègement")
    if st.session_state.scenario['reduction_poids'] > 0:
        st.metric("Réduction poids", f"-{st.session_state.scenario['reduction_poids']}%")
    else:
        st.metric("Réduction poids", "Aucun")

st.divider()

# ==================== OBJECTIF ATTEINT ====================

st.header("🎯 Objectif climatique")

reduction_pct = resultats['reduction_pct']
objectif_atteint = resultats['objectif_atteint']

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if objectif_atteint:
        st.success(f"### ✅ Objectif ATTEINT : {reduction_pct:.1f}% de réduction")
        st.balloons()
    else:
        st.error(f"### ❌ Objectif NON atteint : {reduction_pct:.1f}% de réduction")
        st.warning(f"Il manque encore **{70 - reduction_pct:.1f} points** pour atteindre l'objectif de -70%")

st.divider()

# ==================== GRAPHIQUE CASCADE ====================

st.header("📊 Décomposition des leviers (cascade)")

# Calcul des contributions de chaque levier
co2_2025 = resultats['bilan_2025']['co2_total_territoire']
co2_2050 = resultats['bilan_2050']['co2_total_territoire']

# Calculer impact de chaque levier
km_2025_apres_sobriete = resultats['km_2025_apres_sobriete']

# 1. Impact sobriété (MODIFIÉ)
from utils.calculations import calculer_bilan_territoire
bilan_apres_sobriete = calculer_bilan_territoire(
    km_2025_apres_sobriete,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    st.session_state.parc_2025,
    st.session_state.parc_velo_2025,
    st.session_state.parc_bus_2025,
    reduction_poids=0
)
impact_sobriete = bilan_apres_sobriete['co2_total_territoire'] - co2_2025

# 2. Impact report modal
# Calculer avec sobriété + report modal, mais sans les autres leviers
parc_intermediaire = st.session_state.parc_2025.copy()
km_voiture = km_2025_apres_sobriete['voiture']
km_avion = km_2025_apres_sobriete['avion']

km_transferes_velo = km_voiture * st.session_state.scenario['report_velo'] / 100
km_transferes_bus = km_voiture * st.session_state.scenario['report_bus'] / 100
km_transferes_train_voiture = km_voiture * st.session_state.scenario['report_train'] / 100
km_transferes_train_avion = km_avion * st.session_state.scenario['report_train_avion'] / 100

km_apres_report = {
    'voiture': max(0, km_voiture - km_transferes_velo - km_transferes_bus - km_transferes_train_voiture),
    'bus': km_2025_apres_sobriete['bus'] + km_transferes_bus,
    'train': km_2025_apres_sobriete['train'] + km_transferes_train_voiture + km_transferes_train_avion,
    'velo': km_2025_apres_sobriete['velo'] + km_transferes_velo,
    'avion': max(0, km_avion - km_transferes_train_avion),
    'marche': km_2025_apres_sobriete['marche']
}

bilan_apres_report = calculer_bilan_territoire(
    km_apres_report,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    st.session_state.parc_2025,
    st.session_state.parc_velo_2025,
    st.session_state.parc_bus_2025,
    reduction_poids=0
)
impact_report = bilan_apres_report['co2_total_territoire'] - bilan_apres_sobriete['co2_total_territoire']

# 3. Impact électrification
parc_2050 = {
    'part_thermique': st.session_state.scenario['part_thermique'],
    'part_ve': st.session_state.scenario['part_ve'],
    'taux_occupation': st.session_state.parc_2025['taux_occupation']  # Sans taux de remplissage encore
}
parc_velo_2050 = {
    'part_elec': st.session_state.scenario['part_velo_elec'],
    'part_classique': st.session_state.scenario['part_velo_classique']
}
parc_bus_2050 = {
    'part_elec': st.session_state.scenario['part_bus_elec'],
    'part_thermique': st.session_state.scenario['part_bus_thermique']
}

bilan_apres_elec = calculer_bilan_territoire(
    km_apres_report,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_2050,
    parc_velo_2050,
    parc_bus_2050,
    reduction_poids=0
)
impact_electrification = bilan_apres_elec['co2_total_territoire'] - bilan_apres_report['co2_total_territoire']

# 4. Impact taux de remplissage
parc_2050_avec_remplissage = parc_2050.copy()
parc_2050_avec_remplissage['taux_occupation'] = st.session_state.scenario['taux_remplissage']

bilan_apres_remplissage = calculer_bilan_territoire(
    km_apres_report,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_2050_avec_remplissage,
    parc_velo_2050,
    parc_bus_2050,
    reduction_poids=0
)
impact_remplissage = bilan_apres_remplissage['co2_total_territoire'] - bilan_apres_elec['co2_total_territoire']

# 5. Impact allègement
impact_allegement = co2_2050 - bilan_apres_remplissage['co2_total_territoire']

# Graphique cascade
fig_cascade = go.Figure(go.Waterfall(
    name="Émissions CO₂",
    orientation="v",
    measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
    x=["2025", "Sobriété", "Report modal", "Électrification", "Taux remplissage", "Allègement", "2050"],
    y=[co2_2025, impact_sobriete, impact_report, impact_electrification, impact_remplissage, impact_allegement, co2_2050],
    text=[f"{co2_2025:.0f} t", 
          f"{impact_sobriete:+.0f} t", 
          f"{impact_report:+.0f} t",
          f"{impact_electrification:+.0f} t",
          f"{impact_remplissage:+.0f} t",
          f"{impact_allegement:+.0f} t",
          f"{co2_2050:.0f} t"],
    textposition="outside",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "green"}},
    increasing={"marker": {"color": "red"}},
    totals={"marker": {"color": "blue"}}
))

fig_cascade.update_layout(
    title="Contribution de chaque levier à la réduction des émissions",
    yaxis_title="Émissions CO₂ (tonnes/an)",
    showlegend=False,
    height=500
)

st.plotly_chart(fig_cascade, use_container_width=True)

st.divider()

# ==================== COMPARAISON KM ET CO2 ====================

st.header("📊 Comparaison 2025 vs 2050")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Kilomètres parcourus")
    km_2025_total = resultats['bilan_2025']['km_total_territoire']
    km_2050_total = resultats['bilan_2050']['km_total_territoire']
    
    st.metric("2025", f"{format_nombre(km_2025_total)} Mkm")
    st.metric("2050", f"{format_nombre(km_2050_total)} Mkm", 
             f"{((km_2050_total - km_2025_total) / km_2025_total * 100):+.1f}%")

with col2:
    st.subheader("Émissions CO₂")
    st.metric("2025", f"{format_nombre(co2_2025)} tonnes")
    st.metric("2050", f"{format_nombre(co2_2050)} tonnes", 
             f"{-reduction_pct:.1f}%")

st.divider()

# ==================== PARTS MODALES ====================

st.header("🥧 Évolution des parts modales")

parts_2025 = calculer_parts_modales(st.session_state.km_2025_territoire)
parts_2050 = calculer_parts_modales(resultats['km_2050_territoire'])

col1, col2 = st.columns(2)

with col1:
    st.subheader("2025")
    df_2025 = pd.DataFrame({
        'Mode': list(parts_2025.keys()),
        'Part (%)': list(parts_2025.values())
    })
    df_2025['Mode'] = df_2025['Mode'].map({
        'voiture': '🚗 Voiture',
        'bus': '🚌 Bus',
        'train': '🚆 Train',
        'velo': '🚴 Vélo',
        'avion': '✈️ Avion',
        'marche': '🚶 Marche'
    })
    
    import plotly.express as px
    fig_2025 = px.pie(df_2025, values='Part (%)', names='Mode', hole=0.4)
    fig_2025.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_2025, use_container_width=True)

with col2:
    st.subheader("2050")
    df_2050 = pd.DataFrame({
        'Mode': list(parts_2050.keys()),
        'Part (%)': list(parts_2050.values())
    })
    df_2050['Mode'] = df_2050['Mode'].map({
        'voiture': '🚗 Voiture',
        'bus': '🚌 Bus',
        'train': '🚆 Train',
        'velo': '🚴 Vélo',
        'avion': '✈️ Avion',
        'marche': '🚶 Marche'
    })
    
    fig_2050 = px.pie(df_2050, values='Part (%)', names='Mode', hole=0.4)
    fig_2050.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_2050, use_container_width=True)

st.divider()

# ==================== EXPORT CSV ====================

st.header("📥 Exporter les résultats")

# Créer le DataFrame d'export
data_export = {
    'Indicateur': [],
    'Valeur': []
}

# Informations générales
data_export['Indicateur'].extend([
    'Population',
    'CO2 2025 (tonnes)',
    'CO2 2050 (tonnes)',
    'Réduction CO2 (%)',
    'Objectif atteint'
])
data_export['Valeur'].extend([
    st.session_state.population,
    f"{co2_2025:.0f}",
    f"{co2_2050:.0f}",
    f"{reduction_pct:.1f}",
    'Oui' if objectif_atteint else 'Non'
])

# Scénario - Électrification
data_export['Indicateur'].extend([
    'Part VE 2050 (%)',
    'Part bus élec 2050 (%)',
    'Part vélos élec 2050 (%)'
])
data_export['Valeur'].extend([
    st.session_state.scenario['part_ve'],
    st.session_state.scenario['part_bus_elec'],
    st.session_state.scenario['part_velo_elec']
])

# Scénario - Sobriété
data_export['Indicateur'].extend([
    'Réduction km voiture (%)',
    'Réduction km avion (%)'
])
data_export['Valeur'].extend([
    st.session_state.scenario.get('reduction_km_voiture', 0),
    st.session_state.scenario.get('reduction_km_avion', 0)
])

# Scénario - Report modal
data_export['Indicateur'].extend([
    'Report voiture vers vélo (%)',
    'Report voiture vers bus (%)',
    'Report voiture vers train (%)',
    'Report avion vers train (%)'
])
data_export['Valeur'].extend([
    st.session_state.scenario['report_velo'],
    st.session_state.scenario['report_bus'],
    st.session_state.scenario['report_train'],
    st.session_state.scenario['report_train_avion']
])

# Scénario - Autres leviers
data_export['Indicateur'].extend([
    'Taux remplissage 2050',
    'Réduction poids (%)'
])
data_export['Valeur'].extend([
    st.session_state.scenario['taux_remplissage'],
    st.session_state.scenario['reduction_poids']
])

# Impacts des leviers
data_export['Indicateur'].extend([
    'Impact sobriété (tonnes CO2)',
    'Impact report modal (tonnes CO2)',
    'Impact électrification (tonnes CO2)',
    'Impact taux remplissage (tonnes CO2)',
    'Impact allègement (tonnes CO2)'
])
data_export['Valeur'].extend([
    f"{impact_sobriete:.0f}",
    f"{impact_report:.0f}",
    f"{impact_electrification:.0f}",
    f"{impact_remplissage:.0f}",
    f"{impact_allegement:.0f}"
])

df_export = pd.DataFrame(data_export)
csv = df_export.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Télécharger les résultats (CSV)",
    data=csv,
    file_name="scenario_mobilite_2050.csv",
    mime="text/csv",
    use_container_width=True
)

st.divider()

# ==================== NAVIGATION ====================

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("⬅️ Modifier le scénario", use_container_width=True):
        st.session_state.scenario_2050_valide = False
        st.switch_page("pages/3_🎯_Scenario_2050.py")

with col3:
    if st.button("🔄 Recommencer", use_container_width=True, type="secondary"):
        # Réinitialiser toutes les validations
        st.session_state.donnees_2025_validees = False
        st.session_state.bilan_2025_valide = False
        st.session_state.scenario_2050_valide = False
        st.switch_page("pages/1_📝_Donnees_2025.py")
