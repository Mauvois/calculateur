# views/previsions.py
"""Module pour l'onglet de prévisions annuelles - Version SAS 2 associés"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List

from config import SCENARIOS_CROISSANCE, CHARGES_FIXES_DEFAUT, OBJECTIFS_REMUNERATION, SIMULATION_PARAMS
from models import Projet, PrevisionAnnuelle, Previsions
from utils import format_currency, format_percentage


def render_previsions_tab():
    """Affiche l'onglet des prévisions annuelles adapté à votre SAS"""
    st.header("📈 Prévisions annuelles - SAS Caribo")
    st.markdown("Construisez votre plan d'affaires basé sur votre réalité : **2 associés, projets géomatique/data spatiale**")

    # Initialisation
    if 'previsions_annuelles' not in st.session_state:
        st.session_state.previsions_annuelles = Previsions()
        st.session_state.projets_annee_1 = []

    # Section objectifs de rémunération
    st.subheader("🎯 Objectifs de rémunération")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Objectif net/associé", format_currency(OBJECTIFS_REMUNERATION["dividendes_nets_par_associe"]))
    with col2:
        st.metric("Total dividendes nets", format_currency(OBJECTIFS_REMUNERATION["total_dividendes_nets"]))
    with col3:
        st.metric("Dividendes bruts nécessaires", format_currency(OBJECTIFS_REMUNERATION["dividendes_bruts_necessaires"]))
    with col4:
        st.metric("Bénéfice avant IS requis", format_currency(OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]))

    st.info("💡 **Calcul SAS** : Flat tax 30% (17,2% prélèvements sociaux + 12,8% IR) + IS 25%")

    st.divider()

    # Section scénarios
    st.subheader("📊 Scénarios de développement")

    scenario_choisi = st.selectbox(
        "Choisissez votre scénario",
        ["Personnalisé"] + list(SCENARIOS_CROISSANCE.keys()),
        help="Scénarios adaptés à votre activité de conseil en géomatique"
    )

    if scenario_choisi != "Personnalisé":
        scenario = SCENARIOS_CROISSANCE[scenario_choisi]

        # Affichage du scénario
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**{scenario_choisi}** : {scenario['description']}")
            st.write(f"**CA objectif année 1** : {format_currency(scenario['ca_objectif_annee_1'])}")
            st.write(f"**Croissance annuelle** : {format_percentage(scenario['taux_croissance'])}")

            # Mix de projets
            st.write("**Mix de projets :**")
            total_ca_mix = 0
            for type_projet, details in scenario['mix_projets'].items():
                ca_type = details['nb'] * details['ca_moyen']
                total_ca_mix += ca_type
                st.write(f"- {details['description']} = {format_currency(ca_type)}")

            st.write(f"**Total CA mix** : {format_currency(total_ca_mix)}")

        with col2:
            # Métriques du scénario
            benefice_prevu = scenario['ca_objectif_annee_1'] - scenario['charges_fixes_initiales']
            taux_marge = benefice_prevu / scenario['ca_objectif_annee_1'] if scenario['ca_objectif_annee_1'] > 0 else 0

            st.metric("Bénéfice brut prévu", format_currency(benefice_prevu))
            st.metric("Taux de marge", format_percentage(taux_marge))

            # Vérification objectif
            if benefice_prevu >= OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]:
                st.success("✅ Objectif rémunération atteignable")
            else:
                manque = OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"] - benefice_prevu
                st.warning(f"⚠️ Manque {format_currency(manque)} pour l'objectif")

        # Bouton pour appliquer le scénario
        if st.button(f"🚀 Appliquer le scénario {scenario_choisi}", type="primary"):
            appliquer_scenario(scenario_choisi, scenario)
            st.success(f"Scénario {scenario_choisi} appliqué !")
            st.rerun()

    st.divider()

    # Section projets personnalisés
    st.subheader("💼 Vos projets de l'année 1")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("➕ Ajouter le projet en cours aux prévisions", type="secondary"):
            if st.session_state.projet_courant and st.session_state.projet_courant.services:
                projet_copie = st.session_state.projet_courant.dupliquer()
                st.session_state.projets_annee_1.append(projet_copie)
                st.success(f"Projet '{projet_copie.nom}' ajouté aux prévisions !")
                st.rerun()
            else:
                st.error("Le projet en cours est vide. Ajoutez des services d'abord.")

    with col2:
        if st.button("🗑️ Vider tous les projets"):
            st.session_state.projets_annee_1 = []
            st.rerun()

    # Affichage des projets
    if st.session_state.projets_annee_1:
        st.write(f"**{len(st.session_state.projets_annee_1)} projets ajoutés**")

        total_ca_projets = 0
        total_maintenance = 0

        for idx, projet in enumerate(st.session_state.projets_annee_1):
            with st.expander(f"{projet.nom} - {format_currency(projet.total_ht)}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**Client :** {projet.client}")
                    st.write(f"**Type :** {projet.type_client}")
                    st.write(f"**Services :** {len(projet.services)}")

                with col2:
                    st.metric("Total HT", format_currency(projet.total_ht))
                    if projet.maintenance_annuelle_ht > 0:
                        st.metric("Maintenance/an", format_currency(projet.maintenance_annuelle_ht))

                with col3:
                    # Multiplicateur projet
                    multiplicateur = st.number_input(
                        "Nb projets similaires/an",
                        min_value=1,
                        max_value=5,
                        value=1,
                        key=f"mult_projet_{idx}",
                        help="Combien de projets similaires dans l'année"
                    )

                    if st.button("🗑️", key=f"del_projet_{idx}"):
                        st.session_state.projets_annee_1.pop(idx)
                        st.rerun()

                total_ca_projets += projet.total_ht * multiplicateur
                total_maintenance += projet.maintenance_annuelle_ht * multiplicateur

        # Résumé financier
        st.divider()
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("CA Projets", format_currency(total_ca_projets))
        with col2:
            st.metric("Maintenance", format_currency(total_maintenance))
        with col3:
            ca_total = total_ca_projets + total_maintenance
            st.metric("CA Total", format_currency(ca_total))
        with col4:
            if ca_total >= OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]:
                st.success("🎯 Objectif OK")
            else:
                st.warning("⚠️ Sous objectif")

    else:
        st.info("Aucun projet ajouté. Utilisez les scénarios ou ajoutez vos projets manuellement.")

    # Section charges et paramètres
    st.divider()
    st.subheader("💰 Charges fixes et paramètres")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Charges fixes annuelles :**")
        total_charges = 0
        for nom, valeur in CHARGES_FIXES_DEFAUT.items():
            nouvelle_valeur = st.number_input(
                nom.replace("_", " ").title(),
                min_value=0,
                value=valeur,
                step=100,
                key=f"charge_{nom}"
            )
            st.session_state.charges_fixes = st.session_state.charges_fixes or {}
            st.session_state.charges_fixes[nom] = nouvelle_valeur
            total_charges += nouvelle_valeur

        st.metric("**Total charges fixes**", format_currency(total_charges))

    with col2:
        st.write("**Paramètres de projection :**")

        nb_annees = st.slider("Nombre d'années", 1, 5, 3)

        taux_croissance = st.slider(
            "Taux de croissance annuel",
            0.0, 0.3, 0.12,
            step=0.01,
            format="%.0f%%"
        )

        taux_inflation = st.slider(
            "Inflation des charges",
            0.0, 0.05, 0.025,
            step=0.005,
            format="%.1f%%"
        )

    # Génération des prévisions
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("🔮 Générer les prévisions", type="primary", use_container_width=True):
            if st.session_state.projets_annee_1:
                generer_previsions_sas(nb_annees, taux_croissance, taux_inflation)
                st.success("Prévisions générées ! Consultez l'onglet 'Résultats & Analyses'")
                st.rerun()
            else:
                st.error("Ajoutez au moins un projet avant de générer les prévisions.")

    with col2:
        # Simulation express
        if st.session_state.projets_annee_1:
            ca_annee_1 = sum(p.total_ht * st.session_state.get(f"mult_projet_{i}", 1)
                           for i, p in enumerate(st.session_state.projets_annee_1))
            benefice_estime = ca_annee_1 - total_charges

            st.write("**Simulation express :**")
            st.write(f"CA année 1 : {format_currency(ca_annee_1)}")
            st.write(f"Bénéfice estimé : {format_currency(benefice_estime)}")

            if benefice_estime >= OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]:
                st.success("🎯 Objectif atteignable")
            else:
                st.warning("⚠️ Revoir le mix projets")


