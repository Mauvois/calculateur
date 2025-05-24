# views/previsions.py
"""Module pour l'onglet de prévisions annuelles"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List

from config import SCENARIOS_CROISSANCE, CHARGES_FIXES_DEFAUT
from models import Projet, PrevisionAnnuelle, Previsions
from utils import format_currency, format_percentage


def render_previsions_tab():
    """Affiche l'onglet des prévisions annuelles"""
    st.header("📈 Prévisions annuelles")
    st.markdown("Construisez votre plan d'affaires en ajoutant des projets et en définissant vos charges.")

    # Initialisation des prévisions si nécessaire
    if 'previsions_annuelles' not in st.session_state:
        st.session_state.previsions_annuelles = Previsions()
        st.session_state.projets_annee_1 = []

    # Section 1 : Gestion des projets de l'année 1
    st.subheader("1. Projets prévus pour l'année 1")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Option pour ajouter le projet en cours
        if st.button("➕ Ajouter le projet en cours aux prévisions", type="primary"):
            if st.session_state.projet_courant and st.session_state.projet_courant.services:
                projet_copie = st.session_state.projet_courant.dupliquer()
                st.session_state.projets_annee_1.append(projet_copie)
                st.success(f"Projet '{projet_copie.nom}' ajouté aux prévisions !")
            else:
                st.error("Le projet en cours est vide. Ajoutez des services d'abord.")

    with col2:
        # Bouton pour charger un scénario type
        scenario_type = st.selectbox(
            "Charger un scénario type",
            ["Personnalisé"] + list(SCENARIOS_CROISSANCE.keys())
        )

        if scenario_type != "Personnalisé":
            if st.button("Appliquer le scénario", key="apply_scenario"):
                charger_scenario_type(scenario_type)
                st.rerun()

    # Affichage des projets ajoutés
    if st.session_state.projets_annee_1:
        st.write(f"**{len(st.session_state.projets_annee_1)} projets ajoutés**")

        total_ca_projets = 0
        total_maintenance = 0

        for idx, projet in enumerate(st.session_state.projets_annee_1):
            with st.expander(f"{projet.nom} - {format_currency(projet.total_ht)}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**Client :** {projet.client}")
                    st.write(f"**Services :** {len(projet.services)}")

                    # Détail des services
                    for service in projet.services:
                        st.write(f"- {service.service.nom} ({service.quantite}x)")

                with col2:
                    st.metric("Total HT", format_currency(projet.total_ht))
                    if projet.maintenance_annuelle_ht > 0:
                        st.metric("Maintenance/an", format_currency(projet.maintenance_annuelle_ht))

                with col3:
                    # Nombre de fois ce projet dans l'année
                    multiplicateur = st.number_input(
                        "Nombre de fois",
                        min_value=1,
                        max_value=10,
                        value=1,
                        key=f"mult_projet_{idx}",
                        help="Combien de fois ce type de projet sera réalisé dans l'année"
                    )

                    if st.button("🗑️", key=f"del_projet_{idx}"):
                        st.session_state.projets_annee_1.pop(idx)
                        st.rerun()

                total_ca_projets += projet.total_ht * multiplicateur
                total_maintenance += projet.maintenance_annuelle_ht * multiplicateur

        # Résumé
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CA Projets année 1", format_currency(total_ca_projets))
        with col2:
            st.metric("Maintenance année 1", format_currency(total_maintenance))
        with col3:
            st.metric("CA Total année 1", format_currency(total_ca_projets + total_maintenance))

    else:
        st.info("Aucun projet ajouté. Utilisez le bouton ci-dessus ou chargez un scénario type.")

    # Section 2 : Charges fixes
    st.divider()
    st.subheader("2. Charges fixes annuelles")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.charges_fixes["loyer"] = st.number_input(
            "Loyer / Bureau (€/an)",
            min_value=0,
            max_value=50000,
            value=st.session_state.charges_fixes.get("loyer", CHARGES_FIXES_DEFAUT["loyer"]),
            step=100,
            help="Charges locatives annuelles"
        )

        st.session_state.charges_fixes["logiciels"] = st.number_input(
            "Logiciels / Outils (€/an)",
            min_value=0,
            max_value=20000,
            value=st.session_state.charges_fixes.get("logiciels", CHARGES_FIXES_DEFAUT["logiciels"]),
            step=100,
            help="Licences et abonnements"
        )

        st.session_state.charges_fixes["deplacements"] = st.number_input(
            "Déplacements (€/an)",
            min_value=0,
            max_value=20000,
            value=st.session_state.charges_fixes.get("deplacements", CHARGES_FIXES_DEFAUT["deplacements"]),
            step=100,
            help="Frais de déplacement et missions"
        )

    with col2:
        st.session_state.charges_fixes["materiel"] = st.number_input(
            "Matériel (€/an)",
            min_value=0,
            max_value=20000,
            value=st.session_state.charges_fixes.get("materiel", CHARGES_FIXES_DEFAUT["materiel"]),
            step=100,
            help="Matériel informatique et bureautique"
        )

        st.session_state.charges_fixes["admin"] = st.number_input(
            "Admin / Compta (€/an)",
            min_value=0,
            max_value=20000,
            value=st.session_state.charges_fixes.get("admin", CHARGES_FIXES_DEFAUT["admin"]),
            step=100,
            help="Frais administratifs et comptables"
        )

        # Total des charges
        total_charges = sum(st.session_state.charges_fixes.values())
        st.metric("Total charges fixes", format_currency(total_charges))

    # Section 3 : Paramètres de projection
    st.divider()
    st.subheader("3. Paramètres de projection")

    col1, col2, col3 = st.columns(3)

    with col1:
        nb_annees = st.slider(
            "Nombre d'années",
            min_value=1,
            max_value=5,
            value=3,
            help="Période de projection"
        )

    with col2:
        taux_croissance = st.slider(
            "Taux de croissance annuel",
            min_value=0.0,
            max_value=0.5,
            value=0.15,
            step=0.05,
            format="%.0f%%",
            help="Croissance du CA année après année"
        )

    with col3:
        taux_inflation = st.slider(
            "Inflation des charges",
            min_value=0.0,
            max_value=0.1,
            value=0.02,
            step=0.01,
            format="%.0f%%",
            help="Augmentation annuelle des charges"
        )

    # Bouton de génération des prévisions
    if st.button("🔮 Générer les prévisions", type="primary"):
        if st.session_state.projets_annee_1:
            generer_previsions(nb_annees, taux_croissance, taux_inflation)
            st.success("Prévisions générées ! Consultez l'onglet 'Résultats & Analyses'")
        else:
            st.error("Ajoutez au moins un projet avant de générer les prévisions.")


