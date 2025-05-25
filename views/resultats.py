# views/resultats.py
"""Module pour l'onglet de résultats et analyses - Version SAS adaptée"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from config import OBJECTIFS_REMUNERATION, GRAPH_CONFIG
from utils import (
    format_currency, format_percentage,
    creer_graphique_ca_evolution, creer_graphique_repartition,
    calculer_seuil_rentabilite
)


def render_resultats_tab():
    """Affiche l'onglet des résultats et analyses adapté SAS"""
    st.header("📊 Résultats & Analyses - SAS Caribo")

    # Vérifier qu'il y a des prévisions
    if ('previsions_annuelles' not in st.session_state or
        not st.session_state.previsions_annuelles.annees):
        st.info("Aucune prévision générée. Allez dans l'onglet 'Prévisions annuelles' pour créer vos prévisions.")
        return

    # Récupérer les données
    df_resultats = st.session_state.previsions_annuelles.get_dataframe_resultats()

    # === SECTION SAS : ANALYSE DE LA RÉMUNÉRATION ===
    st.subheader("💰 Analyse de la rémunération SAS")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Objectifs de rémunération :**")
        st.write(f"• Dividendes nets par associé : {format_currency(OBJECTIFS_REMUNERATION['dividendes_nets_par_associe'])}")
        st.write(f"• Total dividendes nets (2 associés) : {format_currency(OBJECTIFS_REMUNERATION['total_dividendes_nets'])}")
        st.write(f"• Dividendes bruts nécessaires : {format_currency(OBJECTIFS_REMUNERATION['dividendes_bruts_necessaires'])}")
        st.write(f"• Bénéfice avant IS requis : {format_currency(OBJECTIFS_REMUNERATION['benefice_avant_is_necessaire'])}")

    with col2:
        # Vérification objectifs par année
        st.write("**Atteinte des objectifs par année :**")
        for _, row in df_resultats.iterrows():
            annee = int(row["Année"])
            benefice_brut = row["Résultat brut"]

            if benefice_brut >= OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]:
                st.success(f"Année {annee} : ✅ Objectif atteint ({format_currency(benefice_brut)})")
            else:
                manque = OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"] - benefice_brut
                st.warning(f"Année {annee} : ⚠️ Manque {format_currency(manque)}")

    # Calcul détaillé de la rémunération possible
    st.write("**Rémunération réalisable par année :**")

    remuneration_data = []
    for _, row in df_resultats.iterrows():
        annee = int(row["Année"])
        benefice_brut = row["Résultat brut"]

        # Calcul IS (25%)
        is_du = max(0, benefice_brut * 0.25)
        benefice_apres_is = benefice_brut - is_du

        # Calcul dividendes possibles (flat tax 30%)
        dividendes_nets_possible = benefice_apres_is * 0.70  # 70% après flat tax
        dividendes_nets_par_associe = dividendes_nets_possible / 2

        remuneration_data.append({
            "Année": annee,
            "Bénéfice brut": benefice_brut,
            "IS (25%)": is_du,
            "Bénéfice après IS": benefice_apres_is,
            "Dividendes nets possibles": dividendes_nets_possible,
            "Net par associé": dividendes_nets_par_associe
        })

    df_remuneration = pd.DataFrame(remuneration_data)

    # Formater pour affichage
    df_remuneration_display = df_remuneration.copy()
    for col in df_remuneration_display.columns:
        if col != "Année":
            df_remuneration_display[col] = df_remuneration_display[col].apply(lambda x: format_currency(x))

    st.dataframe(df_remuneration_display, use_container_width=True, hide_index=True)

    st.divider()

    # === KPIs PRINCIPAUX ===
    st.subheader("🎯 Indicateurs clés")

    annee_1 = df_resultats.iloc[0]
    derniere_annee = df_resultats.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "CA Année 1",
            format_currency(annee_1["CA Total"]),
            help="Chiffre d'affaires total de la première année"
        )

    with col2:
        benefice_annee_1 = remuneration_data[0]["Bénéfice brut"]
        objectif_atteint = benefice_annee_1 >= OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]
        delta_objectif = benefice_annee_1 - OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]

        st.metric(
            "Bénéfice Année 1",
            format_currency(benefice_annee_1),
            delta=format_currency(delta_objectif),
            delta_color="normal" if objectif_atteint else "inverse",
            help="Bénéfice brut avant IS"
        )

    with col3:
        net_par_associe_annee_1 = remuneration_data[0]["Net par associé"]
        delta_net = net_par_associe_annee_1 - OBJECTIFS_REMUNERATION["dividendes_nets_par_associe"]

        st.metric(
            "Net par associé An1",
            format_currency(net_par_associe_annee_1),
            delta=format_currency(delta_net),
            delta_color="normal" if delta_net >= 0 else "inverse",
            help="Dividendes nets possibles par associé"
        )

    with col4:
        if len(df_resultats) > 1:
            croissance_totale = (derniere_annee["CA Total"] / annee_1["CA Total"]) - 1
            st.metric(
                f"Croissance {len(df_resultats)} ans",
                format_percentage(croissance_totale),
                help="Croissance totale du CA"
            )
        else:
            st.metric("Nb projets", len(st.session_state.projets_annee_1))

    # Tableau détaillé
    st.divider()
    st.subheader("📋 Tableau détaillé des prévisions")

    # Formater le DataFrame pour l'affichage
    df_affichage = df_resultats.copy()

    # Colonnes monétaires
    colonnes_monetaires = ["CA Projets", "CA Maintenance", "CA Total", "Charges fixes",
                          "Résultat brut", "Impôt", "Résultat net"]
    for col in colonnes_monetaires:
        df_affichage[col] = df_affichage[col].apply(lambda x: format_currency(x))

    # Taux de marge
    df_affichage["Taux de marge"] = df_affichage["Taux de marge"].apply(lambda x: format_percentage(x))

    # Afficher avec style
    st.dataframe(
        df_affichage,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Année": st.column_config.NumberColumn("Année", format="%d"),
            "CA Total": st.column_config.TextColumn("CA Total", help="Chiffre d'affaires total"),
            "Taux de marge": st.column_config.TextColumn("Marge nette", help="Résultat net / CA")
        }
    )

    # === GRAPHIQUES ===
    st.divider()
    st.subheader("📈 Visualisations")

    # Sélection du type de graphique
    type_graphique = st.selectbox(
        "Type de graphique",
        ["Évolution CA et Bénéfice", "Analyse rémunération SAS", "Capacité vs Objectifs", "Ratios financiers"]
    )

    if type_graphique == "Évolution CA et Bénéfice":
        fig = creer_graphique_ca_evolution(df_resultats)
        st.pyplot(fig)

        # Commentaire automatique
        if df_resultats["Résultat net"].iloc[-1] > df_resultats["Résultat net"].iloc[0]:
            st.success("✅ Progression positive du résultat net sur la période")
        else:
            st.warning("⚠️ Attention, le résultat net n'augmente pas sur la période")

    elif type_graphique == "Analyse rémunération SAS":
        # Graphique spécifique à la rémunération SAS
        fig, ax = plt.subplots(figsize=GRAPH_CONFIG['figsize'])

        annees = [r["Année"] for r in remuneration_data]
        benefices_bruts = [r["Bénéfice brut"] for r in remuneration_data]
        nets_par_associe = [r["Net par associé"] for r in remuneration_data]

        # Ligne objectif
        objectif_line = [OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"]] * len(annees)
        objectif_net_line = [OBJECTIFS_REMUNERATION["dividendes_nets_par_associe"]] * len(annees)

        ax.plot(annees, benefices_bruts, marker='o', linewidth=2,
                label="Bénéfice brut", color=GRAPH_CONFIG['colors'][0])
        ax.plot(annees, objectif_line, '--',
                label=f"Objectif bénéfice ({format_currency(OBJECTIFS_REMUNERATION['benefice_avant_is_necessaire'])})",
                color=GRAPH_CONFIG['colors'][3])

        # Axe secondaire pour net par associé
        ax2 = ax.twinx()
        ax2.plot(annees, nets_par_associe, marker='s', linewidth=2,
                 label="Net par associé", color=GRAPH_CONFIG['colors'][1])
        ax2.plot(annees, objectif_net_line, '--',
                 label=f"Objectif net ({format_currency(OBJECTIFS_REMUNERATION['dividendes_nets_par_associe'])})",
                 color=GRAPH_CONFIG['colors'][4])

        # Mise en forme
        ax.set_xlabel("Année")
        ax.set_ylabel("Bénéfice brut (€)")
        ax2.set_ylabel("Net par associé (€)")
        ax.set_title("Analyse de la rémunération SAS")
        ax.grid(True, linestyle='--', alpha=0.7)

        # Légendes combinées
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Formatage des axes
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k€"))
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k€"))

        plt.tight_layout()
        st.pyplot(fig)

    elif type_graphique == "Capacité vs Objectifs":
        # Analyse de la capacité de l'entreprise
        fig, ax = plt.subplots(figsize=GRAPH_CONFIG['figsize'])

        # Données de capacité théorique vs réalité
        annees = df_resultats["Année"].tolist()
        ca_reel = df_resultats["CA Total"].tolist()

        # Capacité théorique basée sur la croissance
        ca_objectif = []
        for i, annee in enumerate(annees):
            if i == 0:
                ca_objectif.append(ca_reel[0])
            else:
                # Supposer une croissance régulière
                croissance_moy = 0.12  # 12% par défaut
                ca_objectif.append(ca_objectif[0] * (1 + croissance_moy) ** (i))

        ax.bar([f"An{int(a)}" for a in annees], ca_reel,
               label='CA réalisé', color=GRAPH_CONFIG['colors'][0], alpha=0.8)
        ax.plot([f"An{int(a)}" for a in annees], ca_objectif,
                marker='o', linewidth=2, color=GRAPH_CONFIG['colors'][2],
                label='Tendance objectif')

        # Ligne objectif minimum
        ca_min_objectif = [OBJECTIFS_REMUNERATION["benefice_avant_is_necessaire"] + 15000] * len(annees)  # +15k charges
        ax.axhline(y=ca_min_objectif[0], color=GRAPH_CONFIG['colors'][3],
                   linestyle='--', label=f'CA minimum pour objectif')
