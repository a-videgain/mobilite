# pages/4_📈_Resultats_2050.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from utils.calculations import calculer_2050, format_nombre, calculer_parts_modales
from utils.constants import POPULATION_PB, DISTANCE_TERRE_SOLEIL, initialiser_session

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

# Vérification connexion
if not st.session_state.get('logged_in', False):
    st.error("❌ Veuillez vous connecter")
    st.stop()


st.set_page_config(page_title="📈 Résultats 2050", page_icon="📈", layout="wide")

st.title("🚗 Mobilité Pays Basque 2050")
st.header("📈 Résultats du scénario 2050")

# Vérification
if 'scenario' not in st.session_state:
    st.error("❌ Données du scénario manquantes. Veuillez compléter la page '🎯 Scénario 2050'.")
    st.stop()

# ==================== CALCULS ====================

resultats = calculer_2050()

# Calculs par habitant
co2_par_hab_2025 = (resultats['bilan_2025']['co2_total_territoire'] * 1000) / POPULATION_PB
co2_par_hab_2050 = (resultats['bilan_2050']['co2_total_territoire'] * 1000) / POPULATION_PB

km_par_hab_jour_2025 = (resultats['bilan_2025']['km_total_territoire'] * 1e6) / POPULATION_PB / 365
km_par_hab_jour_2050 = (resultats['bilan_2050']['km_total_territoire'] * 1e6) / POPULATION_PB / 365

km_par_hab_an_2025 = km_par_hab_jour_2025 * 365
km_par_hab_an_2050 = km_par_hab_jour_2050 * 365

# Distances équivalentes Terre-Soleil
nb_terre_soleil_2025 = (resultats['bilan_2025']['km_total_territoire'] * 1e6) / DISTANCE_TERRE_SOLEIL
nb_terre_soleil_2050 = (resultats['bilan_2050']['km_total_territoire'] * 1e6) / DISTANCE_TERRE_SOLEIL

# ==================== MÉTRIQUES PRINCIPALES ====================

col1, col2, col3 = st.columns(3)

with col1:
    delta_co2_territoire = resultats['bilan_2050']['co2_total_territoire'] - resultats['bilan_2025']['co2_total_territoire']
    st.metric(
        "🌍 CO₂ territoire 2050",
        f"{format_nombre(resultats['bilan_2050']['co2_total_territoire'])} tonnes/an",
        delta=f"{format_nombre(delta_co2_territoire)} t/an",
        delta_color="inverse"
    )
    st.caption(f"Par habitant : {format_nombre(co2_par_hab_2050)} kg/an")

with col2:
    st.metric("📉 Réduction vs 2025", f"{resultats['reduction_pct']:.1f}%")

with col3:
    if resultats['objectif_atteint']:
        st.success("🏆 **Objectif SNBC atteint !**\n\nRéduction ≥ 80% ✅")
    else:
        st.error(f"❌ **Objectif non atteint** : {resultats['reduction_pct']:.1f}% (objectif : -80%)")

st.divider()

# ==================== INDICATEURS PAR HABITANT ====================

st.subheader("👤 Indicateurs par habitant")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 2025")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("CO₂/hab/an", f"{format_nombre(co2_par_hab_2025)} kg")
    with c2:
        st.metric("Km/hab/jour", f"{format_nombre(km_par_hab_jour_2025, 1)} km")

with col2:
    st.markdown("##### 2050")
    c1, c2 = st.columns(2)
    delta_co2 = co2_par_hab_2050 - co2_par_hab_2025
    delta_km = km_par_hab_jour_2050 - km_par_hab_jour_2025
    with c1:
        st.metric("CO₂/hab/an", f"{format_nombre(co2_par_hab_2050)} kg", delta=f"{format_nombre(delta_co2)} kg", delta_color="inverse")
    with c2:
        st.metric("Km/hab/jour", f"{format_nombre(km_par_hab_jour_2050, 1)} km", delta=f"{format_nombre(delta_km, 1)} km", delta_color="inverse")

