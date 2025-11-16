import streamlit as st
from utils.constants import calculer_km_territoire, initialiser_session

    
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
    
st.title("🚗 Décarboner les mobilités au Pays Basque \n **Quelle est la situation de départ** ? ")
st.header("📝 Étape 1 : Saisie des données 2025")


# NOUVEAU BLOC - Sources pour les étudiants
with st.expander("📚 **Sources de données - À lire attentivement**", expanded=False):
    st.markdown("""

    ### La Communauté d'Agglomération Pays Basque (CAPB)
    Ce travail se concentre sur les habitant.e.s de la Communauté d'Agglomération Pays Basque.
    Pour les données de population, consultez la [fiche INSEE CAPB](https://www.insee.fr/fr/statistiques/2011101?geo=EPCI-200067106).
    
    
    ### Mobilité du quotidien (courtes distances)
    
    Selon l'Enquête Mobilité des Personnes (EMP) française de 2019 et l'Enquête Ménages et Déplacements (EMD) de 2010,
    il est estimé que les habitant.e.s de la Communauté d'Agglomération Pays Basque effectuent en moyenne **1,1 déplacements quotidiens 
    en voiture** sur une distance moyenne de **23,3 km par trajet**.
    L'usage des **transports en commun urbains** (bus, trambus) représente **0,2 déplacements par jour** avec une distance moyenne par trajet de **4,5 km**. Il est le plus élevé pour les déplacements entre le domicile et le lieu de scolarité (école, université).
    La **marche à pied** reste le mode le plus fréquent avec **1,4 déplacements quotidiens** sur des distances très courtes de **390 mètres en moyenne**. 
    Le **vélo** est utilisé pour **0,7 déplacements par jour** sur environ **1,57 km par trajet** en moyenne.
    
    Sources : CEREMA, Enquête Mobilité des Personnes 2019 ; INSEE, données mobilité Nouvelle-Aquitaine 2022, 
    Enquêtes Ménages et Déplacements (EMD)  basco-landaise 2010 [EDM2009](https://www.calameo.com/books/000191469aa6d36f2cc24)
    Déplacements domicile-travail (comparateur national)** — Agence AGAM    👉 [Outil en ligne](https://spot.agam.org/tb/mobilites)

    ---
    
    ### ✈️ Mobilité longue distance (train, avion)
    
    Pour les **déplacements ferroviaires**, les habitants des territoires côtiers du Pays Basque effectuent 
    en moyenne **54,75 trajets en train par an**, principalement sur les liaisons Hendaye-Bayonne et vers Bordeaux, 
    avec une distance moyenne de **11 km par trajet** pour les déplacements régionaux. Concernant le **transport aérien**, 
    les données de l'aéroport Biarritz-Pays-Basque indiquent une fréquentation moyenne de **5,11 vols par habitant et par an** 
    (incluant allers et retours), avec une distance moyenne de **503 km par vol** (destinations principales : Paris, 
    capitales européennes).
    
    *Sources : 
    
    ---
    
    ### 🚗 État du parc de véhicules (2025)
    
    Au 1er janvier 2025, le parc automobile du territoire compte **3% de véhicules 100% électriques** et **97% de véhicules 
    thermiques** (par hypothèse, les véhicules hybrides sont considérés ici comme des véhicules thermiques), selon les données du fichier national des immatriculations. Le **taux d'occupation 
    moyen des voitures particulières** est de **1,1 personne par véhicule** pour les déplacements quotidiens. 
    La part de temps passé à l'arrêt par voiture (stationnement) peut être calculé à partir de la distance totale parcourue par une voiture et une estimation de vitesse moyenne . 
    
    Pour les **transports collectifs urbains**, la flotte de bus TXIK TXAK compte **43% de bus électriques**.
    
    Concernant les **vélos**, les ventes récentes montrent que **15% du parc est constitué de vélos à assistance électrique (VAE)** 
    et **85% de vélos classiques**. 
    
    *Sources : ADEME Base Carbone v13.0 (2024) ; AAA Data (immatriculations) ; GART, Observatoire des transports 2024 ; 
    Union Sport & Cycle*
    - **Voitures particulières immatriculées par commune et par type de recharge** — Agence ORE    👉 [Jeu de données](https://www.data.gouv.fr/fr/datasets/voitures-particulieres-immatriculees-par-commune-et-par-type-de-recharge-jeu-de-donnees-aaadata/#/resources)
    - **Part des bus électriques TXIK TXAK** [Electrification bus CAPB](https://www.communaute-paysbasque.fr/actualites/toutes-les-actualites/actualite/le-trambus-colonne-vertebrale-du-reseau-txik-txak-transforme-la-ville-et-arrive-a-bassussarry-en-2026)


    ---
    
    ⚠️ **Consignes :** Utilisez ces informations pour remplir les champs ci-dessous. Certaines données nécessitent 
    des calculs simples (par exemple : déplacements/jour × distance/déplacement × 365 jours = km/an).

    ---
    ###  Les facteurs d'émissions
    
    Les émissions sont considérées par km, sur l'ensemble du cycle de vie (ACV) de chaque mode.
    Il est recommandé d'utiliser les valeurs de références de l'Agence de l'environnement et de la maîtrise de l'énergie (ADEME) pour les émissions pour chaque mode: [Impact CO2 ADEME](https://impactco2.fr/outils/transport).
    Attention aux unités. Les données doivent ici être entrées en gCO₂/km.
    Par hypothèse, seuls les principaux modes de transport sont considérés: marche, vélo, bus, train, avion, voiture.
    
    """)



