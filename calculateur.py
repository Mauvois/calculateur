import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Calculateur Financier - Datamap", layout="wide")
st.title("📊 Calculateur Financier - Datamap")
st.markdown("Estimez votre chiffre d'affaires, vos charges et votre résultat net en fonction de vos missions et de votre structure d'équipe.")

# Paramètres par défaut
TAUX_IS = 0.25  # Taux d'impôt sur les sociétés (25%)
TAUX_CHARGES_PATRONALES = 0.6  # 60% de charges patronales sur le salaire net

# Fonction pour calculer les résultats financiers
def calculer_resultats(annees, activite, rh, charges_fixes, taux_croissance=0.1):
    resultats = []

    # Activité initiale
    ca_initial = (
        activite["packagés"] * 4000 +
        activite["jours_conseil"] * 1000 +
        activite["formations"] * 2000 +
        activite["projets_sur_mesure"] * 20000 +
        activite["abonnements"] * 1000
    )

    # Charges de personnel initiales
    salaires_fondateurs = rh["nb_fondateurs"] * rh["salaire_net_fondateur"] * (1 + TAUX_CHARGES_PATRONALES) * 12
    salaires_autres = rh["nb_salaries"] * rh["salaire_chargé_salarié"] + rh["nb_alternants"] * rh["cout_alternant"]

    # Total des charges fixes
    total_charges_fixes = sum(charges_fixes.values())

    for annee in range(1, annees+1):
        # Application du taux de croissance
        ca = ca_initial * (1 + taux_croissance) ** (annee-1)

        # Évolution des salaires (hypothèse simplifiée)
        if annee > 1:
            salaires_fondateurs *= 1.02  # 2% d'augmentation annuelle
            salaires_autres *= (1 + taux_croissance)  # Augmentation liée à la croissance

        # Évolution des charges fixes
        charges_fixes_actuelles = total_charges_fixes * (1 + taux_croissance/2) ** (annee-1)

        # Calculs financiers
        total_charges = salaires_fondateurs + salaires_autres + charges_fixes_actuelles
        resultat_brut = ca - total_charges
        impot = max(0, resultat_brut * TAUX_IS)
        resultat_net = resultat_brut - impot

        resultats.append({
            "Année": annee,
            "CA": ca,
            "Salaires fondateurs": salaires_fondateurs,
            "Autres salaires": salaires_autres,
            "Charges fixes": charges_fixes_actuelles,
            "Total charges": total_charges,
            "Résultat brut": resultat_brut,
            "Impôt": impot,
            "Résultat net": resultat_net
        })

    return pd.DataFrame(resultats)

# Interface utilisateur
tabs = st.tabs(["Paramètres", "Résultats & Graphiques", "Scénarios prédéfinis"])

with tabs[0]:
    st.header("1. Activité prévue")
    col1, col2 = st.columns(2)

    # Création d'un dictionnaire pour stocker les valeurs d'activité
    activite = {}

    with col1:
        activite["packagés"] = st.number_input("Prestations packagées (4000 €)", 0, 20, 2,
                                              help="Audits, BDD spatiales, Dashboards...")
        activite["jours_conseil"] = st.slider("Jours de conseil (TJM 1000 €)", 0, 150, 40,
                                             help="Conseil et analyse avancée facturés en TJM")
        activite["formations"] = st.number_input("Formations (2000 €)", 0, 20, 2,
                                               help="Modules de formation et ateliers")

    with col2:
        activite["projets_sur_mesure"] = st.number_input("Projets sur mesure (20000 €)", 0, 10, 1,
                                                       help="Développements spécifiques")
        activite["abonnements"] = st.number_input("Clients avec abonnement (1000 €/an)", 0, 20, 3,
                                               help="Maintenance et support annuel")

    st.header("2. Ressources humaines")
    col1, col2 = st.columns(2)

    # Création d'un dictionnaire pour stocker les valeurs RH
    rh = {}

    with col1:
        rh["nb_fondateurs"] = st.number_input("Nombre de fondateurs actifs", 1, 5, 2)
        rh["salaire_net_fondateur"] = st.number_input("Salaire net/mois/fondateur (€)", 0, 10000, 2000)

    with col2:
        rh["nb_salaries"] = st.number_input("Nombre de salariés", 0, 10, 0)
        rh["salaire_chargé_salarié"] = st.number_input("Salaire brut chargé moyen salarié (€)", 20000, 60000, 36000)
        rh["nb_alternants"] = st.number_input("Nombre d'alternants", 0, 5, 0)
        rh["cout_alternant"] = st.number_input("Coût annuel moyen alternant (€)", 0, 20000, 12000)

    st.header("3. Charges fixes")
    col1, col2 = st.columns(2)

    # Création d'un dictionnaire pour stocker les charges fixes
    charges_fixes = {}

    with col1:
        charges_fixes["loyer"] = st.number_input("Loyer / Bureau / Charges (€)", 0, 20000, 4800)
        charges_fixes["logiciels"] = st.number_input("Logiciels / outils (€)", 0, 10000, 2000)
        charges_fixes["deplacements"] = st.number_input("Déplacements / événements (€)", 0, 10000, 2000)

    with col2:
        charges_fixes["materiel"] = st.number_input("Matériel / serveurs (€)", 0, 10000, 3000)
        charges_fixes["admin"] = st.number_input("Compta / Assurance / Admin (€)", 0, 10000, 3000)

    st.header("4. Projections")
    col1, col2 = st.columns(2)

    with col1:
        annees = st.slider("Nombre d'années de projection", 1, 5, 3)

    with col2:
        taux_croissance = st.slider("Taux de croissance annuel", 0.0, 0.5, 0.1, 0.05,
                                 format="%.0f%%", help="Impact sur le CA et les charges variables") * 1.0

