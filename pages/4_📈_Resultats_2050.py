# pages/4_📈_Resultats_2050.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from utils.calculations import calculer_2050, format_nombre, calculer_parts_modales
from utils.constants import DISTANCE_TERRE_SOLEIL, initialiser_session

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

st.set_page_config(page_title="📈 Résultats 2050", page_icon="📈", layout="wide")

st.title("🚗 Mobilité Pays Basque 2050")
st.header("📈 Résultats du scénario 2050")

# Vérification
if 'scenario' not in st.session_state:
    st.error("❌ Données du scénario manquantes. Veuillez compléter la page '🎯 Scénario 2050'.")
    st.stop()

# ==================== CALCULS ====================

resultats = calculer_2050()
st.session_state.resultats_2050 = resultats  # Stocker pour persistence


# Calculs par habitant
co2_par_hab_2025 = (resultats['bilan_2025']['co2_total_territoire'] ) / st.session_state.population
co2_par_hab_2050 = (resultats['bilan_2050']['co2_total_territoire'] ) / st.session_state.population

km_par_hab_jour_2025 = (resultats['bilan_2025']['km_total_territoire'] * 1e6) / st.session_state.population / 365
km_par_hab_jour_2050 = (resultats['bilan_2050']['km_total_territoire'] * 1e6) / st.session_state.population / 365

km_par_hab_an_2025 = km_par_hab_jour_2025 * 365
km_par_hab_an_2050 = km_par_hab_jour_2050 * 365

# Distances équivalentes Terre-Soleil
nb_terre_soleil_2025 = (resultats['bilan_2025']['km_total_territoire'] * 1e6) / DISTANCE_TERRE_SOLEIL
nb_terre_soleil_2050 = (resultats['bilan_2050']['km_total_territoire'] * 1e6) / DISTANCE_TERRE_SOLEIL

# ==================== RÉSUMÉ DU SCÉNARIO ====================

st.subheader("📋 Résumé du scénario construit")

# Construction du résumé intelligent
resume_lignes = []

# 1. Électrification
elec_changes = []
if st.session_state.scenario['part_ve'] != st.session_state.parc_2025['part_ve']:
    elec_changes.append(f"voitures {st.session_state.scenario['part_ve']}% électriques")
if st.session_state.scenario['part_bus_elec'] != st.session_state.parc_bus_2025['part_elec']:
    elec_changes.append(f"bus {st.session_state.scenario['part_bus_elec']}% électriques")
if st.session_state.scenario['part_velo_elec'] != st.session_state.parc_velo_2025['part_elec']:
    elec_changes.append(f"vélos {st.session_state.scenario['part_velo_elec']}% électriques")

if elec_changes:
    resume_lignes.append(f"**Électrification** : {', '.join(elec_changes)}")
else:
    resume_lignes.append("**Pas d'électrification**")

# 2. Sobriété (MODIFIÉ : séparé voiture/avion)
sobriete_changes = []
if st.session_state.scenario['reduction_km_voiture'] != 0:
    if st.session_state.scenario['reduction_km_voiture'] < 0:
        sobriete_changes.append(f"voiture {abs(st.session_state.scenario['reduction_km_voiture'])}% de réduction")
    else:
        sobriete_changes.append(f"voiture +{st.session_state.scenario['reduction_km_voiture']}% d'augmentation")

if st.session_state.scenario['reduction_km_avion'] != 0:
    if st.session_state.scenario['reduction_km_avion'] < 0:
        sobriete_changes.append(f"avion {abs(st.session_state.scenario['reduction_km_avion'])}% de réduction")
    else:
        sobriete_changes.append(f"avion +{st.session_state.scenario['reduction_km_avion']}% d'augmentation")

if sobriete_changes:
    resume_lignes.append(f"**Sobriété** : {', '.join(sobriete_changes)}")
else:
    resume_lignes.append("**Pas de sobriété**")

# 3. Report modal
report_changes = []
if st.session_state.scenario['report_velo'] > 0:
    report_changes.append(f"{st.session_state.scenario['report_velo']}% voiture→vélo")
if st.session_state.scenario['report_bus'] > 0:
    report_changes.append(f"{st.session_state.scenario['report_bus']}% voiture→bus")
if st.session_state.scenario['report_train'] > 0:
    report_changes.append(f"{st.session_state.scenario['report_train']}% voiture→train")