st.info("Cette étape consiste à établir le bilan mobilités du Pays Basque")
# Population
st.subheader("👥 Population de la Communauté d'Agglomération Pays Basque")
st.session_state.population = st.number_input(
    "Nombre d'habitant.e.s (arrondi au millier)", 100000, 500000,
    st.session_state.get('population', 350000), 10000
)

st.divider()

# Mobilités par habitant
st.subheader("🛣️ Mobilités d'un.e habitant.e moyen du Pays Basque")
st.caption("Entrez les distances parcourues PAR HABITANT.E et PAR AN")

header_cols = st.columns([2, 2, 2])
with header_cols[0]:
    st.markdown("**Mode**")
with header_cols[1]:
    st.markdown("**km/an/habitant**")
with header_cols[2]:
    st.markdown("**Déplacements/an/habitant**")

# Voiture
cols = st.columns([2, 2, 2])
with cols[0]:
    st.markdown("🚗 Voiture")
with cols[1]:
    st.session_state.km_2025_habitant['voiture'] = st.number_input(
        "km_v", 0, 20000, st.session_state.km_2025_habitant['voiture'], 100,
        label_visibility="collapsed"
    )
with cols[2]:
    st.session_state.nb_depl_hab['voiture'] = st.number_input(
        "nb_v", 0.0, 2000.0, st.session_state.nb_depl_hab['voiture'], 10.0,
        format="%.1f", label_visibility="collapsed"
    )

# Bus
cols = st.columns([2, 2, 2])
with cols[0]:
    st.markdown("🚌 Bus / TC")
with cols[1]:
    st.session_state.km_2025_habitant['bus'] = st.number_input(
        "km_b", 0, 5000, st.session_state.km_2025_habitant['bus'], 50,
        label_visibility="collapsed"
    )
with cols[2]:
    st.session_state.nb_depl_hab['bus'] = st.number_input(
        "nb_b", 0.0, 1000.0, st.session_state.nb_depl_hab['bus'], 10.0,
        format="%.1f", label_visibility="collapsed"
    )

# Train
cols = st.columns([2, 2, 2])
with cols[0]:
    st.markdown("🚆 Train")
with cols[1]:
    st.session_state.km_2025_habitant['train'] = st.number_input(
        "km_t", 0, 3000, st.session_state.km_2025_habitant['train'], 50,
        label_visibility="collapsed"
    )
with cols[2]:
    st.session_state.nb_depl_hab['train'] = st.number_input(
        "nb_t", 0.0, 500.0, st.session_state.nb_depl_hab['train'], 5.0,
        format="%.1f", label_visibility="collapsed"
    )

# Vélo
cols = st.columns([2, 2, 2])
with cols[0]:
    st.markdown("🚴 Vélo")
with cols[1]:
    st.session_state.km_2025_habitant['velo'] = st.number_input(
        "km_ve", 0, 3000, st.session_state.km_2025_habitant['velo'], 50,
        label_visibility="collapsed"
    )
with cols[2]:
    st.session_state.nb_depl_hab['velo'] = st.number_input(
        "nb_ve", 0.0, 1000.0, st.session_state.nb_depl_hab['velo'], 10.0,
        format="%.1f", label_visibility="collapsed"
    )

# Avion
cols = st.columns([2, 2, 2])
with cols[0]:
    st.markdown("✈️ Avion")
with cols[1]:
    st.session_state.km_2025_habitant['avion'] = st.number_input(
        "km_a", 0, 10000, st.session_state.km_2025_habitant['avion'], 100,
        label_visibility="collapsed"
    )
with cols[2]:
    st.session_state.nb_depl_hab['avion'] = st.number_input(
        "nb_a", 0.0, 100.0, st.session_state.nb_depl_hab['avion'], 1.0,
        format="%.1f", label_visibility="collapsed"
    )

# Marche
cols = st.columns([2, 2, 2])
with cols[0]:
    st.markdown("🚶 Marche")
with cols[1]:
    st.session_state.km_2025_habitant['marche'] = st.number_input(
        "km_m", 0, 1000, st.session_state.km_2025_habitant['marche'], 50,
        label_visibility="collapsed"
    )