def appliquer_scenario(nom_scenario: str, scenario: dict):
    """Applique un scénario prédéfini"""
    # Vider les projets actuels
    st.session_state.projets_annee_1 = []

    # Créer des projets types basés sur le mix
    for type_projet, details in scenario['mix_projets'].items():
        for i in range(details['nb']):
            # Créer un projet type
            nom_projet = f"{type_projet.replace('_', ' ').title()} {i+1}"
            projet = Projet(
                nom=nom_projet,
                client=f"Client {type_projet} {i+1}",
                type_client="À définir"
            )

            # Ajouter un service générique avec le bon montant
            if st.session_state.catalogue_services:
                # Prendre le premier service disponible comme base
                service_base = list(st.session_state.catalogue_services.values())[0]

                # Calculer la complexité pour avoir le bon prix
                prix_cible = details['ca_moyen']
                if prix_cible <= service_base.prix_min:
                    complexite = "Très faible" if "Très faible" in ["Très faible", "Faible", "Moyenne", "Forte", "Très forte"] else "Faible"
                elif prix_cible >= service_base.prix_max:
                    complexite = "Très forte" if "Très forte" in ["Très faible", "Faible", "Moyenne", "Forte", "Très forte"] else "Forte"
                else:
                    complexite = "Moyenne"

                # Calculer la quantité nécessaire
                prix_unitaire = service_base.calculer_prix(complexite=complexite)
                quantite = max(1, round(prix_cible / prix_unitaire))

                projet.ajouter_service(service_base, complexite=complexite, quantite=quantite)

            st.session_state.projets_annee_1.append(projet)

    # Appliquer les charges du scénario
    ratio_charges = scenario['charges_fixes_initiales'] / sum(CHARGES_FIXES_DEFAUT.values())
    for charge, valeur in CHARGES_FIXES_DEFAUT.items():
        st.session_state.charges_fixes[charge] = int(valeur * ratio_charges)


def generer_previsions_sas(nb_annees: int, taux_croissance: float, taux_inflation: float):
    """Génère les prévisions sur plusieurs années pour la SAS"""
    # Réinitialiser
    st.session_state.previsions_annuelles = Previsions(nom_scenario="SAS Caribo")

    # Calculer les multiplicateurs pour chaque projet
    projets_avec_multiplicateurs = []
    for idx, projet in enumerate(st.session_state.projets_annee_1):
        mult = st.session_state.get(f"mult_projet_{idx}", 1)
        for _ in range(mult):
            projets_avec_multiplicateurs.append(projet)

    # Année 1
    prevision_annee_1 = PrevisionAnnuelle(
        annee=1,
        projets=projets_avec_multiplicateurs,
        charges_fixes=st.session_state.charges_fixes.copy(),
        taux_croissance=0
    )
    st.session_state.previsions_annuelles.ajouter_annee(prevision_annee_1)

    # Années suivantes avec adaptation SAS
    st.session_state.previsions_annuelles.generer_projections(
        nb_annees=nb_annees,
        taux_croissance=taux_croissance,
        charges_fixes_base=st.session_state.charges_fixes,
        taux_inflation=taux_inflation
    )