def charger_scenario_type(scenario_nom: str):
    """Charge un scénario type avec des projets prédéfinis"""
    scenario = SCENARIOS_CROISSANCE[scenario_nom]

    # Vider les projets actuels
    st.session_state.projets_annee_1 = []

    # Créer des projets types selon le scénario
    if scenario_nom == "Prudent":
        # 15 projets : mix de petits projets
        # 5 audits simples
        for i in range(5):
            projet = Projet(nom=f"Audit commune {i+1}", client=f"Commune {i+1}", type_client="Petite commune rurale")
            projet.ajouter_service(
                st.session_state.catalogue_services["audit_intelligence_spatiale"],
                complexite="Faible",
                quantite=1
            )
            st.session_state.projets_annee_1.append(projet)

        # 5 analyses spatiales
        for i in range(5):
            projet = Projet(nom=f"Analyse spatiale {i+1}", client=f"Client {i+1}", type_client="")
            projet.ajouter_service(
                st.session_state.catalogue_services["analyse_spatiale"],
                complexite="Moyenne",
                quantite=1
            )
            st.session_state.projets_annee_1.append(projet)

        # 5 formations
        for i in range(5):
            projet = Projet(nom=f"Formation {i+1}", client=f"Client {i+1}", type_client="")
            projet.ajouter_service(
                st.session_state.catalogue_services["formation"],
                complexite="Moyenne",
                quantite=1
            )
            st.session_state.projets_annee_1.append(projet)

    elif scenario_nom == "Réaliste":
        # 25 projets : mix équilibré
        # Charger les templates et les multiplier
        templates = ["commune", "promoteur", "association"]
        for template in templates:
            for i in range(3):
                projet = st.session_state.templates_projets[template].dupliquer()
                projet.nom = f"{projet.nom} - {i+1}"
                st.session_state.projets_annee_1.append(projet)

        # Ajouter quelques projets moyens
        for i in range(10):
            projet = Projet(nom=f"Projet moyen {i+1}", client=f"Client {i+1}", type_client="")
            projet.ajouter_service(
                st.session_state.catalogue_services["dashboard"],
                complexite="Moyenne",
                quantite=1
            )
            st.session_state.projets_annee_1.append(projet)

    elif scenario_nom == "Ambitieux":
        # 40 projets : beaucoup de gros projets
        # Plusieurs gros projets type EPCI et CTM
        for i in range(5):
            projet = st.session_state.templates_projets["epci"].dupliquer()
            projet.nom = f"EPCI - Projet {i+1}"
            st.session_state.projets_annee_1.append(projet)

        for i in range(3):
            projet = st.session_state.templates_projets["ctm"].dupliquer()
            projet.nom = f"Collectivité - Projet {i+1}"
            st.session_state.projets_annee_1.append(projet)

        # Projets moyens et petits pour compléter
        for i in range(20):
            projet = st.session_state.templates_projets["promoteur"].dupliquer()
            projet.nom = f"Promoteur - Projet {i+1}"
            st.session_state.projets_annee_1.append(projet)

    # Mettre à jour les charges selon le scénario
    charges_base = scenario["charges_fixes_initiales"]
    ratio = charges_base / sum(CHARGES_FIXES_DEFAUT.values())

    for charge, valeur in CHARGES_FIXES_DEFAUT.items():
        st.session_state.charges_fixes[charge] = int(valeur * ratio)


def generer_previsions(nb_annees: int, taux_croissance: float, taux_inflation: float):
    """Génère les prévisions sur plusieurs années"""
    # Réinitialiser les prévisions
    st.session_state.previsions_annuelles = Previsions()

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
        taux_croissance=0  # Pas de croissance en année 1
    )
    st.session_state.previsions_annuelles.ajouter_annee(prevision_annee_1)

    # Générer les projections pour les années suivantes
    st.session_state.previsions_annuelles.generer_projections(
        nb_annees=nb_annees,
        taux_croissance=taux_croissance,
        charges_fixes_base=st.session_state.charges_fixes,
        taux_inflation=taux_inflation
    )