st.divider()

# ==================== PARTS MODALES 2025 VS 2050 ====================

st.subheader("🥧 Parts modales - Comparaison 2025 vs 2050")
st.caption("En km/an/habitant")

# Calcul des km par habitant par mode
km_hab_2025 = {mode: (km_terr * 1e6) / POPULATION_PB for mode, km_terr in st.session_state.km_2025_territoire.items()}
km_hab_2050 = {mode: (km_terr * 1e6) / POPULATION_PB for mode, km_terr in resultats['km_2050_territoire'].items()}

# Mapping des noms et couleurs cohérentes pour l'affichage
mode_mapping = {
    'voiture': '🚗 Voiture',
    'bus': '🚌 Bus',
    'train': '🚆 Train',
    'velo': '🚴 Vélo',
    'avion': '✈️ Avion',
    'marche': '🚶 Marche'
}

# Palette de couleurs cohérente
color_map = {
    '🚗 Voiture': '#ef4444',
    '🚌 Bus': '#f59e0b',
    '🚆 Train': '#10b981',
    '🚴 Vélo': '#06b6d4',
    '✈️ Avion': '#8b5cf6',
    '🚶 Marche': '#6b7280'
}

col1, col2 = st.columns(2)

with col1:
    df_2025 = pd.DataFrame({
        'Mode': [mode_mapping[m] for m in km_hab_2025.keys()],
        'km/an/hab': list(km_hab_2025.values())
    })
    fig_2025 = px.pie(
        df_2025, 
        values='km/an/hab', 
        names='Mode', 
        hole=0.4,
        title="2025",
        color='Mode',
        color_discrete_map=color_map
    )
    fig_2025.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_2025, use_container_width=True)
    st.caption(f"**Total : {format_nombre(sum(km_hab_2025.values()))} km/an/hab**")

with col2:
    df_2050 = pd.DataFrame({
        'Mode': [mode_mapping[m] for m in km_hab_2050.keys()],
        'km/an/hab': list(km_hab_2050.values())
    })
    fig_2050 = px.pie(
        df_2050, 
        values='km/an/hab', 
        names='Mode', 
        hole=0.4,
        title="2050",
        color='Mode',
        color_discrete_map=color_map
    )
    fig_2050.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_2050, use_container_width=True)
    st.caption(f"**Total : {format_nombre(sum(km_hab_2050.values()))} km/an/hab**")

st.divider()

# ==================== ÉMISSIONS PAR MODE 2025 VS 2050 ====================

st.subheader("🌍 Émissions CO₂ par mode - Comparaison 2025 vs 2050")
st.caption("En kg/habitant/an")

# Calcul des émissions par habitant par mode
emissions_hab_an_2025 = {mode: (co2 * 1000) / POPULATION_PB for mode, co2 in resultats['bilan_2025']['detail_par_mode'].items()}
emissions_hab_an_2050 = {mode: (co2 * 1000) / POPULATION_PB for mode, co2 in resultats['bilan_2050']['detail_par_mode'].items()}

# Déterminer le max pour uniformiser l'échelle
max_emissions = max(max(emissions_hab_an_2025.values()), max(emissions_hab_an_2050.values()))
y_max = max_emissions * 1.15  # 15% de marge pour les labels

col1, col2 = st.columns(2)

with col1:
    df_emissions_2025 = pd.DataFrame({
        'Mode': [mode_mapping[m] for m in emissions_hab_an_2025.keys()],
        'CO₂ (kg/hab/an)': list(emissions_hab_an_2025.values())
    })
    df_emissions_2025 = df_emissions_2025.sort_values('CO₂ (kg/hab/an)', ascending=False)
    fig_emissions_2025 = px.bar(
        df_emissions_2025,
        x='Mode',
        y='CO₂ (kg/hab/an)',
        text='CO₂ (kg/hab/an)',
        color='Mode',
        color_discrete_map=color_map,
        title="2025"
    )
    fig_emissions_2025.update_traces(texttemplate='%{text:.0f} kg', textposition='outside')
    fig_emissions_2025.update_layout(showlegend=False, yaxis_range=[0, y_max])
    st.plotly_chart(fig_emissions_2025, use_container_width=True)
    st.caption(f"**Total : {format_nombre(sum(emissions_hab_an_2025.values()))} kg/hab/an**")