with tabs[1]:
    # Calcul des résultats
    df_resultats = calculer_resultats(annees, activite, rh, charges_fixes, taux_croissance)

    # Affichage des KPIs pour la première année
    st.header("📊 Résultats financiers")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chiffre d'affaires (Année 1)", f"{df_resultats['CA'].iloc[0]:,.0f} €")
    with col2:
        st.metric("Total charges (Année 1)", f"{df_resultats['Total charges'].iloc[0]:,.0f} €")
    with col3:
        st.metric("Résultat net (Année 1)",
                f"{df_resultats['Résultat net'].iloc[0]:,.0f} €",
                delta=f"{df_resultats['Résultat net'].iloc[0]/df_resultats['CA'].iloc[0]:.1%}")

    # Tableau des résultats
    st.subheader("Tableau prévisionnel")
    df_affichage = df_resultats.copy()
    for col in df_affichage.columns:
        if col != "Année" and col != "Taux de marge":
            df_affichage[col] = df_affichage[col].map(lambda x: f"{x:,.0f} €")
    st.dataframe(df_affichage)

    # Graphiques
    st.subheader("Visualisations")
    col1, col2 = st.columns(2)

    with col1:
        # Graphique d'évolution du CA et résultat net
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(df_resultats["Année"], df_resultats["CA"], marker='o', linewidth=2, label="CA")
        ax1.plot(df_resultats["Année"], df_resultats["Résultat net"], marker='s', linewidth=2, label="Résultat net")
        ax1.set_xlabel("Année")
        ax1.set_ylabel("Montant (€)")
        ax1.set_title("Évolution du CA et du résultat net")
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        # Graphique de répartition des charges (Année 1) - CORRIGÉ
        resultat_net = df_resultats["Résultat net"].iloc[0]

        # Vérifier si les valeurs sont toutes non-négatives pour le graphique en camembert
        salaires_fondateurs = df_resultats["Salaires fondateurs"].iloc[0]
        autres_salaires = df_resultats["Autres salaires"].iloc[0]
        charges_fixes = df_resultats["Charges fixes"].iloc[0]
        impot = df_resultats["Impôt"].iloc[0]

        # Si le résultat net est positif, créer un camembert normal
        if resultat_net >= 0:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            labels = ["Salaires fondateurs", "Autres salaires", "Charges fixes", "Impôt", "Résultat net"]
            sizes = [salaires_fondateurs, autres_salaires, charges_fixes, impot, resultat_net]

            # Vérifier qu'il n'y a pas de valeurs négatives
            sizes = [max(0, size) for size in sizes]

            # Ne pas inclure les valeurs nulles
            non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
            labels = [labels[i] for i in non_zero_indices]
            sizes = [sizes[i] for i in non_zero_indices]

            if len(sizes) > 0:  # S'assurer qu'il y a des valeurs à afficher
                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax2.axis('equal')
                ax2.set_title("Répartition des charges et résultat (Année 1)")
                st.pyplot(fig2)
            else:
                st.warning("Pas de données positives à afficher dans le graphique de répartition.")
        else:
            # Alternative: graphique à barres pour montrer les valeurs négatives
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            labels = ["Salaires fondateurs", "Autres salaires", "Charges fixes", "Impôt", "Résultat net"]
            values = [salaires_fondateurs, autres_salaires, charges_fixes, impot, resultat_net]

            ax2.bar(labels, values, color=['#2196F3', '#4CAF50', '#FFC107', '#FF5722', '#9C27B0'])
            ax2.set_ylabel("Montant (€)")
            ax2.set_title("Répartition des charges et résultat (Année 1)")
            ax2.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig2)

    # Seuil de rentabilité
    st.subheader("Analyse du seuil de rentabilité (Année 1)")
    charges_fixes_totales = df_resultats["Charges fixes"].iloc[0]
    charges_variables = df_resultats["Salaires fondateurs"].iloc[0] + df_resultats["Autres salaires"].iloc[0]

    ca_annee1 = df_resultats["CA"].iloc[0]

    # Éviter la division par zéro
    if ca_annee1 > 0:
        # Éviter une division par zéro ou proche de zéro
        if abs(1 - charges_variables/ca_annee1) > 0.01:
            seuil_rentabilite = charges_fixes_totales / (1 - charges_variables/ca_annee1)
            marge_securite = (ca_annee1 - seuil_rentabilite)/ca_annee1
        else:
            seuil_rentabilite = float('inf')
            marge_securite = -1
    else:
        seuil_rentabilite = float('inf')
        marge_securite = -1

    col1, col2 = st.columns(2)
    with col1:
        if seuil_rentabilite != float('inf'):
            st.metric("Seuil de rentabilité", f"{seuil_rentabilite:,.0f} €")
        else:
            st.warning("Impossible de calculer le seuil de rentabilité (charges variables >= CA)")
    with col2:
        if marge_securite > -1:
            st.metric("Marge de sécurité", f"{marge_securite:.1%}")
        else:
            st.warning("Impossible de calculer la marge de sécurité")

