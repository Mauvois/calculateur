# views/export.py
"""Module pour l'onglet d'export des documents"""

import streamlit as st
from datetime import datetime

from utils import generer_pdf_devis, export_to_excel, format_currency
from config import TAUX_TVA


def render_export_tab():
    """Affiche l'onglet d'export des documents"""
    st.header("📄 Export des documents")
    st.markdown("Générez des devis PDF et exportez vos données vers Excel.")

    # Section 1 : Export du projet en cours
    st.subheader("1. Devis du projet en cours")

    if (st.session_state.projet_courant and
        st.session_state.projet_courant.services):

        # Aperçu du projet
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"**Projet :** {st.session_state.projet_courant.nom}")
            st.write(f"**Client :** {st.session_state.projet_courant.client or 'Non renseigné'}")
            st.write(f"**Nombre de services :** {len(st.session_state.projet_courant.services)}")

        with col2:
            st.metric("Total HT", format_currency(st.session_state.projet_courant.total_ht))
            st.metric("Total TTC", format_currency(st.session_state.projet_courant.total_ttc))

        # Options d'export
        st.write("\n**Options du devis :**")

        col1, col2 = st.columns(2)

        with col1:
            # Informations complémentaires pour le devis
            reference_devis = st.text_input(
                "Référence du devis",
                value=f"DEV-{datetime.now().strftime('%Y%m%d')}-001",
                help="Référence unique du devis"
            )

            validite_devis = st.number_input(
                "Validité du devis (jours)",
                min_value=15,
                max_value=90,
                value=30,
                help="Durée de validité du devis"
            )

        with col2:
            conditions_paiement = st.selectbox(
                "Conditions de paiement",
                ["30 jours net", "50% à la commande, 50% à la livraison",
                 "30% - 40% - 30%", "Comptant à réception"],
                help="Modalités de paiement"
            )

            inclure_details = st.checkbox(
                "Inclure le détail des livrables",
                value=True,
                help="Ajoute la description détaillée de chaque service"
            )

        # Bouton de génération
        if st.button("📄 Générer le devis PDF", type="primary"):
            try:
                # Générer le PDF (fonction à adapter avec les nouvelles options)
                pdf_bytes = generer_pdf_devis(st.session_state.projet_courant)

                # Bouton de téléchargement
                st.download_button(
                    label="💾 Télécharger le devis PDF",
                    data=pdf_bytes,
                    file_name=f"Devis_{st.session_state.projet_courant.nom.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )

                st.success("✅ Devis généré avec succès !")

            except Exception as e:
                st.error(f"❌ Erreur lors de la génération du PDF : {str(e)}")

    else:
        st.info("Aucun projet en cours. Créez un projet dans l'onglet 'Calculateur de projet'.")

    # Section 2 : Export des prévisions
    st.divider()
    st.subheader("2. Export des prévisions financières")

    if ('previsions_annuelles' in st.session_state and
        st.session_state.previsions_annuelles.annees):

        # Aperçu des prévisions
        df_resultats = st.session_state.previsions_annuelles.get_dataframe_resultats()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Nombre d'années", len(df_resultats))
            st.metric("CA année 1", format_currency(df_resultats.iloc[0]["CA Total"]))

        with col2:
            st.metric("CA moyen", format_currency(df_resultats["CA Total"].mean()))
            st.metric("Résultat net moyen", format_currency(df_resultats["Résultat net"].mean()))

        with col3:
            st.metric("Nombre de projets", len(st.session_state.projets_annee_1))
            ca_derniere_annee = df_resultats.iloc[-1]["CA Total"]
            st.metric(f"CA année {len(df_resultats)}", format_currency(ca_derniere_annee))

        # Options d'export Excel
        st.write("\n**Options d'export Excel :**")

        inclure_graphiques = st.checkbox(
            "Inclure les graphiques",
            value=True,
            help="Ajoute des graphiques dans le fichier Excel"
        )

        inclure_details_projets = st.checkbox(
            "Inclure le détail des projets",
            value=True,
            help="Ajoute une feuille avec le détail de chaque projet"
        )

        # Bouton d'export Excel
        if st.button("📊 Générer le fichier Excel", type="secondary"):
            try:
                # Générer le fichier Excel
                excel_bytes = export_to_excel(
                    df_resultats,
                    st.session_state.projet_courant if inclure_details_projets else None
                )

                # Bouton de téléchargement
                st.download_button(
                    label="💾 Télécharger le fichier Excel",
                    data=excel_bytes,
                    file_name=f"Previsions_Datamap_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.success("✅ Fichier Excel généré avec succès !")

            except Exception as e:
                st.error(f"❌ Erreur lors de la génération du fichier Excel : {str(e)}")

    else:
        st.info("Aucune prévision disponible. Générez des prévisions dans l'onglet 'Prévisions annuelles'.")

    # Section 3 : Export du catalogue de services
    st.divider()
    st.subheader("3. Export du catalogue de services")

    st.write("Exportez votre catalogue de services complet avec les tarifs.")

    format_catalogue = st.radio(
        "Format d'export",
        ["PDF - Catalogue commercial", "Excel - Liste détaillée"],
        help="Choisissez le format adapté à votre usage"
    )

    if st.button("📚 Générer le catalogue", type="secondary"):
        if format_catalogue == "Excel - Liste détaillée":
            # Créer un DataFrame du catalogue
            catalogue_data = []
            for service_id, service in st.session_state.catalogue_services.items():
                catalogue_data.append({
                    "Catégorie": service.categorie,
                    "Service": service.nom,
                    "Description": service.description,
                    "Livrable": service.livrable,
                    "Prix min (€)": service.prix_min,
                    "Prix max (€)": service.prix_max,
                    "Maintenance": "Oui" if service.maintenance_applicable else "Non"
                })

            import pandas as pd
            import io

            df_catalogue = pd.DataFrame(catalogue_data)

            # Créer le fichier Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_catalogue.to_excel(writer, sheet_name='Catalogue', index=False)

                # Mise en forme
                workbook = writer.book
                worksheet = writer.sheets['Catalogue']

                # Format monétaire pour les colonnes de prix
                money_format = workbook.add_format({'num_format': '#,##0 €'})
                worksheet.set_column('E:F', 12, money_format)

                # Ajuster la largeur des colonnes
                worksheet.set_column('A:A', 30)  # Catégorie
                worksheet.set_column('B:B', 40)  # Service
                worksheet.set_column('C:D', 50)  # Description et Livrable

            output.seek(0)

            st.download_button(
                label="💾 Télécharger le catalogue Excel",
                data=output.read(),
                file_name=f"Catalogue_Datamap_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Catalogue Excel généré avec succès !")

        else:
            st.warning("🚧 Export PDF du catalogue en cours de développement...")

    # Section 4 : Modèles de documents
    st.divider()
    st.subheader("4. Modèles de documents")

    st.write("Téléchargez des modèles de documents utiles pour votre activité.")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Documents commerciaux :**")
        st.write("- 📄 Modèle de proposition commerciale")
        st.write("- 📋 Template de cahier des charges")
        st.write("- 📊 Modèle de rapport d'audit")

    with col2:
        st.write("**Documents administratifs :**")
        st.write("- 📑 Conditions générales de vente")
        st.write("- 🤝 Modèle de contrat de prestation")
        st.write("- 📝 Template de bon de commande")

    st.info("💡 Les modèles de documents seront disponibles dans une prochaine version.")