if st.session_state.scenario['report_train_avion'] > 0:
    report_changes.append(f"{st.session_state.scenario['report_train_avion']}% avion→train")

if report_changes:
    resume_lignes.append(f"**Report modal** : {', '.join(report_changes)}")
else:
    resume_lignes.append("**Pas de report modal**")

# 4. Taux de remplissage
if st.session_state.scenario['taux_remplissage'] != st.session_state.parc_2025['taux_occupation']:
    variation_remplissage = ((st.session_state.scenario['taux_remplissage'] - st.session_state.parc_2025['taux_occupation']) / st.session_state.parc_2025['taux_occupation']) * 100
    resume_lignes.append(f"**Taux de remplissage** : {st.session_state.scenario['taux_remplissage']:.1f} pers/véh ({variation_remplissage:+.0f}%)")
else:
    resume_lignes.append("**Pas d'amélioration du taux de remplissage**")

# 5. Allègement
if st.session_state.scenario['reduction_poids'] > 0:
    resume_lignes.append(f"**Allègement** : réduction de {st.session_state.scenario['reduction_poids']}% du poids des voitures")
else:
    resume_lignes.append("**Pas d'allègement des voitures**")

# Affichage du résumé
#for ligne in resume_lignes:
#    st.markdown(f"• {ligne}")
resume_text = "  \n".join([f"• {ligne}" for ligne in resume_lignes])
st.info(resume_text)

st.divider()

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
    st.caption(f"Par habitant : {format_nombre(co2_par_hab_2050,2)} tonnes/an")

with col2:
    st.metric("📉 Réduction vs 2025", f"{resultats['reduction_pct']:.1f}%")

with col3:
    if resultats['objectif_atteint']:
        st.success("🏆 **Objectif SNBC atteint !**\n\nRéduction ≥ 70% ✅")
    else:
        st.error(f"❌ **Objectif non atteint** : {resultats['reduction_pct']:.1f}% (objectif : -70%)")

st.divider()

# ==================== INDICATEURS PAR HABITANT ====================

st.subheader("👤 Indicateurs par habitant")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 2025")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("CO₂/hab/an", f"{format_nombre(co2_par_hab_2025,2)} tonnes")
    with c2:
        st.metric("Km/hab/jour", f"{format_nombre(km_par_hab_jour_2025, 1)} km")

with col2:
    st.markdown("##### 2050")
    c1, c2 = st.columns(2)
    delta_co2 = co2_par_hab_2050 - co2_par_hab_2025
    delta_km = km_par_hab_jour_2050 - km_par_hab_jour_2025
    with c1:
        st.metric("CO₂/hab/an", f"{format_nombre(co2_par_hab_2050,2)} tonnes", delta=f"{format_nombre(delta_co2,2)} tonnes", delta_color="inverse")
    with c2:
        st.metric("Km/hab/jour", f"{format_nombre(km_par_hab_jour_2050, 1)} km", delta=f"{format_nombre(delta_km, 1)} km", delta_color="inverse")

st.divider()

# ==================== GRAPHIQUES COMPARAISONS ====================

st.subheader("📊 Comparaisons 2025 vs 2050")

tab1, tab2, tab3, tab4 = st.tabs(["CO₂ par mode", "Kilomètres par mode", "Parts modales", "Émissions moyennes"])

with tab1:
    st.markdown("#### Émissions CO₂ par mode (tonnes/an)")
    
    # Calcul par habitant
    emissions_hab_an_2025 = {mode: (co2/st.session_state.population) * 1000 for mode, co2 in resultats['bilan_2025']['detail_par_mode'].items()}
    emissions_hab_an_2050 = {mode: (co2/st.session_state.population) * 1000 for mode, co2 in resultats['bilan_2050']['detail_par_mode'].items()}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 2025")
        df_2025 = pd.DataFrame({
            'Mode': list(resultats['bilan_2025']['detail_par_mode'].keys()),
            'CO₂ (tonnes/an)': list(resultats['bilan_2025']['detail_par_mode'].values())
        })
        fig_co2_2025 = px.bar(df_2025, x='Mode', y='CO₂ (tonnes/an)', color='Mode')
        fig_co2_2025.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_co2_2025, use_container_width=True,key="fig_co2_2025")
        
        for mode, co2 in resultats['bilan_2025']['detail_par_mode'].items():
            st.caption(f"**{mode.capitalize()}** : {format_nombre(co2)} t/an ({format_nombre(emissions_hab_an_2025[mode],1)} kg/hab/an)")
    
    with col2:
        st.markdown("##### 2050")
        df_2050 = pd.DataFrame({
            'Mode': list(resultats['bilan_2050']['detail_par_mode'].keys()),
            'CO₂ (tonnes/an)': list(resultats['bilan_2050']['detail_par_mode'].values())
        })
        fig_co2_2050 = px.bar(df_2050, x='Mode', y='CO₂ (tonnes/an)', color='Mode')
        fig_co2_2050.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_co2_2050, use_container_width=True, key="fig_co2_2050")
        
        for mode, co2 in resultats['bilan_2050']['detail_par_mode'].items():
            delta = co2 - resultats['bilan_2025']['detail_par_mode'][mode]
            st.caption(f"**{mode.capitalize()}** : {format_nombre(co2)} t/an ({format_nombre(emissions_hab_an_2050[mode],1)} kg/hab/an) [{delta:+.0f} t/an]")