with tabs[2]:
    st.header("Scénarios prédéfinis")

    # Définition des scénarios
    scenarios = {
        "Croissance modeste": {
            "description": "Évolution prudente avec maintien des coûts bas",
            "taux": 0.05,
            "ca_annee1": 54000
        },
        "Croissance intéressante": {
            "description": "Développement progressif avec embauches",
            "taux": 0.15,
            "ca_annee1": 72000
        },
        "Croissance forte": {
            "description": "Expansion rapide et recrutement intensif",
            "taux": 0.30,
            "ca_annee1": 120000
        }
    }

    # Affichage des scénarios
    scenario_choisi = st.selectbox("Choisir un scénario", list(scenarios.keys()))

    st.markdown(f"**Description:** {scenarios[scenario_choisi]['description']}")
    st.markdown(f"**Taux de croissance:** {scenarios[scenario_choisi]['taux']:.0%}")

    # Création du DataFrame avec les 3 scénarios
    data_scenarios = []

    for nom_scenario, details in scenarios.items():
        # Calcul simplifié des résultats pour chaque année
        for annee in range(1, 4):
            ca = details["ca_annee1"] * (1 + details["taux"]) ** (annee-1)

            # Valeurs approximatives basées sur les tableaux de référence
            if nom_scenario == "Croissance modeste":
                salaires_fondateurs = 36000 * (1 + 0.05) ** (annee-1)
                autres_salaires = 0
                charges = 8500 * (1 + 0.05) ** (annee-1)
            elif nom_scenario == "Croissance intéressante":
                salaires_fondateurs = 48000 * (1 + 0.02) ** (annee-1)
                autres_salaires = 0 if annee == 1 else (15000 if annee == 2 else 30000)
                charges = 11000 * (1 + 0.10) ** (annee-1)
            else:  # Croissance forte
                salaires_fondateurs = 72000
                autres_salaires = 0 if annee == 1 else (36000 if annee == 2 else 70000)
                charges = 15000 * (1 + 0.15) ** (annee-1)

            total_charges = salaires_fondateurs + autres_salaires + charges
            resultat = ca - total_charges

            data_scenarios.append({
                "Scénario": nom_scenario,
                "Année": annee,
                "CA": ca,
                "Charges totales": total_charges,
                "Résultat": resultat
            })

    df_scenarios = pd.DataFrame(data_scenarios)

    # Graphique comparatif des scénarios
    fig, ax = plt.subplots(figsize=(12, 6))

    for scenario in scenarios.keys():
        df_temp = df_scenarios[df_scenarios["Scénario"] == scenario]
        ax.plot(df_temp["Année"], df_temp["CA"], marker='o', linewidth=2, label=f"CA - {scenario}")
        ax.plot(df_temp["Année"], df_temp["Résultat"], marker='s', linestyle='--', linewidth=2, label=f"Résultat - {scenario}")

    ax.set_xlabel("Année")
    ax.set_ylabel("Montant (€)")
    ax.set_title("Comparaison des scénarios de croissance")
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

    st.pyplot(fig)

    # Tableau des scénarios
    st.subheader("Détails des scénarios")
    st.dataframe(df_scenarios)
