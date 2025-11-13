# pages/4_📈_Resultats_2050.py

import streamlit as st
from utils.constants import initialiser_session
from utils.calculations import calculer_2050, format_nombre, calculer_parts_modales
import plotly.graph_objects as go
import plotly.express as px
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

st.title("🚗 Mobilité Pays Basque 2050")
st.header("📈 Résultats de votre scénario 2050")

# ==================== OBJECTIF ATTEINT ====================

reduction_pct = resultats['reduction_pct']
objectif_atteint = resultats['objectif_atteint']

if objectif_atteint:
    st.success(f"### 🎉 Félicitations ! Objectif atteint : **{reduction_pct:.1f}%** de réduction des émissions")
    st.balloons()
else:
    st.error(f"### ❌ Objectif non atteint : **{reduction_pct:.1f}%** de réduction")
    st.warning(f"Il manque **{70 - reduction_pct:.1f} points** pour atteindre les -70% de la SNBC")

st.divider()

# ==================== MÉTRIQUES PRINCIPALES ====================

st.subheader("📊 Bilan comparatif 2025 vs 2050")

col1, col2, col3 = st.columns(3)

co2_2025 = resultats['bilan_2025']['co2_total_territoire']
co2_2050 = resultats['bilan_2050']['co2_total_territoire']
km_2025 = resultats['bilan_2025']['km_total_territoire']
km_2050 = resultats['bilan_2050']['km_total_territoire']

with col1:
    st.metric(
        "CO₂ total (tonnes/an)",
        f"{format_nombre(co2_2050)}",
        f"{format_nombre(co2_2050 - co2_2025)} ({-reduction_pct:.1f}%)",
        delta_color="inverse"
    )

with col2:
    st.metric(
        "Km totaux (Mkm/an)",
        f"{format_nombre(km_2050)}",
        f"{format_nombre(km_2050 - km_2025)} ({((km_2050 - km_2025)/km_2025*100):.1f}%)",
        delta_color="inverse"
    )

with col3:
    co2_hab_2025 = co2_2025 / st.session_state.population
    co2_hab_2050 = co2_2050 / st.session_state.population
    st.metric(
        "CO₂/habitant (tonnes/an)",
        f"{co2_hab_2050:.2f}",
        f"{co2_hab_2050 - co2_hab_2025:.2f} ({((co2_hab_2050 - co2_hab_2025)/co2_hab_2025*100):.1f}%)",
        delta_color="inverse"
    )

st.divider()

# ==================== RÉSUMÉ TEXTUEL DU SCÉNARIO ====================

st.subheader("📝 Résumé de votre scénario")

# MODIFIÉ : Sobriété séparée voiture/avion
reduction_voiture = st.session_state.scenario.get('reduction_km_voiture', 0)
reduction_avion = st.session_state.scenario.get('reduction_km_avion', 0)

sobriete_text = "**Sobriété :** "
if reduction_voiture == 0 and reduction_avion == 0:
    sobriete_text += "Aucune réduction des km."
else:
    parts = []
    if reduction_voiture != 0:
        parts.append(f"voiture {reduction_voiture:+.0f}%")
    if reduction_avion != 0:
        parts.append(f"avion {reduction_avion:+.0f}%")
    sobriete_text += ", ".join(parts) + "."

report_parts = []
if st.session_state.scenario['report_velo'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_velo']}% voiture→vélo")
if st.session_state.scenario['report_bus'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_bus']}% voiture→bus")
if st.session_state.scenario['report_train'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_train']}% voiture→train")
if st.session_state.scenario['report_train_avion'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_train_avion']}% avion→train")

report_text = "**Report modal :** "
if report_parts:
    report_text += ", ".join(report_parts) + "."
else:
    report_text += "Aucun report modal."

elec_text = f"**Électrification :** {st.session_state.scenario['part_ve']}% voitures élec, {st.session_state.scenario['part_bus_elec']}% bus élec, {st.session_state.scenario['part_velo_elec']}% vélos élec."

remplissage_text = f"**Taux de remplissage :** {st.session_state.scenario['taux_remplissage']:.1f} pers/véhicule"
if st.session_state.scenario['taux_remplissage'] > st.session_state.parc_2025['taux_occupation']:
    gain = ((st.session_state.scenario['taux_remplissage'] - st.session_state.parc_2025['taux_occupation']) / st.session_state.parc_2025['taux_occupation'] * 100)
    remplissage_text += f" (+{gain:.0f}% vs 2025)."
else:
    remplissage_text += "."

allegement_text = "**Allègement :** "
if st.session_state.scenario['reduction_poids'] > 0:
    allegement_text += f"-{st.session_state.scenario['reduction_poids']}% de poids."
else:
    allegement_text += "Aucun allègement."

st.markdown(f"""
{sobriete_text}

{report_text}

{elec_text}

{remplissage_text}

{allegement_text}
""")

st.divider()

# ==================== GRAPHIQUE CASCADE ====================

st.subheader("🌊 Cascade des leviers")

# Calcul des contributions de chaque levier
from utils.calculations import calculer_bilan_territoire

km_2025_apres_sobriete = resultats['km_2025_apres_sobriete']

# 1. Impact sobriété
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
    'taux_occupation': st.session_state.parc_2025['taux_occupation']
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
    x=["2025", "Sobriété", "Report modal", "Électrification", "Remplissage", "Allègement", "2050"],
    y=[co2_2025, impact_sobriete, impact_report, impact_electrification, impact_remplissage, impact_allegement, co2_2050],
    text=[f"{co2_2025:.0f}", 
          f"{impact_sobriete:+.0f}", 
          f"{impact_report:+.0f}",
          f"{impact_electrification:+.0f}",
          f"{impact_remplissage:+.0f}",
          f"{impact_allegement:+.0f}",
          f"{co2_2050:.0f}"],
    textposition="outside",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "green"}},
    increasing={"marker": {"color": "red"}},
    totals={"marker": {"color": "blue"}}
))

