# pages/3_🎯_Scenario_2050.py

import streamlit as st
from utils.calculations import format_nombre
from utils.constants import initialiser_session

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

st.set_page_config(page_title="🎯 Scénario 2050", page_icon="🎯", layout="wide")

#st.title("🚗 Mobilité Pays Basque 2050")
st.title("🎯 Construire le scénario 2050")
st.header ("A vous de jouer!")
st.warning("**🎯 Objectif SNBC : Réduire d'environ 70% les émissions du secteur transport d'ici 2050** (par rapport à la situation actuelle)")

st.info("""
**💡 Hypothèses du scénario 2050 :**
- Le mix énergétique français est supposé constant, malgré l'augmentation de production nécessaire à l'électrification
- Seuls l'**électrification** et l'**allègement des voitures** réduisent les émissions par km des voitures
- Le **report modal** transfère des km vers des modes moins émetteurs
- La **sobriété** réduit le nombre total de km parcourus
- Le **taux de remplissage** améliore l’efficacité d’usage des véhicules
- Les scénarios se limitent aux modes de transport suivants: voiture, vélo, train, bus, marche à pied et avion
- La décarbonation de l'aviation fait l'objet d'un autre projet. Le facteur d'émission (CO2/km) de l'avion est supposé constant.
""")

# Vérification
if 'scenario' not in st.session_state:
    st.error("❌ Données manquantes. Veuillez d'abord compléter les étapes précédentes.")
    st.stop()

# ==================== LEVIER 1 : ÉLECTRIFICATION ====================

with st.expander("🔧 **LEVIER 1 : Électrification** - Décarboner les parcs", expanded=False):
    st.markdown("**Objectif :** Remplacer les véhicules thermiques par des électriques")

    st.markdown("##### 🚗 Parc automobile")
    part_ve_temp = st.slider(
        "Part véhicules électriques (%)",
        0, 100, st.session_state.scenario['part_ve'], 5
    )
    st.info(f"Part thermique : **{100 - part_ve_temp}%**")

    st.markdown("##### 🚌 Parc bus")
    part_bus_elec_temp = st.slider(
        "Part bus électriques (%)",
        0, 100, st.session_state.scenario.get('part_bus_elec', 5), 5
    )
    st.info(f"Part bus thermiques : **{100 - part_bus_elec_temp}%**")

    st.markdown("##### 🚴 Parc vélo")
    part_velo_elec_temp = st.slider(
        "Part vélos électriques (%)",
        0, 100, st.session_state.scenario['part_velo_elec'], 5
    )
    st.info(f"Part vélos classiques : **{100 - part_velo_elec_temp}%**")

# ==================== LEVIER 2 : SOBRIÉTÉ ====================

with st.expander("🔧 **LEVIER 2 : Sobriété** - Réduire les km parcourus", expanded=False):
    st.markdown("**Objectif :** Diminuer le besoin de déplacement")

    reduction_km_temp = st.slider(
        "Variation des km totaux par rapport à 2025 (%)",
        -50, 10, st.session_state.scenario['reduction_km'], 5
    )

    km_total_2025 = sum(st.session_state.km_2025_territoire.values())
    km_total_2050_prevision = km_total_2025 * (1 + reduction_km_temp / 100)

    if reduction_km_temp < 0:
        st.success(f"✅ Réduction : {format_nombre(km_total_2025)} Mkm → {format_nombre(km_total_2050_prevision)} Mkm ({abs(reduction_km_temp)}%)")
    elif reduction_km_temp > 0:
        st.warning(f"⚠️ Augmentation : {format_nombre(km_total_2025)} Mkm → {format_nombre(km_total_2050_prevision)} Mkm (+{reduction_km_temp}%)")
    else:
        st.info(f"➡️ Stabilité : {format_nombre(km_total_2025)} Mkm")

# ==================== LEVIER 3 : REPORT MODAL ====================

