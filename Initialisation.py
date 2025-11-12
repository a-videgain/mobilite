import streamlit as st
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

st.set_page_config(
    page_title="Mobilité Pays Basque 2050 - ESTIA",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Mobilité Pays Basque 2050  - ESTIA")


st.header("🎯 Projet Décarbonation des Mobilités")

st.markdown("""
### 📋 Contexte du projet

Dans le cadre de la **Stratégie Nationale Bas-Carbone (SNBC)**, la France s'est fixée un objectif ambitieux : 
**réduire d'environ 70% les émissions du secteur transport d'ici 2050** par rapport à la situation actuelle. [Stratégie SNBC Transports](https://www.ecologie.gouv.fr/sites/default/files/documents/Fiche%20SNBC%20Transports_0.pdf).

Ce projet vous propose d'explorer les leviers d'action possibles pour atteindre cet objectif 
sur le territoire du **Pays Basque** . Consultez la [fiche INSEE CAPB](https://www.insee.fr/fr/statistiques/2011101?geo=EPCI-200067106).


### 🎓 Objectifs pédagogiques

À travers cette application, vous allez :
- 📊 Analyser les données de mobilité actuelles du territoire
- 🎯 Construire un scénario 2050 en combinant différents leviers d'action
- 📈 Évaluer l'impact de vos choix sur les émissions de CO₂
- 🧩 Comprendre quels leviers sont les plus efficaces pour décarboner la mobilité

### 🔧 Les 5 leviers disponibles

1. **⚡ Électrification** : Remplacer les véhicules thermiques par des électriques
2. **📉 Sobriété** : Réduire le nombre de km parcourus
3. **🔄 Report modal** : Transférer vers des modes moins émetteurs (vélo, bus, train)
4. **👥 Taux de remplissage** : Augmenter l'occupation des véhicules
5. **🪶 Allègement** : Réduire le poids des véhicules

### 🚀 Démarrage

Cliquez sur "Commencer" pour accéder aux données de mobilité 2025.

### 📦 Livrable attendu

À la fin de ce projet, vous devrez produire un rapport (format docx ou pdf) présentant :
- **Un scénario 2050** cohérent et justifié permettant d'atteindre l'objectif de -70% d'émissions. Ce scénario sera propre au groupe de travail.
- **Une analyse** de votre scénario : quels leviers sont les plus efficaces ? Le niveau de chaque levier est-il réaliste ?
- **Une synthèse** présentant vos choix sur chaque levier
- **Un plan d'action**: les actions à mettre en place par les pouvoirs publics et par les citoyen.ne.s pour parvenir à atteindre les évolutions de chaque levier.
- **Une critique** de l'outil utilisé: les limites des hypothèses simplificatrices


💡 L'outil permet un export des données** (fichier .txt) contenant l'ensemble des résultats.
Pensez à **sauvegarder régulièrement** vos données en exportant vos résultats !


""")



st.info("👈 Utilisez la navigation à gauche pour accéder aux différentes pages")

if st.button("🚀 Commencer", type="primary", use_container_width=True):
    st.switch_page("pages/1_📝_Donnees_2025.py")
    st.session_state.logged_in = False
    st.session_state.code_groupe = None
    st.rerun()