fig_cascade.update_layout(
    title="Contribution de chaque levier (tonnes CO₂/an)",
    yaxis_title="Émissions CO₂ (tonnes)",
    showlegend=False,
    height=500
)

st.plotly_chart(fig_cascade, use_container_width=True)

st.divider()

# ==================== PARTS MODALES ====================

st.subheader("🥧 Évolution des parts modales")

parts_2025 = calculer_parts_modales(st.session_state.km_2025_territoire)
parts_2050 = calculer_parts_modales(resultats['km_2050_territoire'])

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 2025")
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
    
    fig_2025 = px.pie(df_2025, values='Part (%)', names='Mode', hole=0.4)
    fig_2025.update_traces(textposition='inside', textinfo='percent+label')
    fig_2025.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig_2025, use_container_width=True)

with col2:
    st.markdown("##### 2050")
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
    fig_2050.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig_2050, use_container_width=True)

st.divider()

# ==================== DÉTAILS PAR MODE ====================

st.subheader("📋 Détail par mode de transport")

# Créer tableau comparatif
modes_data = []
for mode in ['voiture', 'bus', 'train', 'velo', 'avion', 'marche']:
    mode_label = {'voiture': '🚗 Voiture', 'bus': '🚌 Bus', 'train': '🚆 Train', 
                  'velo': '🚴 Vélo', 'avion': '✈️ Avion', 'marche': '🚶 Marche'}[mode]
    
    km_2025_mode = st.session_state.km_2025_territoire[mode]
    km_2050_mode = resultats['km_2050_territoire'][mode]
    co2_2025_mode = resultats['bilan_2025']['detail_par_mode'][mode]
    co2_2050_mode = resultats['bilan_2050']['detail_par_mode'][mode]
    
    modes_data.append({
        'Mode': mode_label,
        'Km 2025 (Mkm)': f"{km_2025_mode:.1f}",
        'Km 2050 (Mkm)': f"{km_2050_mode:.1f}",
        'Évol km (%)': f"{((km_2050_mode - km_2025_mode)/km_2025_mode*100):+.1f}" if km_2025_mode > 0 else "N/A",
        'CO₂ 2025 (t)': f"{co2_2025_mode:.0f}",
        'CO₂ 2050 (t)': f"{co2_2050_mode:.0f}",
        'Évol CO₂ (%)': f"{((co2_2050_mode - co2_2025_mode)/co2_2025_mode*100):+.1f}" if co2_2025_mode > 0 else "N/A"
    })

df_modes = pd.DataFrame(modes_data)
st.dataframe(df_modes, use_container_width=True, hide_index=True)

st.divider()

# ==================== EXPORT CSV ====================

st.subheader("💾 Exporter les résultats")

# MODIFIÉ : Inclure les nouvelles données de sobriété
data_export = {
    'Indicateur': [
        'Population',
        'CO2 2025 (tonnes)',
        'CO2 2050 (tonnes)',
        'Réduction CO2 (%)',
        'Objectif atteint',
        '',
        'Part VE 2050 (%)',
        'Part bus élec 2050 (%)',
        'Part vélos élec 2050 (%)',
        '',
        'Réduction km voiture (%)',
        'Réduction km avion (%)',
        '',
        'Report voiture→vélo (%)',
        'Report voiture→bus (%)',
        'Report voiture→train (%)',
        'Report avion→train (%)',
        '',
        'Taux remplissage 2050',
        'Réduction poids (%)',
        '',
        'Impact sobriété (t CO2)',
        'Impact report modal (t CO2)',
        'Impact électrification (t CO2)',
        'Impact taux remplissage (t CO2)',
        'Impact allègement (t CO2)'
    ],
    'Valeur': [
        st.session_state.population,
        f"{co2_2025:.0f}",
        f"{co2_2050:.0f}",
        f"{reduction_pct:.1f}",
        'Oui' if objectif_atteint else 'Non',
        '',
        st.session_state.scenario['part_ve'],
        st.session_state.scenario['part_bus_elec'],
        st.session_state.scenario['part_velo_elec'],
        '',
        st.session_state.scenario.get('reduction_km_voiture', 0),
        st.session_state.scenario.get('reduction_km_avion', 0),
        '',
        st.session_state.scenario['report_velo'],
        st.session_state.scenario['report_bus'],
        st.session_state.scenario['report_train'],
        st.session_state.scenario['report_train_avion'],
        '',
        st.session_state.scenario['taux_remplissage'],
        st.session_state.scenario['reduction_poids'],
        '',
        f"{impact_sobriete:.0f}",
        f"{impact_report:.0f}",
        f"{impact_electrification:.0f}",
        f"{impact_remplissage:.0f}",
        f"{impact_allegement:.0f}"
    ]
}

df_export = pd.DataFrame(data_export)
csv = df_export.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Télécharger les résultats (CSV)",
    data=csv,
    file_name="scenario_mobilite_2050.csv",
    mime="text/csv",
    type="primary",
    use_container_width=True
)

st.divider()

# ==================== NAVIGATION ====================

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Modifier le scénario", use_container_width=True):
        st.session_state.scenario_2050_valide = False
        st.switch_page("pages/3_🎯_Scenario_2050.py")

with col3:
    if st.button("🔄 Recommencer", use_container_width=True):
        st.session_state.donnees_2025_validees = False
        st.session_state.bilan_2025_valide = False
        st.session_state.scenario_2050_valide = False
        st.switch_page("pages/1_📝_Donnees_2025.py")