with col2:
    df_emissions_2050 = pd.DataFrame({
        'Mode': [mode_mapping[m] for m in emissions_hab_an_2050.keys()],
        'CO₂ (kg/hab/an)': list(emissions_hab_an_2050.values())
    })
    df_emissions_2050 = df_emissions_2050.sort_values('CO₂ (kg/hab/an)', ascending=False)
    fig_emissions_2050 = px.bar(
        df_emissions_2050,
        x='Mode',
        y='CO₂ (kg/hab/an)',
        text='CO₂ (kg/hab/an)',
        color='Mode',
        color_discrete_map=color_map,
        title="2050"
    )
    fig_emissions_2050.update_traces(texttemplate='%{text:.0f} kg', textposition='outside')
    fig_emissions_2050.update_layout(showlegend=False, yaxis_range=[0, y_max])
    st.plotly_chart(fig_emissions_2050, use_container_width=True)
    st.caption(f"**Total : {format_nombre(sum(emissions_hab_an_2050.values()))} kg/hab/an**")

st.divider()

# ==================== GRAPHIQUE EN CASCADE ====================

with st.expander("📊 Analyse avancée : Contribution de chaque levier", expanded=False):
    st.markdown("""
    Ce graphique décompose la réduction totale en montrant la contribution 
    séquentielle de chaque levier (ordre d'application du modèle).
    """)
    
    import plotly.graph_objects as go
    
    # Scénario de référence (aucun levier)
    co2_2025_base = resultats['bilan_2025']['co2_total_territoire']
    
    def calculer_scenario_partiel(modifications):
        """Calcule un scénario avec seulement certains leviers activés"""
        scenario_temp = {
            'reduction_km': 0,
            'report_velo': 0,
            'report_bus': 0,
            'report_train': 0,
            'report_train_avion': 0,
            'taux_remplissage': st.session_state.parc_2025['taux_occupation'],
            'part_ve': st.session_state.parc_2025['part_ve'],
            'part_thermique': st.session_state.parc_2025['part_thermique'],
            'part_velo_elec': st.session_state.parc_velo_2025['part_elec'],
            'part_velo_classique': st.session_state.parc_velo_2025['part_classique'],
            'part_bus_elec': st.session_state.parc_bus_2025['part_elec'],
            'part_bus_thermique': st.session_state.parc_bus_2025['part_thermique'],
            'reduction_poids': 0
        }
        scenario_temp.update(modifications)
        
        # Sauvegarder scénario actuel
        scenario_actuel = st.session_state.scenario.copy()
        st.session_state.scenario = scenario_temp
        resultats_temp = calculer_2050()
        st.session_state.scenario = scenario_actuel
        
        return resultats_temp['bilan_2050']['co2_total_territoire']
    
    # Calcul des contributions
    co2_elec_voiture = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique']
    })
    contrib_elec_voiture = co2_2025_base - co2_elec_voiture
    
    co2_elec_bus = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique'],
        'part_bus_elec': st.session_state.scenario['part_bus_elec'],
        'part_bus_thermique': st.session_state.scenario['part_bus_thermique']
    })
    contrib_elec_bus = co2_elec_voiture - co2_elec_bus
    
    co2_elec_velo = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique'],
        'part_bus_elec': st.session_state.scenario['part_bus_elec'],
        'part_bus_thermique': st.session_state.scenario['part_bus_thermique'],
        'part_velo_elec': st.session_state.scenario['part_velo_elec'],
        'part_velo_classique': st.session_state.scenario['part_velo_classique']
    })
    contrib_elec_velo = co2_elec_bus - co2_elec_velo
    
    co2_sobriete = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique'],
        'part_bus_elec': st.session_state.scenario['part_bus_elec'],
        'part_bus_thermique': st.session_state.scenario['part_bus_thermique'],
        'part_velo_elec': st.session_state.scenario['part_velo_elec'],
        'part_velo_classique': st.session_state.scenario['part_velo_classique'],
        'reduction_km': st.session_state.scenario['reduction_km']
    })
    contrib_sobriete = co2_elec_velo - co2_sobriete
    
    co2_report = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique'],
        'part_bus_elec': st.session_state.scenario['part_bus_elec'],
        'part_bus_thermique': st.session_state.scenario['part_bus_thermique'],
        'part_velo_elec': st.session_state.scenario['part_velo_elec'],
        'part_velo_classique': st.session_state.scenario['part_velo_classique'],
        'reduction_km': st.session_state.scenario['reduction_km'],
        'report_velo': st.session_state.scenario['report_velo'],
        'report_bus': st.session_state.scenario['report_bus'],
        'report_train': st.session_state.scenario['report_train'],
        'report_train_avion': st.session_state.scenario['report_train_avion']
    })
    contrib_report = co2_sobriete - co2_report
    
    co2_remplissage = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique'],
        'part_bus_elec': st.session_state.scenario['part_bus_elec'],
        'part_bus_thermique': st.session_state.scenario['part_bus_thermique'],
        'part_velo_elec': st.session_state.scenario['part_velo_elec'],
        'part_velo_classique': st.session_state.scenario['part_velo_classique'],
        'reduction_km': st.session_state.scenario['reduction_km'],
        'report_velo': st.session_state.scenario['report_velo'],
        'report_bus': st.session_state.scenario['report_bus'],
        'report_train': st.session_state.scenario['report_train'],
        'report_train_avion': st.session_state.scenario['report_train_avion'],
        'taux_remplissage': st.session_state.scenario['taux_remplissage']
    })
    contrib_remplissage = co2_report - co2_remplissage
    
    co2_allegement = calculer_scenario_partiel({
        'part_ve': st.session_state.scenario['part_ve'],
        'part_thermique': st.session_state.scenario['part_thermique'],
        'part_bus_elec': st.session_state.scenario['part_bus_elec'],
        'part_bus_thermique': st.session_state.scenario['part_bus_thermique'],
        'part_velo_elec': st.session_state.scenario['part_velo_elec'],
        'part_velo_classique': st.session_state.scenario['part_velo_classique'],
        'reduction_km': st.session_state.scenario['reduction_km'],
        'report_velo': st.session_state.scenario['report_velo'],
        'report_bus': st.session_state.scenario['report_bus'],
        'report_train': st.session_state.scenario['report_train'],
        'report_train_avion': st.session_state.scenario['report_train_avion'],
        'taux_remplissage': st.session_state.scenario['taux_remplissage'],
        'reduction_poids': st.session_state.scenario['reduction_poids']
    })
    contrib_allegement = co2_remplissage - co2_allegement
    
    # Créer le graphique en cascade
    fig_cascade = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["2025", "Élec. voitures", "Élec. bus", "Élec. vélos", "Sobriété", "Report modal", "Remplissage", "Allègement", "2050"],
        y=[co2_2025_base, 
           -contrib_elec_voiture,
           -contrib_elec_bus,
           -contrib_elec_velo,
           -contrib_sobriete,
           -contrib_report,
           -contrib_remplissage,
           -contrib_allegement,
           co2_allegement],
        text=[f"{co2_2025_base:.0f}",
              f"-{contrib_elec_voiture:.0f}" if contrib_elec_voiture > 0 else f"+{abs(contrib_elec_voiture):.0f}",
              f"-{contrib_elec_bus:.0f}" if contrib_elec_bus > 0 else f"+{abs(contrib_elec_bus):.0f}",
              f"-{contrib_elec_velo:.0f}" if contrib_elec_velo > 0 else f"+{abs(contrib_elec_velo):.0f}",
              f"-{contrib_sobriete:.0f}" if contrib_sobriete > 0 else f"+{abs(contrib_sobriete):.0f}",
              f"-{contrib_report:.0f}" if contrib_report > 0 else f"+{abs(contrib_report):.0f}",
              f"-{contrib_remplissage:.0f}" if contrib_remplissage > 0 else f"+{abs(contrib_remplissage):.0f}",
              f"-{contrib_allegement:.0f}" if contrib_allegement > 0 else f"+{abs(contrib_allegement):.0f}",
              f"{co2_allegement:.0f}"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#10b981"}},
        increasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))
    
    fig_cascade.update_layout(
        title="Contribution de chaque levier (tonnes CO₂/an)",
        showlegend=False,
        height=500,
        yaxis_title="Émissions CO₂ (tonnes/an)"
    )
    
    st.plotly_chart(fig_cascade, use_container_width=True)

