# utils.py
"""Fonctions utilitaires pour le calculateur Caribo"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Dict, Any
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents

from config import GRAPH_CONFIG, PDF_CONFIG
from models import Projet, Previsions


def format_currency(value: float, include_cents: bool = False) -> str:
    """Formate une valeur monétaire"""
    if include_cents:
        return f"{value:,.2f} €"
    return f"{value:,.0f} €"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formate un pourcentage"""
    return f"{value * 100:.{decimals}f}%"


def init_session_state():
    """Initialise les variables de session Streamlit"""
    if 'initialized' not in st.session_state:
        from data import creer_catalogue_services, creer_templates_projets
        from config import CHARGES_FIXES_DEFAUT

        # Charger le catalogue et les templates
        st.session_state.catalogue_services = creer_catalogue_services()
        st.session_state.templates_projets = creer_templates_projets(st.session_state.catalogue_services)

        # Initialiser le projet en cours
        st.session_state.projet_courant = Projet(nom="Nouveau projet")

        # Initialiser les prévisions
        st.session_state.previsions = Previsions()

        # Charges fixes
        st.session_state.charges_fixes = CHARGES_FIXES_DEFAUT.copy()

        # Options d'affichage
        st.session_state.mode_avance = False

        st.session_state.initialized = True


def creer_graphique_ca_evolution(df_resultats: pd.DataFrame) -> plt.Figure:
    """Crée un graphique d'évolution du CA et du résultat net"""
    plt.style.use(GRAPH_CONFIG['style'])
    fig, ax = plt.subplots(figsize=GRAPH_CONFIG['figsize'])

    # Tracer les courbes
    ax.plot(df_resultats["Année"], df_resultats["CA Total"],
            marker='o', linewidth=2, label="CA Total", color=GRAPH_CONFIG['colors'][0])
    ax.plot(df_resultats["Année"], df_resultats["Résultat net"],
            marker='s', linewidth=2, label="Résultat net", color=GRAPH_CONFIG['colors'][1])

    # Mise en forme
    ax.set_xlabel("Année", fontsize=12)
    ax.set_ylabel("Montant (€)", fontsize=12)
    ax.set_title("Évolution du CA et du résultat net", fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='best', framealpha=0.9)

    # Formater l'axe Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k€"))

    # Ajuster les marges
    plt.tight_layout()

    return fig


