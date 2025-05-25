# app.py
"""Application principale du calculateur financier Caribo"""

import streamlit as st
from config import APP_CONFIG, NIVEAUX_COMPLEXITE, TYPES_CLIENTS
from utils import init_session_state, format_currency, load_template_projet
from models import ServiceSelectionne, Projet

# Configuration de la page
st.set_page_config(
    page_title=APP_CONFIG['title'],
    page_icon=APP_CONFIG['page_icon'],
    layout=APP_CONFIG['layout'],
    initial_sidebar_state=APP_CONFIG['initial_sidebar_state']
)

# Initialisation
init_session_state()

# Titre principal
st.title(f"{APP_CONFIG['page_icon']} {APP_CONFIG['title']}")
st.markdown("Estimez vos prix de projets et construisez vos prévisions financières")

# Onglets principaux
tabs = st.tabs(["💰 Calculateur de projet", "📈 Prévisions annuelles", "📊 Résultats & Analyses", "📄 Export"])

# ONGLET 1 : Calculateur de projet
with tabs[0]:
    st.header("Calculateur de projet")

    # Section Templates
    st.subheader("📋 Templates de projets")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏢 EPCI - Projet ZAN", use_container_width=True):
            st.session_state.projet_courant = load_template_projet("epci")
            st.success("Template EPCI chargé !")
            st.rerun()

        if st.button("🏘️ Commune - Vacance", use_container_width=True):
            st.session_state.projet_courant = load_template_projet("commune")
            st.success("Template Commune chargé !")
            st.rerun()

    with col2:
        if st.button("🏗️ Promoteur - 300 logements", use_container_width=True):
            st.session_state.projet_courant = load_template_projet("promoteur")
            st.success("Template Promoteur chargé !")
            st.rerun()

        if st.button("🏛️ CTM - SOSTE", use_container_width=True):
            st.session_state.projet_courant = load_template_projet("ctm")
            st.success("Template CTM chargé !")
            st.rerun()

    with col3:
        if st.button("🌿 Association - Mangrove", use_container_width=True):
            st.session_state.projet_courant = load_template_projet("association")
            st.success("Template Association chargé !")
            st.rerun()

        if st.button("🆕 Nouveau projet vierge", use_container_width=True):
            st.session_state.projet_courant = Projet(nom="Nouveau projet")
            st.success("Nouveau projet créé !")
            st.rerun()

    st.divider()

    # Informations du projet
    st.subheader("📝 Informations du projet")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.projet_courant.nom = st.text_input(
            "Nom du projet",
            value=st.session_state.projet_courant.nom
        )
        st.session_state.projet_courant.client = st.text_input(
            "Client",
            value=st.session_state.projet_courant.client
        )

    with col2:
        # Gérer la compatibilité avec les anciens types de clients des templates
        type_client_actuel = st.session_state.projet_courant.type_client
        try:
            # Essayer de trouver le type client dans la nouvelle liste
            index_actuel = TYPES_CLIENTS.index(type_client_actuel) + 1 if type_client_actuel else 0
        except ValueError:
            # Si le type client n'existe pas dans la nouvelle liste, utiliser l'index 0 (vide)
            index_actuel = 0

        st.session_state.projet_courant.type_client = st.selectbox(
            "Type de client",
            options=[""] + TYPES_CLIENTS,
            index=index_actuel
        )

        # Mode d'affichage
        st.session_state.mode_avance = st.checkbox("Mode avancé (réglages détaillés)", value=st.session_state.mode_avance)

    st.divider()

    # Services du projet
    st.subheader("🛠️ Services du projet")

    # Affichage des services existants
    if st.session_state.projet_courant.services:
        for idx, service_sel in enumerate(st.session_state.projet_courant.services):
            with st.expander(f"**{service_sel.service.nom}** - {format_currency(service_sel.prix_total)}", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    # Quantité
                    nouvelle_quantite = st.number_input(
                        "Quantité",
                        min_value=1,
                        value=service_sel.quantite,
                        key=f"quantite_{idx}"
                    )
                    if nouvelle_quantite != service_sel.quantite:
                        service_sel.quantite = nouvelle_quantite
                        st.rerun()

                with col2:
                    if st.session_state.mode_avance and service_sel.service.facteurs_variation:
                        # Mode avancé : sliders pour chaque facteur
                        st.write("**Facteurs de variation :**")
                        facteurs_modifies = False
                        nouveaux_facteurs = {}

                        for facteur in service_sel.service.facteurs_variation:
                            valeur_actuelle = service_sel.facteurs_custom.get(facteur.nom, facteur.valeur_defaut)
                            nouvelle_valeur = st.slider(
                                facteur.nom,
                                min_value=float(facteur.impact_min),
                                max_value=float(facteur.impact_max),
                                value=float(valeur_actuelle),
                                key=f"facteur_{idx}_{facteur.nom}",
                                help=facteur.description
                            )
                            nouveaux_facteurs[facteur.nom] = nouvelle_valeur
                            if nouvelle_valeur != valeur_actuelle:
                                facteurs_modifies = True

                        if facteurs_modifies:
                            service_sel.facteurs_custom = nouveaux_facteurs
                            service_sel.prix_unitaire = service_sel.service.calculer_prix(facteurs_custom=nouveaux_facteurs)
                            st.rerun()

                    elif st.session_state.mode_avance and not service_sel.service.facteurs_variation:
                        # Mode avancé mais pas de facteurs : afficher un message
                        st.info("Ce service n'a pas de facteurs de variation configurés")

                    if not st.session_state.mode_avance or not service_sel.service.facteurs_variation:
                        # Mode simple : sélection de la complexité
                        # Gérer la compatibilité avec les anciennes valeurs de complexité
                        complexite_actuelle = service_sel.complexite
                        if complexite_actuelle not in NIVEAUX_COMPLEXITE:
                            # Si l'ancienne complexité n'existe plus, prendre la valeur médiane
                            complexite_actuelle = list(NIVEAUX_COMPLEXITE.keys())[len(NIVEAUX_COMPLEXITE)//2]

                        nouvelle_complexite = st.select_slider(
                            "Complexité",
                            options=list(NIVEAUX_COMPLEXITE.keys()),
                            value=complexite_actuelle,
                            key=f"complexite_{idx}"
                        )
                        if nouvelle_complexite != service_sel.complexite:
                            service_sel.complexite = nouvelle_complexite
                            service_sel.prix_unitaire = service_sel.service.calculer_prix(complexite=nouvelle_complexite)
                            st.rerun()

                with col3:
                    st.write(f"**Prix unitaire :**")
                    st.write(format_currency(service_sel.prix_unitaire))

                    if st.button("🗑️ Supprimer", key=f"suppr_{idx}"):
                        st.session_state.projet_courant.retirer_service(idx)
                        st.rerun()

                # Afficher les détails du service
                st.write(f"**Livrable :** {service_sel.service.livrable}")
                st.write(f"**Valeur client :** {service_sel.service.valeur_client}")

                if service_sel.service.maintenance_applicable:
                    st.info(f"💡 Maintenance annuelle estimée : {format_currency(service_sel.maintenance_annuelle)}")
    else:
        st.info("Aucun service ajouté. Utilisez le bouton ci-dessous pour ajouter des services.")

    # Ajouter un nouveau service
    st.divider()
    st.subheader("➕ Ajouter un service")

    # Sélection par catégorie
    categories = list(set(s.categorie for s in st.session_state.catalogue_services.values()))
    categorie_selectionnee = st.selectbox("Catégorie", ["Toutes"] + sorted(categories))

    # Filtrer les services
    services_disponibles = list(st.session_state.catalogue_services.values())
    if categorie_selectionnee != "Toutes":
        services_disponibles = [s for s in services_disponibles if s.categorie == categorie_selectionnee]

    # Sélection du service
    if services_disponibles:
        service_selectionne = st.selectbox(
            "Service",
            options=services_disponibles,
            format_func=lambda s: f"{s.nom} ({format_currency(s.prix_min)} - {format_currency(s.prix_max)})"
        )

        if service_selectionne:
            col1, col2, col3 = st.columns(3)

            with col1:
                quantite_nouveau = st.number_input("Quantité", min_value=1, value=1, key="quantite_nouveau")

            with col2:
                complexite_nouveau = st.select_slider(
                    "Complexité",
                    options=list(NIVEAUX_COMPLEXITE.keys()),
                    value=list(NIVEAUX_COMPLEXITE.keys())[2],  # Prendre le 3ème élément (index 2) = niveau médian
                    key="complexite_nouveau"
                )

            with col3:
                if st.button("➕ Ajouter au projet", type="primary", use_container_width=True):
                    # Initialiser les facteurs_custom avec les valeurs par défaut si le service en a
                    facteurs_custom = {}
                    if service_selectionne.facteurs_variation:
                        for facteur in service_selectionne.facteurs_variation:
                            facteurs_custom[facteur.nom] = facteur.valeur_defaut

                    st.session_state.projet_courant.ajouter_service(
                        service_selectionne,
                        complexite=complexite_nouveau,
                        quantite=quantite_nouveau,
                        facteurs_custom=facteurs_custom if facteurs_custom else None
                    )
                    st.success(f"Service '{service_selectionne.nom}' ajouté !")
                    st.rerun()

    # Résumé du projet
    st.divider()
    st.subheader("📊 Résumé du projet")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total HT", format_currency(st.session_state.projet_courant.total_ht))

    with col2:
        st.metric("TVA (8,5%)", format_currency(st.session_state.projet_courant.tva))

    with col3:
        st.metric("Total TTC", format_currency(st.session_state.projet_courant.total_ttc))

    with col4:
        if st.session_state.projet_courant.maintenance_annuelle_ht > 0:
            st.metric("Maintenance/an", format_currency(st.session_state.projet_courant.maintenance_annuelle_ht))
        else:
            st.metric("Maintenance/an", "N/A")

# ONGLET 2 : Prévisions annuelles
with tabs[1]:
    from views.previsions import render_previsions_tab
    render_previsions_tab()

# ONGLET 3 : Résultats & Analyses
with tabs[2]:
    from views.resultats import render_resultats_tab
    render_resultats_tab()

# ONGLET 4 : Export
with tabs[3]:
    from views.export import render_export_tab
    render_export_tab()