st.divider()

# ==================== KILOMÈTRES COMPARAISON ====================

st.subheader("🛣️ Kilomètres parcourus - Comparaison")

col1, col2 = st.columns(2)

with col1:
    st.metric("Km totaux 2025", f"{format_nombre(resultats['bilan_2025']['km_total_territoire'])} Mkm/an")
    st.caption(f"Soit {nb_terre_soleil_2025:.1f} fois la distance Terre-Soleil")
    st.caption(f"Par habitant : {format_nombre(km_par_hab_an_2025)} km/an")

with col2:
    delta_km_total = resultats['bilan_2050']['km_total_territoire'] - resultats['bilan_2025']['km_total_territoire']
    st.metric(
        "Km totaux 2050",
        f"{format_nombre(resultats['bilan_2050']['km_total_territoire'])} Mkm/an",
        delta=f"{format_nombre(delta_km_total)} Mkm/an",
        delta_color="inverse"
    )
    st.caption(f"Soit {nb_terre_soleil_2050:.1f} fois la distance Terre-Soleil")
    st.caption(f"Par habitant : {format_nombre(km_par_hab_an_2050)} km/an")

st.divider()

# ==================== JAUGE OBJECTIF SNBC ====================

st.subheader("🎯 Progression vers l'objectif SNBC")

