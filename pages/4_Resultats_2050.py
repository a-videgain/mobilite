# pages/4_Resultats_2050.py

import streamlit as st
import plotly.graph_objects as go
from utils.calculations import calculer_2050, format_nombre
from utils.constants import POPULATION_PB, DISTANCE_TERRE_SOLEIL

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
    - Quelle part de l’électrification contribue le plus ?
    - Quelle sobriété ou quel report modal ont été les plus décisifs ?
    """)
else:
    st.warning("""
    ⚠️ **Objectif non atteint.**  
    Essayez d’ajuster vos leviers : plus de sobriété, électrification accrue,
    ou report modal plus fort vers les modes actifs et collectifs.
    """)

st.divider()

# ==================== NAVIGATION ====================

st.markdown("### 🔁 Navigation")
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Revenir au scénario", use_container_width=True):
        st.switch_page("pages/3_Scenario_2050.py")

with col2:
    if st.button("🏁 Revenir à l'accueil", use_container_width=True):
        st.switch_page("app.py")