with st.expander("🔧 **LEVIER 3 : Report modal** - Transférer vers modes décarbonés", expanded=False):
    st.markdown("**Objectif :** Transférer des km vers des modes moins émetteurs")
    st.caption("Valeurs = % des km du mode d'origine transférés (appliqué APRÈS sobriété)")

    st.markdown("##### 🚗 Report depuis la voiture")
    report_velo_temp = st.slider("🚴 Voiture → Vélo (%)", 0, 50, st.session_state.scenario['report_velo'], 1)
    report_bus_temp = st.slider("🚌 Voiture → Bus (%)", 0, 50, st.session_state.scenario['report_bus'], 1)
    report_train_temp = st.slider("🚆 Voiture → Train (%)", 0, 50, st.session_state.scenario['report_train'], 1)

    report_total_voiture = report_velo_temp + report_bus_temp + report_train_temp
    st.info(f"**Report total depuis voiture : {report_total_voiture}%**")

    st.markdown("##### ✈️ Report depuis l'avion")
    report_train_avion_temp = st.slider("🚆 Avion → Train (%)", 0, 100, st.session_state.scenario['report_train_avion'], 1)
    st.info(f"**{report_train_avion_temp}%** des km avion transférés vers le train")

# ==================== LEVIER 4 : TAUX DE REMPLISSAGE ====================

with st.expander("🔧 **LEVIER 4 : Taux de remplissage** - Augmenter l’occupation des véhicules", expanded=False):
    st.markdown("**Objectif :** Plus de personnes par véhicule")
    taux_remplissage_temp = st.slider(
        "Taux d'occupation (pers/véhicule)",
        1.0, 3.0, st.session_state.scenario['taux_remplissage'], 0.1, format="%.1f"
    )

    gain_remplissage = ((taux_remplissage_temp - st.session_state.parc_2025['taux_occupation']) /
                        st.session_state.parc_2025['taux_occupation']) * 100

    if gain_remplissage > 0:
        st.success(f"✅ +{gain_remplissage:.1f}% vs 2025")
    elif gain_remplissage < 0:
        st.warning(f"⚠️ {gain_remplissage:.1f}% vs 2025")
    else:
        st.info("➡️ Identique à 2025")

# ==================== LEVIER 5 : ALLÈGEMENT ====================

with st.expander("🔧 **LEVIER 5 : Allègement** - Réduire le poids des véhicules", expanded=False):
    st.markdown("**Objectif :** Véhicules plus légers, moins consommateurs")
    st.caption("Impact estimé : -10% poids = -7% émissions  CO2 (thermique ET électrique)")

    reduction_poids_temp = st.slider("Réduction poids (%)", 0, 30, st.session_state.scenario['reduction_poids'], 5)

    if reduction_poids_temp > 0:
        reduction_conso = reduction_poids_temp * 0.7
        st.success(f"✅ Réduction consommation : -{reduction_conso:.1f}% (tous véhicules)")
    else:
        st.info("➡️ Pas d'allègement")
# ==================== VALIDATION ET NAVIGATION ====================

st.divider()

if 'scenario_2050_valide' not in st.session_state:
    st.session_state.scenario_2050_valide = False

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🔄 Réinitialiser les leviers", use_container_width=True, type="secondary"):
        st.session_state.scenario = {
            'reduction_km': 0,
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
        st.session_state.scenario_2050_valide = False
        st.rerun()

with col3:
    if st.button("✅ Valider le scénario", type="primary", use_container_width=True):
        st.session_state.scenario.update({
            'part_ve': part_ve_temp,
            'part_thermique': 100 - part_ve_temp,
            'part_bus_elec': part_bus_elec_temp,
            'part_bus_thermique': 100 - part_bus_elec_temp,
            'part_velo_elec': part_velo_elec_temp,
            'part_velo_classique': 100 - part_velo_elec_temp,
            'reduction_km': reduction_km_temp,
            'report_velo': report_velo_temp,
            'report_bus': report_bus_temp,
            'report_train': report_train_temp,
            'report_train_avion': report_train_avion_temp,
            'taux_remplissage': taux_remplissage_temp,
            'reduction_poids': reduction_poids_temp
        })
        st.session_state.scenario_2050_valide = True
        st.rerun()

# Si validé, afficher bouton navigation
if st.session_state.scenario_2050_valide:
    st.success("✅ Scénario validé !")
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("➡️ Voir les résultats 2050", type="primary", use_container_width=True):
            st.switch_page("pages/4_📈_Resultats_2050.py")
