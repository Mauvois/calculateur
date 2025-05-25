# views/resultats.py
"""Module pour l'onglet de résultats et analyses"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils import (
    format_currency, format_percentage,
    creer_graphique_ca_evolution, creer_graphique_repartition,
    calculer_seuil_rentabilite
)
from config import GRAPH_CONFIG


def render_resultats_tab():
    """Affiche l'onglet des résultats et analyses"""
    st.header("📊 Résultats & Analyses")

    # Vérifier qu'il y a des prévisions
    if ('previsions_annuelles' not in st.session_state or
        not st.session_state.previsions_annuelles.annees):
        st.info("Aucune prévision générée. Allez dans l'onglet 'Prévisions annuelles' pour créer vos prévisions.")
        return

    # Récupérer les données
    df_resultats = st.session_state.previsions_annuelles.get_dataframe_resultats()

    # KPIs principaux
    st.subheader("🎯 Indicateurs clés")

    # Métriques de l'année 1
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
        st.metric(
            "Résultat net Année 1",
            format_currency(annee_1["Résultat net"]),
            delta=format_percentage(annee_1["Taux de marge"]),
            help="Résultat net après impôts"
        )

    with col3:
        ca_moyen = df_resultats["CA Total"].mean()
        st.metric(
            "CA moyen",
            format_currency(ca_moyen),
            help=f"Moyenne sur {len(df_resultats)} ans"
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

    # Graphiques
    st.divider()
    st.subheader("📈 Visualisations")

    # Sélection du type de graphique
    type_graphique = st.selectbox(
        "Type de graphique",
        ["Évolution CA et Résultat", "Répartition année 1", "Analyse comparative", "Ratios financiers"]
    )

    if type_graphique == "Évolution CA et Résultat":
        fig = creer_graphique_ca_evolution(df_resultats)
        st.pyplot(fig)

        # Commentaire automatique
        if df_resultats["Résultat net"].iloc[-1] > df_resultats["Résultat net"].iloc[0]:
            st.success("✅ Progression positive du résultat net sur la période")
        else:
            st.warning("⚠️ Attention, le résultat net n'augmente pas sur la période")

    elif type_graphique == "Répartition année 1":
        fig = creer_graphique_repartition(df_resultats, annee=1)
        st.pyplot(fig)

    elif type_graphique == "Analyse comparative":
        # Graphique comparatif des années
        fig, ax = plt.subplots(figsize=GRAPH_CONFIG['figsize'])

        annees = df_resultats["Année"].tolist()
        x = range(len(annees))
        width = 0.35

        # Barres pour CA et charges
        ca_bars = ax.bar([i - width/2 for i in x], df_resultats["CA Total"],
                         width, label='CA Total', color=GRAPH_CONFIG['colors'][0])
        charges_bars = ax.bar([i + width/2 for i in x], df_resultats["Charges fixes"],
                              width, label='Charges fixes', color=GRAPH_CONFIG['colors'][3])

        # Ligne pour le résultat net
        ax2 = ax.twinx()
        resultat_line = ax2.plot(x, df_resultats["Résultat net"],
                                color=GRAPH_CONFIG['colors'][2], marker='o',
                                linewidth=2, label='Résultat net')

        # Mise en forme
        ax.set_xlabel('Année')
        ax.set_ylabel('CA et Charges (€)')
        ax2.set_ylabel('Résultat net (€)')
        ax.set_title('Analyse comparative par année')
        ax.set_xticks(x)
        ax.set_xticklabels(annees)

        # Légendes combinées
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')

        # Formatage des axes
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k€"))
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/1000:.0f}k€"))

        plt.tight_layout()
        st.pyplot(fig)

    else:  # Ratios financiers
        # Calculer les ratios
        ratios_data = []
        for _, row in df_resultats.iterrows():
            ratios_data.append({
                "Année": int(row["Année"]),
                "Marge nette (%)": row["Taux de marge"] * 100,
                "Charges / CA (%)": (row["Charges fixes"] / row["CA Total"] * 100) if row["CA Total"] > 0 else 0,
                "Rentabilité (%)": (row["Résultat net"] / row["CA Total"] * 100) if row["CA Total"] > 0 else 0
            })

        df_ratios = pd.DataFrame(ratios_data)

        # Graphique des ratios
        fig, ax = plt.subplots(figsize=GRAPH_CONFIG['figsize'])

        for col in ["Marge nette (%)", "Charges / CA (%)", "Rentabilité (%)"]:
            ax.plot(df_ratios["Année"], df_ratios[col], marker='o', linewidth=2, label=col)

        ax.set_xlabel("Année")
        ax.set_ylabel("Pourcentage (%)")
        ax.set_title("Évolution des ratios financiers")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

        plt.tight_layout()
        st.pyplot(fig)

    # Analyse du seuil de rentabilité
    st.divider()
    st.subheader("💡 Analyse du seuil de rentabilité")

    annee_analyse = st.selectbox("Année à analyser", df_resultats["Année"].tolist())
    donnees_annee = df_resultats[df_resultats["Année"] == annee_analyse].iloc[0]

    # Pour simplifier, on considère que toutes les charges sont fixes
    seuil, marge_securite = calculer_seuil_rentabilite(
        donnees_annee["CA Total"],
        donnees_annee["Charges fixes"],
        0  # Pas de charges variables dans ce modèle simplifié
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if seuil != float('inf'):
            st.metric("Seuil de rentabilité", format_currency(seuil))
        else:
            st.metric("Seuil de rentabilité", "N/A")

    with col2:
        if marge_securite >= 0:
            st.metric("Marge de sécurité", format_percentage(marge_securite))
        else:
            st.metric("Marge de sécurité", "N/A")

    with col3:
        # Point mort en nombre de projets
        if len(st.session_state.projets_annee_1) > 0:
            ca_moyen_projet = donnees_annee["CA Projets"] / len(st.session_state.projets_annee_1)
            if ca_moyen_projet > 0:
                point_mort_projets = int(seuil / ca_moyen_projet) + 1
                st.metric("Point mort", f"{point_mort_projets} projets")

    # Insights et recommandations
    st.divider()
    st.subheader("🎓 Insights et recommandations")

    # Analyse automatique
    insights = []

    # Croissance
    if len(df_resultats) > 1:
        taux_croissance_moyen = ((derniere_annee["CA Total"] / annee_1["CA Total"]) ** (1/(len(df_resultats)-1))) - 1
        insights.append(f"📈 Taux de croissance annuel moyen : {format_percentage(taux_croissance_moyen)}")

    # Rentabilité
    marge_moyenne = df_resultats["Taux de marge"].mean()
    if marge_moyenne > 0.2:
        insights.append("✅ Excellente rentabilité moyenne (>20%)")
    elif marge_moyenne > 0.1:
        insights.append("👍 Bonne rentabilité moyenne (>10%)")
    else:
        insights.append("⚠️ Rentabilité à améliorer (<10%)")

    # Charges
    ratio_charges_moyen = (df_resultats["Charges fixes"] / df_resultats["CA Total"]).mean()
    if ratio_charges_moyen < 0.3:
        insights.append("✅ Charges fixes bien maîtrisées (<30% du CA)")
    elif ratio_charges_moyen < 0.5:
        insights.append("👍 Charges fixes raisonnables (<50% du CA)")
    else:
        insights.append("⚠️ Charges fixes élevées (>50% du CA)")

    # Projets
    nb_projets = len(st.session_state.projets_annee_1)
    ca_moyen_projet = annee_1["CA Projets"] / nb_projets if nb_projets > 0 else 0
    insights.append(f"📊 CA moyen par projet : {format_currency(ca_moyen_projet)}")

    # Services avec maintenance
    projets_avec_maintenance = sum(1 for p in st.session_state.projets_annee_1
                                  if p.maintenance_annuelle_ht > 0)
    if projets_avec_maintenance > 0:
        ratio_maintenance = annee_1["CA Maintenance"] / annee_1["CA Total"]
        insights.append(f"🔧 Revenus récurrents (maintenance) : {format_percentage(ratio_maintenance)} du CA")

    # Afficher les insights
    for insight in insights:
        st.write(insight)

    # Recommandations
    st.write("\n**Recommandations :**")

    if marge_moyenne < 0.15:
        st.write("- 💡 Augmenter les prix ou réduire les charges pour améliorer la rentabilité")

    if ratio_charges_moyen > 0.4:
        st.write("- 💡 Optimiser les charges fixes (négociation loyers, mutualisation...)")

    if projets_avec_maintenance < nb_projets * 0.3:
        st.write("- 💡 Développer plus de projets avec maintenance pour des revenus récurrents")

    if nb_projets < 20:
        st.write("- 💡 Diversifier la base clients pour réduire les risques")