fig_jauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=resultats['reduction_pct'],
    delta={'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "lightgreen" if resultats['reduction_pct'] >= 80 else "orange"},
        'steps': [
            {'range': [0, 50], 'color': '#fee2e2'},
            {'range': [50, 80], 'color': '#fed7aa'},
            {'range': [80, 100], 'color': '#d1fae5'}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 80}
    },
    title={'text': "Réduction des émissions (%)"}
))
fig_jauge.update_layout(height=300, font={'size': 16})
st.plotly_chart(fig_jauge, use_container_width=True)

st.divider()

# ==================== INTERPRÉTATION ====================

st.subheader("🧩 Interprétation des résultats")

if resultats['objectif_atteint']:
    st.success("""
    ✅ **Félicitations ! Votre scénario atteint l'objectif SNBC (-80%).**  
    Vous pouvez maintenant identifier les leviers les plus efficaces :
    - Quel leviers contribue le plus ?
    - Le scénario est-il réaliste?
    - Quelle sobriété ou quel report modal ont été les plus décisifs ?
    """)
else:
    st.warning("""
    ⚠️ **Objectif non atteint.**  
    Essayez d'ajuster vos leviers : plus de sobriété, électrification accrue,
    ou report modal plus fort vers les modes actifs et collectifs.
    """)

st.divider()
st.divider()

# ==================== NAVIGATION ====================

st.markdown("### 🔁 Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Modifier le scénario", use_container_width=True):
        st.session_state.scenario_2050_valide = False
        st.switch_page("pages/3_🎯_Scenario_2050.py")

with col2:
    if st.button("🏠 Retour accueil", use_container_width=True):
        st.switch_page("Initialisation.py")
