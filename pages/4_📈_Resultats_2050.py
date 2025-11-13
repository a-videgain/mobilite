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

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if objectif_atteint:
        st.success(f"### ✅ Objectif atteint : **{reduction_pct:.1f}%** de réduction")
        st.balloons()
    else:
        st.error(f"### ❌ Objectif non atteint : **{reduction_pct:.1f}%** de réduction")
        st.warning(f"Il manque **{70 - reduction_pct:.1f} points** pour atteindre l'objectif")

st.divider()

# ==================== MÉTRIQUES PRINCIPALES ====================

st.subheader("📊 Bilan comparatif")

col1, col2, col3 = st.columns(3)

co2_2025 = resultats['bilan_2025']['co2_total_territoire']
co2_2050 = resultats['bilan_2050']['co2_total_territoire']
km_2025 = resultats['bilan_2025']['km_total_territoire']
km_2050 = resultats['bilan_2050']['km_total_territoire']

with col1:
    st.metric(
        "CO₂ total (t/an)",
        f"{format_nombre(co2_2050)}",
        f"{format_nombre(co2_2050 - co2_2025)}",
        delta_color="inverse"
    )
    st.caption("2025 : " + format_nombre(co2_2025) + " t")

with col2:
    st.metric(
        "Km totaux (Mkm/an)",
        f"{format_nombre(km_2050)}",
        f"{format_nombre(km_2050 - km_2025)}",
        delta_color="inverse"
    )
    st.caption("2025 : " + format_nombre(km_2025) + " Mkm")

with col3:
    co2_hab_2025 = co2_2025 / st.session_state.population
    co2_hab_2050 = co2_2050 / st.session_state.population
    st.metric(
        "CO₂/hab (t/an)",
        f"{co2_hab_2050:.2f}",
        f"{co2_hab_2050 - co2_hab_2025:.2f}",
        delta_color="inverse"
    )
    st.caption(f"2025 : {co2_hab_2025:.2f} t")

st.divider()

# ==================== RÉSUMÉ DU SCÉNARIO ====================

st.subheader("📝 Résumé de votre scénario")

resume_lignes = []

# MODIFIÉ - Sobriété voiture et avion séparées
reduction_voiture = st.session_state.scenario.get('reduction_km_voiture', 0)
reduction_avion = st.session_state.scenario.get('reduction_km_avion', 0)

if reduction_voiture != 0 or reduction_avion != 0:
    sobriete_parts = []
    
    if reduction_voiture < 0:
        sobriete_parts.append(f"voiture {abs(reduction_voiture)}% (réduction)")
    elif reduction_voiture > 0:
        sobriete_parts.append(f"voiture +{reduction_voiture}% (augmentation)")
    
    if reduction_avion < 0:
        sobriete_parts.append(f"avion {abs(reduction_avion)}% (réduction)")
    elif reduction_avion > 0:
        sobriete_parts.append(f"avion +{reduction_avion}% (augmentation)")
    
    if sobriete_parts:
        resume_lignes.append(f"**Sobriété** : {', '.join(sobriete_parts)}")
else:
    resume_lignes.append("**Pas de sobriété**")