def creer_graphique_repartition(df_resultats: pd.DataFrame, annee: int = 1) -> plt.Figure:
    """Crée un graphique de répartition des charges et résultats"""
    plt.style.use(GRAPH_CONFIG['style'])
    fig, ax = plt.subplots(figsize=GRAPH_CONFIG['figsize'])

    # Récupérer les données de l'année spécifiée
    donnees_annee = df_resultats[df_resultats["Année"] == annee].iloc[0]

    # Préparer les données pour le graphique
    categories = ["CA Projets", "CA Maintenance", "Charges fixes", "Impôt", "Résultat net"]
    valeurs = [
        donnees_annee["CA Projets"],
        donnees_annee["CA Maintenance"],
        -donnees_annee["Charges fixes"],
        -donnees_annee["Impôt"],
        donnees_annee["Résultat net"]
    ]

    # Créer le graphique en cascade (waterfall)
    cumsum = 0
    for i, (cat, val) in enumerate(zip(categories, valeurs)):
        if i < 2:  # Revenus
            ax.bar(cat, val, bottom=cumsum, color=GRAPH_CONFIG['colors'][0], alpha=0.8)
            cumsum += val
        elif i < 4:  # Charges
            ax.bar(cat, val, bottom=cumsum + val, color=GRAPH_CONFIG['colors'][3], alpha=0.8)
            cumsum += val
        else:  # Résultat net
            color = GRAPH_CONFIG['colors'][2] if val > 0 else GRAPH_CONFIG['colors'][3]
            ax.bar(cat, val, color=color, alpha=0.8)

    # Mise en forme
    ax.set_ylabel("Montant (€)", fontsize=12)
    ax.set_title(f"Analyse financière - Année {annee}", fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax.axhline(y=0, color='black', linewidth=1)

    # Rotation des labels
    plt.xticks(rotation=45, ha='right')

    # Formater l'axe Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k€"))

    plt.tight_layout()

    return fig


def generer_pdf_devis(projet: Projet) -> bytes:
    """Génère un devis PDF pour un projet"""
    buffer = io.BytesIO()

    # Créer le document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=PDF_CONFIG['margin'],
        leftMargin=PDF_CONFIG['margin'],
        topMargin=PDF_CONFIG['margin'],
        bottomMargin=PDF_CONFIG['margin']
    )

    # Styles
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=PDF_CONFIG['title_size'],
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30
    )
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=PDF_CONFIG['subtitle_size'],
        textColor=colors.HexColor('#333333'),
        spaceAfter=20
    )

    # Contenu du document
    elements = []

    # En-tête
    elements.append(Paragraph("DEVIS", style_title))
    elements.append(Paragraph(f"Projet : {projet.nom}", style_subtitle))
    elements.append(Paragraph(f"Client : {projet.client}", styles['Normal']))
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))

    # Tableau des services
    data = [["Service", "Quantité", "Prix unitaire HT", "Total HT"]]

    for service_sel in projet.services:
        data.append([
            Paragraph(service_sel.service.nom, styles['Normal']),
            str(service_sel.quantite),
            format_currency(service_sel.prix_unitaire),
            format_currency(service_sel.prix_total)
        ])

    # Créer le tableau
    table = Table(data, colWidths=[3.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))

    # Totaux
    total_data = [
        ["", "", "Total HT :", format_currency(projet.total_ht)],
        ["", "", "TVA (8,5%) :", format_currency(projet.tva)],
        ["", "", "Total TTC :", format_currency(projet.total_ttc)]
    ]

    if projet.maintenance_annuelle_ht > 0:
        total_data.insert(1, ["", "", "Maintenance annuelle HT :", format_currency(projet.maintenance_annuelle_ht)])

    total_table = Table(total_data, colWidths=[3.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
    ]))

    elements.append(total_table)

    # Générer le PDF
    doc.build(elements)

    # Retourner le contenu du buffer
    buffer.seek(0)
    return buffer.read()


def calculer_seuil_rentabilite(ca: float, charges_fixes: float, charges_variables: float) -> tuple:
    """Calcule le seuil de rentabilité et la marge de sécurité"""
    if ca <= 0:
        return float('inf'), -1

    taux_marge_variable = 1 - (charges_variables / ca)

    if taux_marge_variable <= 0.01:  # Éviter division par zéro
        return float('inf'), -1

    seuil = charges_fixes / taux_marge_variable
    marge_securite = (ca - seuil) / ca if ca > seuil else 0

    return seuil, marge_securite


def export_to_excel(df_resultats: pd.DataFrame, projet: Projet = None) -> bytes:
    """Exporte les résultats vers un fichier Excel"""
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Feuille de résultats financiers
        df_resultats.to_excel(writer, sheet_name='Résultats financiers', index=False)

        # Si un projet est fourni, ajouter le détail
        if projet:
            # Créer un DataFrame avec le détail des services
            services_data = []
            for service_sel in projet.services:
                services_data.append({
                    'Service': service_sel.service.nom,
                    'Catégorie': service_sel.service.categorie,
                    'Quantité': service_sel.quantite,
                    'Prix unitaire HT': service_sel.prix_unitaire,
                    'Total HT': service_sel.prix_total,
                    'Maintenance annuelle': service_sel.maintenance_annuelle
                })

            df_services = pd.DataFrame(services_data)
            df_services.to_excel(writer, sheet_name='Détail projet', index=False)

        # Obtenir le workbook et les worksheets
        workbook = writer.book

        # Format monétaire
        money_format = workbook.add_format({'num_format': '#,##0 €'})
        percent_format = workbook.add_format({'num_format': '0.0%'})

        # Appliquer les formats à la feuille de résultats
        worksheet = writer.sheets['Résultats financiers']
        worksheet.set_column('B:I', 15, money_format)
        worksheet.set_column('J:J', 12, percent_format)

    output.seek(0)
    return output.read()


def load_template_projet(template_key: str) -> Projet:
    """Charge un template de projet depuis le catalogue"""
    if template_key in st.session_state.templates_projets:
        return st.session_state.templates_projets[template_key].dupliquer()
    return None