with cols[2]:
    st.session_state.nb_depl_hab['marche'] = st.number_input(
        "nb_m", 0.0, 2000.0, st.session_state.nb_depl_hab['marche'], 10.0,
        format="%.1f", label_visibility="collapsed"
    )

calculer_km_territoire()
km_total_hab = sum(st.session_state.km_2025_habitant.values())
st.info(f"📊 **Total par habitant : {km_total_hab:,.0f} km/an**".replace(',', ' '))

st.divider()

# Parc automobile
st.subheader("🚗 Caractéristiques du parc automobile 2025: voitures immatriculées dans la CAPB")
col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.parc_2025['part_ve'] = st.number_input(
        "Part véhicules électriques (%)", 0, 100,
        st.session_state.parc_2025['part_ve'], 1
    )
    st.session_state.parc_2025['part_thermique'] = 100 - st.session_state.parc_2025['part_ve']
    st.caption(f"Part thermique : {st.session_state.parc_2025['part_thermique']}%")

with col2:
    st.session_state.parc_2025['emission_thermique'] = st.number_input(
        "Émission voiture thermique (gCO₂/km ACV)", 0, 500,
        st.session_state.parc_2025['emission_thermique'], 10
    )
    st.session_state.emissions['voiture_electrique'] = st.number_input(
        "Émission voiture électrique (gCO₂/km ACV)", 0, 200,
        st.session_state.emissions['voiture_electrique'], 5
    )

with col3:
    st.session_state.parc_2025['taux_occupation'] = st.number_input(
        "Taux d'occupation moyen (pers/véh)", 1.0, 4.0,
        st.session_state.parc_2025['taux_occupation'], 0.1, format="%.1f"
    )
    st.session_state.parc_2025['temps_stationnement'] = st.number_input(
        "Temps stationné (%): part du temps total où une voiture n'est pas utilisée", 80, 99,
        st.session_state.parc_2025['temps_stationnement'], 1
    )

st.divider()

# Parc vélo
st.subheader("🚴 Caractéristiques parc vélo 2025")
col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.parc_velo_2025['part_elec'] = st.number_input(
        "Part vélos électriques (%)", 0, 100,
        st.session_state.parc_velo_2025['part_elec'], 1
    )
    st.session_state.parc_velo_2025['part_classique'] = 100 - st.session_state.parc_velo_2025['part_elec']
    st.caption(f"Part vélos classiques : {st.session_state.parc_velo_2025['part_classique']}%")

with col2:
    st.session_state.emissions['velo_elec'] = st.number_input(
        "Émission vélo électrique (gCO₂/km ACV)", 0, 50,
        st.session_state.emissions['velo_elec'], 1
    )

with col3:
    st.session_state.emissions['velo_classique'] = st.number_input(
        "Émission vélo classique (gCO₂/km ACV)", 0, 20,
        st.session_state.emissions['velo_classique'], 1
    )

st.divider()

# Parc bus
st.subheader("🚌 Caractéristiques parc bus 2025")
col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.parc_bus_2025['part_elec'] = st.number_input(
        "Part bus électriques (%)", 0, 100,
        st.session_state.parc_bus_2025['part_elec'], 1
    )
    st.session_state.parc_bus_2025['part_thermique'] = 100 - st.session_state.parc_bus_2025['part_elec']
    st.caption(f"Part bus thermiques : {st.session_state.parc_bus_2025['part_thermique']}%")

with col2:
    st.session_state.emissions['bus_thermique'] = st.number_input(
        "Émission bus thermique (gCO₂/km/passager ACV)", 0, 300,
        st.session_state.emissions['bus_thermique'], 1
    )

with col3:
    st.session_state.emissions['bus_electrique'] = st.number_input(
        "Émission bus électrique (gCO₂/km/passage ACV)", 0, 100,
        st.session_state.emissions['bus_electrique'], 1
    )

st.divider()

# Autres modes
with st.expander("⚙️ Facteurs d'émission autres modes (gCO₂/km ACV)"):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.emissions['train'] = st.number_input(
            "Train (gCO₂/km/passager)", 0.0, 50.0, st.session_state.emissions['train'], 0.5
        )
        st.session_state.emissions['avion'] = st.number_input(
            "Avion (gCO₂/km/passager)", 0, 500, st.session_state.emissions['avion'], 10
        )
    with col2:
        st.session_state.emissions['marche'] = st.number_input(
            "Marche (gCO₂/km)", 0, 10, st.session_state.emissions['marche'], 1
        )

st.divider()

# Validation
if 'donnees_2025_validees' not in st.session_state:
    st.session_state.donnees_2025_validees = False

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("✅ Valider les données 2025", type="primary", use_container_width=True):
        calculer_km_territoire()
        st.session_state.donnees_2025_validees = True

        st.rerun()

if st.session_state.donnees_2025_validees:
    st.success("✅ Données 2025 validées !")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("➡️ Voir le bilan 2025", type="primary", use_container_width=True):
            st.switch_page("pages/2_📊_Bilan_2025.py")