# Report modal
report_parts = []
if st.session_state.scenario['report_velo'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_velo']}% des km voiture transférés vers le vélo")
if st.session_state.scenario['report_bus'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_bus']}% vers le bus")
if st.session_state.scenario['report_train'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_train']}% vers le train")
if st.session_state.scenario['report_train_avion'] > 0:
    report_parts.append(f"{st.session_state.scenario['report_train_avion']}% des km avion transférés vers le train")

if report_parts:
    resume_lignes.append("**Report modal** : " + ", ".join(report_parts))
else:
    resume_lignes.append("**Pas de report modal**")

# Électrification
elec_parts = []
if st.session_state.scenario['part_ve'] != st.session_state.parc_2025['part_ve']:
    elec_parts.append(f"voitures électriques : {st.session_state.scenario['part_ve']}%")
if st.session_state.scenario['part_bus_elec'] != st.session_state.parc_bus_2025['part_elec']:
    elec_parts.append(f"bus électriques : {st.session_state.scenario['part_bus_elec']}%")
if st.session_state.scenario['part_velo_elec'] != st.session_state.parc_velo_2025['part_elec']:
    elec_parts.append(f"vélos électriques : {st.session_state.scenario['part_velo_elec']}%")

if elec_parts:
    resume_lignes.append("**Électrification** : " + ", ".join(elec_parts))
else:
    resume_lignes.append("**Pas de changement dans l'électrification**")

# Taux de remplissage
if st.session_state.scenario['taux_remplissage'] != st.session_state.parc_2025['taux_occupation']:
    diff_pct = ((st.session_state.scenario['taux_remplissage'] - st.session_state.parc_2025['taux_occupation']) / 
                st.session_state.parc_2025['taux_occupation'] * 100)
    resume_lignes.append(f"**Taux de remplissage** : {st.session_state.scenario['taux_remplissage']:.1f} personnes/véhicule ({diff_pct:+.0f}%)")
else:
    resume_lignes.append("**Pas de changement du taux de remplissage**")

# Allègement
if st.session_state.scenario['reduction_poids'] > 0:
    resume_lignes.append(f"**Allègement** : réduction de {st.session_state.scenario['reduction_poids']}% du poids des véhicules")
else:
    resume_lignes.append("**Pas d'allègement des véhicules**")

for ligne in resume_lignes:
    st.markdown(ligne)

st.divider()

# ==================== GRAPHIQUE CASCADE ====================

st.subheader("🌊 Cascade des leviers d'action")

st.caption("Ce graphique montre comment chaque levier contribue à réduire (ou augmenter) les émissions de CO₂")

# Calcul détaillé des contributions
from utils.calculations import calculer_bilan_territoire

# Point de départ : 2025
co2_initial = co2_2025

# 1️⃣ Après sobriété
km_2025_apres_sobriete = resultats['km_2025_apres_sobriete']
bilan_apres_sobriete = calculer_bilan_territoire(
    km_2025_apres_sobriete,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    st.session_state.parc_2025,
    st.session_state.parc_velo_2025,
    st.session_state.parc_bus_2025,
    reduction_poids=0
)
co2_apres_sobriete = bilan_apres_sobriete['co2_total_territoire']
impact_sobriete = co2_apres_sobriete - co2_initial

# 2️⃣ Après report modal
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
co2_apres_report = bilan_apres_report['co2_total_territoire']
impact_report = co2_apres_report - co2_apres_sobriete

# 3️⃣ Après électrification
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
co2_apres_elec = bilan_apres_elec['co2_total_territoire']
impact_electrification = co2_apres_elec - co2_apres_report

# 4️⃣ Après taux de remplissage
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
co2_apres_remplissage = bilan_apres_remplissage['co2_total_territoire']
impact_remplissage = co2_apres_remplissage - co2_apres_elec

# 5️⃣ Après allègement (final)
impact_allegement = co2_2050 - co2_apres_remplissage

# Création du graphique cascade
fig = go.Figure(go.Waterfall(
    name="Émissions CO₂",
    orientation="v",
    measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
    x=["2025<br>Référence", "Sobriété", "Report<br>modal", "Électrification", "Taux<br>remplissage", "Allègement", "2050<br>Final"],
    y=[co2_initial, impact_sobriete, impact_report, impact_electrification, impact_remplissage, impact_allegement, co2_2050],
    text=[
        f"{co2_initial:,.0f} t".replace(',', ' '),
        f"{impact_sobriete:+,.0f} t".replace(',', ' '),
        f"{impact_report:+,.0f} t".replace(',', ' '),
        f"{impact_electrification:+,.0f} t".replace(',', ' '),
        f"{impact_remplissage:+,.0f} t".replace(',', ' '),
        f"{impact_allegement:+,.0f} t".replace(',', ' '),
        f"{co2_2050:,.0f} t".replace(',', ' ')
    ],
    textposition="outside",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#2ecc71"}},  # Vert pour réduction
    increasing={"marker": {"color": "#e74c3c"}},  # Rouge pour augmentation
    totals={"marker": {"color": "#3498db"}}       # Bleu pour totaux
))

fig.update_layout(
    title="",
    yaxis_title="Émissions CO₂ (tonnes/an)",
    showlegend=False,
    height=500,
    margin=dict(t=50, b=100)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================== CONTRIBUTION DES LEVIERS ====================

st.subheader("🔍 Contribution des leviers d'action")

# Fonction pour calculer un scénario partiel
def calculer_scenario_partiel(scenario_partiel):
    from utils.calculations import calculer_bilan_territoire
    
    # MODIFIÉ - Ajout reduction_km_voiture et reduction_km_avion
    scenario_complet = {
        'reduction_km_voiture': 0,
        'reduction_km_avion': 0,
        'report_velo': 0,
        'report_bus': 0,
        'report_train': 0,
        'report_train_avion': 0,
        'taux_remplissage': st.session_state.parc_2025['taux_occupation'],
        'part_ve': st.session_state.parc_2025['part_ve'],
        'part_thermique': 100 - st.session_state.parc_2025['part_ve'],
        'part_velo_elec': st.session_state.parc_velo_2025['part_elec'],
        'part_velo_classique': st.session_state.parc_velo_2025['part_classique'],
        'part_bus_elec': st.session_state.parc_bus_2025['part_elec'],
        'part_bus_thermique': st.session_state.parc_bus_2025['part_thermique'],
        'reduction_poids': 0
    }
    scenario_complet.update(scenario_partiel)
    
    # MODIFIÉ - Sobriété séparée par mode
    km_apres_sobriete = {}
    for mode, km in st.session_state.km_2025_territoire.items():
        if mode == 'voiture':
            facteur = (1 + scenario_complet['reduction_km_voiture'] / 100)
            km_apres_sobriete[mode] = km * facteur
        elif mode == 'avion':
            facteur = (1 + scenario_complet['reduction_km_avion'] / 100)
            km_apres_sobriete[mode] = km * facteur
        else:
            km_apres_sobriete[mode] = km
    
    km_voiture = km_apres_sobriete['voiture']
    km_avion = km_apres_sobriete['avion']
    
    km_transferes_velo = km_voiture * scenario_complet['report_velo'] / 100
    km_transferes_bus = km_voiture * scenario_complet['report_bus'] / 100
    km_transferes_train_voiture = km_voiture * scenario_complet['report_train'] / 100
    km_transferes_train_avion = km_avion * scenario_complet['report_train_avion'] / 100
    
    km_final = {
        'voiture': max(0, km_voiture - km_transferes_velo - km_transferes_bus - km_transferes_train_voiture),
        'bus': km_apres_sobriete['bus'] + km_transferes_bus,
        'train': km_apres_sobriete['train'] + km_transferes_train_voiture + km_transferes_train_avion,
        'velo': km_apres_sobriete['velo'] + km_transferes_velo,
        'avion': max(0, km_avion - km_transferes_train_avion),
        'marche': km_apres_sobriete['marche']
    }
    
    parc = {
        'part_thermique': scenario_complet['part_thermique'],
        'part_ve': scenario_complet['part_ve'],
        'taux_occupation': scenario_complet['taux_remplissage']
    }
    
    parc_velo = {
        'part_elec': scenario_complet['part_velo_elec'],
        'part_classique': scenario_complet['part_velo_classique']
    }
    
    parc_bus = {
        'part_elec': scenario_complet['part_bus_elec'],
        'part_thermique': scenario_complet['part_bus_thermique']
    }
    
    emissions = st.session_state.emissions.copy()
    emissions['emission_thermique'] = st.session_state.parc_2025['emission_thermique']
    
    bilan = calculer_bilan_territoire(km_final, emissions, parc, parc_velo, parc_bus, 
                                      reduction_poids=scenario_complet['reduction_poids'])
    
    return bilan['co2_total_territoire']

# Calculs des contributions individuelles

# Sobriété seule (MODIFIÉ)
co2_sobriete = calculer_scenario_partiel({
    'reduction_km_voiture': st.session_state.scenario.get('reduction_km_voiture', 0),
    'reduction_km_avion': st.session_state.scenario.get('reduction_km_avion', 0)
})
gain_sobriete = ((co2_2025 - co2_sobriete) / co2_2025) * 100

# Sobriété + Report modal (MODIFIÉ)
co2_sobriete_report = calculer_scenario_partiel({
    'reduction_km_voiture': st.session_state.scenario.get('reduction_km_voiture', 0),
    'reduction_km_avion': st.session_state.scenario.get('reduction_km_avion', 0),
    'report_velo': st.session_state.scenario['report_velo'],
    'report_bus': st.session_state.scenario['report_bus'],
    'report_train': st.session_state.scenario['report_train'],
    'report_train_avion': st.session_state.scenario['report_train_avion']
})
gain_report = ((co2_sobriete - co2_sobriete_report) / co2_2025) * 100

# Sobriété + Report + Électrification (MODIFIÉ)
co2_sobriete_report_elec = calculer_scenario_partiel({
    'reduction_km_voiture': st.session_state.scenario.get('reduction_km_voiture', 0),
    'reduction_km_avion': st.session_state.scenario.get('reduction_km_avion', 0),
    'report_velo': st.session_state.scenario['report_velo'],
    'report_bus': st.session_state.scenario['report_bus'],
    'report_train': st.session_state.scenario['report_train'],
    'report_train_avion': st.session_state.scenario['report_train_avion'],
    'part_ve': st.session_state.scenario['part_ve'],
    'part_thermique': st.session_state.scenario['part_thermique'],
    'part_velo_elec': st.session_state.scenario['part_velo_elec'],
    'part_velo_classique': st.session_state.scenario['part_velo_classique'],
    'part_bus_elec': st.session_state.scenario['part_bus_elec'],
    'part_bus_thermique': st.session_state.scenario['part_bus_thermique']
})
gain_electrification = ((co2_sobriete_report - co2_sobriete_report_elec) / co2_2025) * 100

# Sobriété + Report + Électrification + Taux remplissage (MODIFIÉ)
co2_sobriete_report_elec_remplissage = calculer_scenario_partiel({
    'reduction_km_voiture': st.session_state.scenario.get('reduction_km_voiture', 0),
    'reduction_km_avion': st.session_state.scenario.get('reduction_km_avion', 0),
    'report_velo': st.session_state.scenario['report_velo'],
    'report_bus': st.session_state.scenario['report_bus'],
    'report_train': st.session_state.scenario['report_train'],
    'report_train_avion': st.session_state.scenario['report_train_avion'],
    'part_ve': st.session_state.scenario['part_ve'],
    'part_thermique': st.session_state.scenario['part_thermique'],
    'part_velo_elec': st.session_state.scenario['part_velo_elec'],
    'part_velo_classique': st.session_state.scenario['part_velo_classique'],
    'part_bus_elec': st.session_state.scenario['part_bus_elec'],
    'part_bus_thermique': st.session_state.scenario['part_bus_thermique'],
    'taux_remplissage': st.session_state.scenario['taux_remplissage']
})
gain_remplissage = ((co2_sobriete_report_elec - co2_sobriete_report_elec_remplissage) / co2_2025) * 100

# Allègement (différence finale)
gain_allegement = ((co2_sobriete_report_elec_remplissage - co2_2050) / co2_2025) * 100

# Affichage des contributions
col1, col2 = st.columns(2)

with col1:
    st.metric("💨 Sobriété", f"{gain_sobriete:+.1f}%", help="Réduction des km parcourus")
    st.metric("🚆 Report modal", f"{gain_report:+.1f}%", help="Transfert vers modes décarbonés")
    st.metric("🔋 Électrification", f"{gain_electrification:+.1f}%", help="Remplacement thermique → électrique")

with col2:
    st.metric("👥 Taux remplissage", f"{gain_remplissage:+.1f}%", help="Plus de personnes par véhicule")
    st.metric("⚖️ Allègement", f"{gain_allegement:+.1f}%", help="Réduction du poids des véhicules")
    
    # Vérification
    total_gains = gain_sobriete + gain_report + gain_electrification + gain_remplissage + gain_allegement
    st.metric("🎯 Total", f"{total_gains:.1f}%", help="Somme des contributions")

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

# MODIFIÉ - Inclure les nouvelles données de sobriété
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
        'Gain sobriété (%)',
        'Gain report modal (%)',
        'Gain électrification (%)',
        'Gain taux remplissage (%)',
        'Gain allègement (%)'
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
        f"{gain_sobriete:.1f}",
        f"{gain_report:.1f}",
        f"{gain_electrification:.1f}",
        f"{gain_remplissage:.1f}",
        f"{gain_allegement:.1f}"
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