with tab2:
    st.markdown("#### Kilomètres parcourus par mode (Mkm/an)")
    
    # Calcul km/hab/an pour chaque mode
    km_hab_2025 = {mode: (km_mkm * 1e6) / st.session_state.population for mode, km_mkm in st.session_state.km_2025_territoire.items()}
    km_hab_2050 = {mode: (km_mkm * 1e6) / st.session_state.population for mode, km_mkm in resultats['km_2050_territoire'].items()}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 2025")
        df_km_2025 = pd.DataFrame({
            'Mode': list(st.session_state.km_2025_territoire.keys()),
            'Km (Mkm/an)': list(st.session_state.km_2025_territoire.values())
        })
        fig_km_2025 = px.bar(df_km_2025, x='Mode', y='Km (Mkm/an)', color='Mode')
        fig_km_2025.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_km_2025, use_container_width=True,key="fig_km_2025")
        
        for mode, km in st.session_state.km_2025_territoire.items():
            st.caption(f"**{mode.capitalize()}** : {format_nombre(km)} Mkm/an ({format_nombre(km_hab_2025[mode])} km/hab/an)")
    
    with col2:
        st.markdown("##### 2050")
        df_km_2050 = pd.DataFrame({
            'Mode': list(resultats['km_2050_territoire'].keys()),
            'Km (Mkm/an)': list(resultats['km_2050_territoire'].values())
        })
        fig_km_2050 = px.bar(df_km_2050, x='Mode', y='Km (Mkm/an)', color='Mode')
        fig_km_2050.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_km_2050, use_container_width=True,key="fig_km_2050")
        
        for mode, km in resultats['km_2050_territoire'].items():
            delta = km - st.session_state.km_2025_territoire[mode]
            st.caption(f"**{mode.capitalize()}** : {format_nombre(km)} Mkm/an ({format_nombre(km_hab_2050[mode])} km/hab/an) [{delta:+.1f} Mkm/an]")

