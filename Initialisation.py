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
    page_title="Mobilité Pays Basque 2050",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Mobilité Pays Basque 2050")


st.header("🎯 Projet Décarbonation des Transports")

st.markdown("""
### 📋 Contexte du projet

Dans le cadre de la **Stratégie Nationale Bas-Carbone (SNBC)**, la France s'est fixée un objectif ambitieux : 
**réduire d'environ 70% les émissions du secteur transport d'ici 2050** par rapport à la situation actuelle.

Ce projet vous propose d'explorer les leviers d'action possibles pour atteindre cet objectif 
sur le territoire du **Pays Basque** (350 000 habitants).

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
5. **🪶 Allègement** : Réduire le poids des véhicules)
### 🚀 Démarrage

Cliquez sur "Commencer" pour accéder aux données de mobilité 2025.
"""

st.info("👈 Utilisez la navigation à gauche pour accéder aux différentes pages")

if st.button("🚀 Commencer",, type="primary", use_container_width=True):
    st.switch_page("pages/1_📝_Donnees_2025.py")
    st.session_state.logged_in = False
    st.session_state.code_groupe = None
    st.rerun()