with tab3:
    st.markdown("#### Parts modales (% des km)")
    
    parts_modales_2025 = calculer_parts_modales(st.session_state.km_2025_territoire)
    parts_modales_2050 = calculer_parts_modales(resultats['km_2050_territoire'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 2025")
        df_parts_2025 = pd.DataFrame({
            'Mode': list(parts_modales_2025.keys()),
            'Part (%)': list(parts_modales_2025.values())
        })
        fig_parts_2025 = px.pie(df_parts_2025, values='Part (%)', names='Mode', hole=0.3)
        fig_parts_2025.update_layout(height=400)
        st.plotly_chart(fig_parts_2025, use_container_width=True,key="fig_parts2025")
    
    with col2:
        st.markdown("##### 2050")
        df_parts_2050 = pd.DataFrame({
            'Mode': list(parts_modales_2050.keys()),
            'Part (%)': list(parts_modales_2050.values())
        })
        fig_parts_2050 = px.pie(df_parts_2050, values='Part (%)', names='Mode', hole=0.3)
        fig_parts_2050.update_layout(height=400)
        st.plotly_chart(fig_parts_2050, use_container_width=True,key="figparts2050")
    
    st.markdown("##### Évolution des parts modales")
    for mode in parts_modales_2025:
        delta_part = parts_modales_2050[mode] - parts_modales_2025[mode]
        st.caption(f"**{mode.capitalize()}** : {parts_modales_2025[mode]:.1f}% → {parts_modales_2050[mode]:.1f}% ({delta_part:+.1f} pts)")

with tab4:
    st.markdown("#### Émissions moyennes (gCO₂/km)")
    
    # Calcul des émissions moyennes par km pour chaque mode
    emissions_moyennes_2025 = {}
    emissions_moyennes_2050 = {}
    
    for mode in st.session_state.km_2025_territoire:
        if st.session_state.km_2025_territoire[mode] > 0:
            emissions_moyennes_2025[mode] = (resultats['bilan_2025']['detail_par_mode'][mode] * 1_000_000) / (st.session_state.km_2025_territoire[mode] * 1e6)
        else:
            emissions_moyennes_2025[mode] = 0
        
        if resultats['km_2050_territoire'][mode] > 0:
            emissions_moyennes_2050[mode] = (resultats['bilan_2050']['detail_par_mode'][mode] * 1_000_000) / (resultats['km_2050_territoire'][mode] * 1e6)
        else:
            emissions_moyennes_2050[mode] = 0
    
    df_emissions_moy = pd.DataFrame({
        'Mode': list(emissions_moyennes_2025.keys()),
        '2025 (gCO₂/km)': list(emissions_moyennes_2025.values()),
        '2050 (gCO₂/km)': list(emissions_moyennes_2050.values())
    })
    
    fig_emissions = go.Figure()
    fig_emissions.add_trace(go.Bar(name='2025', x=df_emissions_moy['Mode'], y=df_emissions_moy['2025 (gCO₂/km)']))
    fig_emissions.add_trace(go.Bar(name='2050', x=df_emissions_moy['Mode'], y=df_emissions_moy['2050 (gCO₂/km)']))
    fig_emissions.update_layout(barmode='group', height=400, yaxis_title="gCO₂/km")
    st.plotly_chart(fig_emissions, use_container_width=True,key="emission")
    
    for mode in emissions_moyennes_2025:
        delta = emissions_moyennes_2050[mode] - emissions_moyennes_2025[mode]
        reduction = ((emissions_moyennes_2025[mode] - emissions_moyennes_2050[mode]) / emissions_moyennes_2025[mode] * 100) if emissions_moyennes_2025[mode] > 0 else 0
        st.caption(f"**{mode.capitalize()}** : {emissions_moyennes_2025[mode]:.1f} → {emissions_moyennes_2050[mode]:.1f} gCO₂/km ({delta:+.1f} gCO₂/km, {reduction:.1f}% de réduction)")

st.divider()

# ==================== CONTRIBUTION DES LEVIERS ====================

st.subheader("🎯 Contribution des leviers à la réduction")

# Calcul des contributions (approche séquentielle)

# État initial 2025
co2_2025_base = resultats['bilan_2025']['co2_total_territoire']

# 1️⃣ Après électrification uniquement
from utils.calculations import calculer_bilan_territoire

scenario_elec = st.session_state.scenario.copy()
scenario_elec['reduction_km_voiture'] = 0
scenario_elec['reduction_km_avion'] = 0
scenario_elec['report_velo'] = 0
scenario_elec['report_bus'] = 0
scenario_elec['report_train'] = 0
scenario_elec['report_train_avion'] = 0
scenario_elec['taux_remplissage'] = st.session_state.parc_2025['taux_occupation']
scenario_elec['reduction_poids'] = 0

parc_elec = {
    'part_thermique': st.session_state.scenario['part_thermique'],
    'part_ve': st.session_state.scenario['part_ve'],
    'taux_occupation': st.session_state.parc_2025['taux_occupation']
}

parc_velo_elec = {
    'part_elec': st.session_state.scenario['part_velo_elec'],
    'part_classique': st.session_state.scenario['part_velo_classique']
}

parc_bus_elec = {
    'part_elec': st.session_state.scenario['part_bus_elec'],
    'part_thermique': st.session_state.scenario['part_bus_thermique']
}

bilan_elec = calculer_bilan_territoire(
    st.session_state.km_2025_territoire,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_elec,
    parc_velo_elec,
    parc_bus_elec,
    reduction_poids=0
)

co2_elec = bilan_elec['co2_total_territoire']
contrib_elec_voiture = (co2_2025_base - co2_elec) * (st.session_state.scenario['part_ve'] / 100) if st.session_state.scenario['part_ve'] > st.session_state.parc_2025['part_ve'] else 0
contrib_elec_bus = (co2_2025_base - co2_elec) * (st.session_state.scenario['part_bus_elec'] / 100) if st.session_state.scenario['part_bus_elec'] > st.session_state.parc_bus_2025['part_elec'] else 0
contrib_elec_velo = (co2_2025_base - co2_elec) * (st.session_state.scenario['part_velo_elec'] / 100) if st.session_state.scenario['part_velo_elec'] > st.session_state.parc_velo_2025['part_elec'] else 0
contrib_elec = co2_2025_base - co2_elec

# 2️⃣ Après sobriété (MODIFIÉ : utilise les km après sobriété voiture ET avion)
km_apres_sobriete = resultats['km_2025_apres_sobriete']

bilan_sobriete = calculer_bilan_territoire(
    km_apres_sobriete,
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_elec,
    parc_velo_elec,
    parc_bus_elec,
    reduction_poids=0
)

co2_sobriete = bilan_sobriete['co2_total_territoire']
contrib_sobriete = co2_elec - co2_sobriete

# 3️⃣ Après report modal
bilan_report = calculer_bilan_territoire(
    resultats['km_2050_territoire'],
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_elec,
    parc_velo_elec,
    parc_bus_elec,
    reduction_poids=0
)

co2_report = bilan_report['co2_total_territoire']
contrib_report = co2_sobriete - co2_report

# 4️⃣ Après taux de remplissage
parc_remplissage = parc_elec.copy()
parc_remplissage['taux_occupation'] = st.session_state.scenario['taux_remplissage']

bilan_remplissage = calculer_bilan_territoire(
    resultats['km_2050_territoire'],
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_remplissage,
    parc_velo_elec,
    parc_bus_elec,
    reduction_poids=0
)

co2_remplissage = bilan_remplissage['co2_total_territoire']
contrib_remplissage = co2_report - co2_remplissage

# 5️⃣ Après allègement
bilan_allegement = calculer_bilan_territoire(
    resultats['km_2050_territoire'],
    {**st.session_state.emissions, 'emission_thermique': st.session_state.parc_2025['emission_thermique']},
    parc_remplissage,
    parc_velo_elec,
    parc_bus_elec,
    reduction_poids=st.session_state.scenario['reduction_poids']
)

co2_allegement = bilan_allegement['co2_total_territoire']
contrib_allegement = co2_remplissage - co2_allegement

# Graphique en cascade
if True:  # Toujours afficher
    fig_cascade = go.Figure(go.Waterfall(
        name="Contributions",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["CO₂ 2025", 
           "Électrif. voiture", 
           "Électrif. bus", 
           "Électrif. vélo",
           "Sobriété", 
           "Report modal", 
           "Taux remplissage", 
           "Allègement",
           "CO₂ 2050"],
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
    
    st.plotly_chart(fig_cascade, use_container_width=True,key="fig_cascade")

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
    delta={'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "lightgreen" if resultats['reduction_pct'] >= 70 else "orange"},
        'steps': [
            {'range': [0, 50], 'color': '#fee2e2'},
            {'range': [50, 70], 'color': '#fed7aa'},
            {'range': [70, 100], 'color': '#d1fae5'}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 70}
    },
    title={'text': "Réduction des émissions (%)"}
))
fig_jauge.update_layout(height=300, font={'size': 16})
st.plotly_chart(fig_jauge, use_container_width=True,key="fig_jauge")

st.divider()

# ==================== INTERPRÉTATION ====================

st.subheader("🧩 Interprétation des résultats")

if resultats['objectif_atteint']:
    st.success("""
    ✅ **Félicitations ! Votre scénario atteint l'objectif SNBC (-70%).**  
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

# ==================== EXPORT DES DONNÉES ====================

st.subheader("💾 Export des données")

# Préparer le contenu texte
export_text = f"""==============================================
MOBILITÉ PAYS BASQUE 2050 - EXPORT DONNÉES
Code groupe : {st.session_state.get('code_groupe', 'N/A')}
Population territoire : {format_nombre(st.session_state.population)} habitants
==============================================

--- SITUATION INITIALE (km/an/habitant) ---
Voiture : {st.session_state.km_2025_habitant['voiture']} km/an/hab
Bus : {st.session_state.km_2025_habitant['bus']} km/an/hab
Train : {st.session_state.km_2025_habitant['train']} km/an/hab
Vélo : {st.session_state.km_2025_habitant['velo']} km/an/hab
Avion : {st.session_state.km_2025_habitant['avion']} km/an/hab
Marche : {st.session_state.km_2025_habitant['marche']} km/an/hab

--- BILAN 2025 ---
CO₂ territoire : {format_nombre(resultats['bilan_2025']['co2_total_territoire'])} tonnes/an
CO₂ par habitant : {format_nombre(co2_par_hab_2025, 2)} tonnes/an
Km totaux territoire : {format_nombre(resultats['bilan_2025']['km_total_territoire'])} Mkm/an
Km par habitant : {format_nombre(km_par_hab_an_2025)} km/an

--- SCÉNARIO 2050 - LEVIERS ---
Électrification voitures : {st.session_state.scenario['part_ve']}% VE
Électrification bus : {st.session_state.scenario['part_bus_elec']}% élec
Électrification vélos : {st.session_state.scenario['part_velo_elec']}% élec
Sobriété voiture (variation km) : {st.session_state.scenario['reduction_km_voiture']:+}%
Sobriété avion (variation km) : {st.session_state.scenario['reduction_km_avion']:+}%
Report voiture→vélo : {st.session_state.scenario['report_velo']}%
Report voiture→bus : {st.session_state.scenario['report_bus']}%
Report voiture→train : {st.session_state.scenario['report_train']}%
Report avion→train : {st.session_state.scenario['report_train_avion']}%
Taux remplissage : {st.session_state.scenario['taux_remplissage']:.1f} pers/véh
Réduction poids : {st.session_state.scenario['reduction_poids']}%

--- BILAN 2050 ---
CO₂ territoire : {format_nombre(resultats['bilan_2050']['co2_total_territoire'])} tonnes/an
CO₂ par habitant : {format_nombre(co2_par_hab_2050, 2)} tonnes/an
Km totaux territoire : {format_nombre(resultats['bilan_2050']['km_total_territoire'])} Mkm/an
Km par habitant : {format_nombre(km_par_hab_an_2050)} km/an
Réduction CO₂ : {resultats['reduction_pct']:.1f}%
Objectif SNBC atteint : {"OUI ✓" if resultats['objectif_atteint'] else "NON ✗"}

--- KM PAR MODE (km/an/habitant) ---
                    2025        2050
Voiture :      {km_hab_2025['voiture']:>10.0f}  {km_hab_2050['voiture']:>10.0f}
Bus :          {km_hab_2025['bus']:>10.0f}  {km_hab_2050['bus']:>10.0f}
Train :        {km_hab_2025['train']:>10.0f}  {km_hab_2050['train']:>10.0f}
Vélo :         {km_hab_2025['velo']:>10.0f}  {km_hab_2050['velo']:>10.0f}
Avion :        {km_hab_2025['avion']:>10.0f}  {km_hab_2050['avion']:>10.0f}
Marche :       {km_hab_2025['marche']:>10.0f}  {km_hab_2050['marche']:>10.0f}

--- ÉMISSIONS PAR MODE (kg CO₂/an/habitant) ---
                    2025        2050
Voiture :      {emissions_hab_an_2025['voiture']:>10.1f}  {emissions_hab_an_2050['voiture']:>10.1f}
Bus :          {emissions_hab_an_2025['bus']:>10.1f}  {emissions_hab_an_2050['bus']:>10.1f}
Train :        {emissions_hab_an_2025['train']:>10.1f}  {emissions_hab_an_2050['train']:>10.1f}
Vélo :         {emissions_hab_an_2025['velo']:>10.1f}  {emissions_hab_an_2050['velo']:>10.1f}
Avion :        {emissions_hab_an_2025['avion']:>10.1f}  {emissions_hab_an_2050['avion']:>10.1f}
Marche :       {emissions_hab_an_2025['marche']:>10.1f}  {emissions_hab_an_2050['marche']:>10.1f}

==============================================
"""

col1, col2 = st.columns([2, 1])
with col1:
    st.download_button(
        label="📥 Télécharger toutes les données (TXT)",
        data=export_text,
        file_name=f"mobilite_PB_2050_{st.session_state.get('code_groupe', 'export')}.txt",
        mime="text/plain",
        use_container_width=True
    )

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
