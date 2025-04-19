import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Calculateur Financier - Datamap", layout="wide")
st.title("📊 Calculateur Financier - Datamap")
st.markdown("Estimez votre chiffre d'affaires, vos charges et votre résultat net en fonction de vos missions et de votre structure d'équipe.")

# Initialisation de session_state pour la persistence des données
if 'initialized' not in st.session_state:
    # Constantes
    st.session_state.TAUX_IS = 0.25  # Taux d'impôt sur les sociétés (25%)
    st.session_state.TAUX_CHARGES_PATRONALES = 0.6  # 60% de charges patronales sur le salaire net

    # Catalogue de services
    st.session_state.SERVICES = {
        "audit_sig": {"label": "Audit SIG", "prix_unitaire": 3500, "min": 0, "max": 10, "step": 1},
        "bdd_spatiale": {"label": "BDD Spatiale", "prix_unitaire": 5000, "min": 0, "max": 10, "step": 1},
        "dashboard": {"label": "Dashboard", "prix_unitaire": 4000, "min": 0, "max": 10, "step": 1},
        "jours_conseil": {"label": "Jours de conseil (TJM 1100 €)", "prix_unitaire": 1100, "min": 0, "max": 200, "step": 1},
        "formations": {"label": "Formations", "prix_unitaire": 2000, "min": 0, "max": 20, "step": 1},
        "projets_sur_mesure": {"label": "Projets sur mesure", "prix_unitaire": 20000, "min": 0, "max": 10, "step": 1},
    }

    # Définition des scénarios
    st.session_state.SCENARIOS = {
        "Croissance modeste": {
            "description": "Évolution prudente avec maintien des coûts bas",
            "taux_croissance": 0.05,
            "ratio_salaires_ca": 0.67,  # 67% du CA pour les salaires fondateurs
            "charges_fixes_initiales": 8500,
            "taux_inflation_charges": 0.02,
        },
        "Croissance intéressante": {
            "description": "Développement progressif avec embauches",
            "taux_croissance": 0.15,
            "ratio_salaires_ca": 0.67,  # 67% du CA pour les salaires fondateurs
            "charges_fixes_initiales": 11000,
            "taux_inflation_charges": 0.05,
        },
        "Croissance forte": {
            "description": "Expansion rapide et recrutement intensif",
            "taux_croissance": 0.30,
            "ratio_salaires_ca": 0.60,  # 60% du CA pour les salaires fondateurs
            "charges_fixes_initiales": 15000,
            "taux_inflation_charges": 0.10,
        }
    }

    # Données par défaut
    st.session_state.activite = {service: 0 for service in st.session_state.SERVICES}
    st.session_state.activite["jours_conseil"] = 40
    st.session_state.activite["audit_sig"] = 2
    st.session_state.activite["projets_sur_mesure"] = 1
    st.session_state.activite["formations"] = 2

    st.session_state.rh = {
        "nb_fondateurs": 2,
        "salaire_net_fondateur": 2000,
        "nb_salaries": 0,
        "salaire_chargé_salarié": 36000,
        "nb_alternants": 0,
        "cout_alternant": 12000
    }

    st.session_state.charges_fixes = {
        "loyer": 4800,
        "logiciels": 2000,
        "deplacements": 2000,
        "materiel": 3000,
        "admin": 3000
    }

    st.session_state.projection = {
        "annees": 3,
        "taux_croissance": 0.10,
        "scenario_actif": "Personnalisé"
    }

    st.session_state.initialized = True

# Fonction pour calculer les résultats financiers
def calculer_resultats(activites, rh, charges_fixes, projection):
    resultats = []
    annees = projection["annees"]
    taux_croissance = projection["taux_croissance"]

    # Calcul du CA initial
    ca_initial = 0
    for service, quantite in activites.items():
        prix_unitaire = st.session_state.SERVICES[service]["prix_unitaire"]
        ca_initial += quantite * prix_unitaire

    # Abonnements de maintenance (15-20% des projets)
    valeur_projets = activites["projets_sur_mesure"] * st.session_state.SERVICES["projets_sur_mesure"]["prix_unitaire"]
    maintenance_initiale = valeur_projets * 0.15  # 15% du coût des projets
    ca_initial += maintenance_initiale

    # Charges de personnel initiales
    salaires_fondateurs_base = rh["nb_fondateurs"] * rh["salaire_net_fondateur"] * (1 + st.session_state.TAUX_CHARGES_PATRONALES) * 12
    salaires_autres_base = rh["nb_salaries"] * rh["salaire_chargé_salarié"] + rh["nb_alternants"] * rh["cout_alternant"]

    # Total des charges fixes
    total_charges_fixes_base = sum(charges_fixes.values())

    for annee in range(1, annees+1):
        # Application du taux de croissance au CA
        ca = ca_initial * (1 + taux_croissance) ** (annee-1)

        # Évolution des salaires
        salaires_fondateurs = salaires_fondateurs_base * (1 + 0.02) ** (annee-1)  # 2% d'inflation sur salaires

        # Pour les autres salaires, on suit une logique d'embauche progressive
        if annee == 1:
            salaires_autres = salaires_autres_base
        else:
            # Embauche progressive - hypothèse d'une équipe qui grandit avec le CA
            # Au-delà de 100k€ de CA, on ajoute 1 salarié par tranches de 50k€ supplémentaires
            salaries_theoriques = max(0, int((ca - 100000) / 50000))
            salaires_autres = salaries_theoriques * rh["salaire_chargé_salarié"]

        # Évolution des charges fixes: on sépare l'inflation des coûts fixes
        # - Loyer: indexé sur l'inflation (2%)
        # - Logiciels, matériel: indexé sur la croissance
        charges_fixes_inflations = charges_fixes["loyer"] * (1 + 0.02) ** (annee-1)
        charges_fixes_variables = (total_charges_fixes_base - charges_fixes["loyer"]) * (1 + taux_croissance/2) ** (annee-1)
        charges_fixes_actuelles = charges_fixes_inflations + charges_fixes_variables

        # Calculs financiers
        total_charges = salaires_fondateurs + salaires_autres + charges_fixes_actuelles
        resultat_brut = ca - total_charges
        impot = max(0, resultat_brut * st.session_state.TAUX_IS)
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
            "Résultat net": resultat_net,
            "Taux de marge": resultat_net / ca if ca > 0 else 0
        })

    return pd.DataFrame(resultats)

# Fonction pour appliquer un scénario
def appliquer_scenario(nom_scenario):
    if nom_scenario != "Personnalisé" and nom_scenario in st.session_state.SCENARIOS:
        scenario = st.session_state.SCENARIOS[nom_scenario]

        # Mise à jour du taux de croissance
        st.session_state.projection["taux_croissance"] = scenario["taux_croissance"]

        # Ajustement des activités selon le scénario
        ca_cible = 0
        if nom_scenario == "Croissance modeste":
            ca_cible = 54000
        elif nom_scenario == "Croissance intéressante":
            ca_cible = 72000
        elif nom_scenario == "Croissance forte":
            ca_cible = 120000

        # On garde la même répartition entre les services mais on ajuste le volume
        ca_actuel = sum(st.session_state.activite[service] * st.session_state.SERVICES[service]["prix_unitaire"]
                       for service in st.session_state.activite)

        if ca_actuel > 0:
            ratio = ca_cible / ca_actuel
            for service in st.session_state.activite:
                st.session_state.activite[service] = round(st.session_state.activite[service] * ratio)

        # Mise à jour des salaires fondateurs en fonction du ratio du scénario
        salaire_mensuel = ca_cible * scenario["ratio_salaires_ca"] / (12 * st.session_state.rh["nb_fondateurs"] * (1 + st.session_state.TAUX_CHARGES_PATRONALES))
        st.session_state.rh["salaire_net_fondateur"] = round(salaire_mensuel / 100) * 100  # Arrondi au 100€ près

        # Mise à jour des charges fixes
        total_charges_fixes = scenario["charges_fixes_initiales"]
        facteur_repartition = total_charges_fixes / sum(st.session_state.charges_fixes.values())

        for charge in st.session_state.charges_fixes:
            st.session_state.charges_fixes[charge] = round(st.session_state.charges_fixes[charge] * facteur_repartition)

    st.session_state.projection["scenario_actif"] = nom_scenario

# Interface utilisateur
tabs = st.tabs(["Paramètres", "Résultats & Graphiques", "Scénarios"])

# Onglet Paramètres
with tabs[0]:
    st.header("1. Activité prévue")

    # Choix du scénario (en haut pour pouvoir initialiser les données)
    st.subheader("Choisir un scénario de base")
    scenarios_list = ["Personnalisé"] + list(st.session_state.SCENARIOS.keys())
    scenario_choisi = st.selectbox(
        "Scénario",
        scenarios_list,
        index=scenarios_list.index(st.session_state.projection["scenario_actif"])
    )

    # Appliquer le scénario si changé
    if scenario_choisi != st.session_state.projection["scenario_actif"]:
        appliquer_scenario(scenario_choisi)

    col1, col2 = st.columns(2)

    with col1:
        for service in ["audit_sig", "bdd_spatiale", "dashboard"]:
            info = st.session_state.SERVICES[service]
            st.session_state.activite[service] = st.number_input(
                f"{info['label']} ({info['prix_unitaire']} €)",
                min_value=info["min"],
                max_value=info["max"],
                value=st.session_state.activite[service],
                step=info["step"],
                help=f"Prix unitaire: {info['prix_unitaire']} €"
            )

    with col2:
        for service in ["jours_conseil", "formations", "projets_sur_mesure"]:
            info = st.session_state.SERVICES[service]
            st.session_state.activite[service] = st.number_input(
                f"{info['label']} ({info['prix_unitaire']} €)",
                min_value=info["min"],
                max_value=info["max"],
                value=st.session_state.activite[service],
                step=info["step"],
                help=f"Prix unitaire: {info['prix_unitaire']} €"
            )

    # Calcul et affichage du CA prévisionnel
    ca_previsionnel = sum(st.session_state.activite[service] * st.session_state.SERVICES[service]["prix_unitaire"]
                       for service in st.session_state.activite)

    # Maintenance (15% des projets sur mesure)
    valeur_projets = st.session_state.activite["projets_sur_mesure"] * st.session_state.SERVICES["projets_sur_mesure"]["prix_unitaire"]
    maintenance = valeur_projets * 0.15

    ca_previsionnel += maintenance

    st.info(f"**CA prévisionnel année 1: {ca_previsionnel:,.0f} €** (dont maintenance: {maintenance:,.0f} €)")

    st.header("2. Ressources humaines")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.rh["nb_fondateurs"] = st.number_input(
            "Nombre de fondateurs actifs",
            min_value=1,
            max_value=5,
            value=st.session_state.rh["nb_fondateurs"]
        )

        st.session_state.rh["salaire_net_fondateur"] = st.number_input(
            "Salaire net/mois/fondateur (€)",
            min_value=0,
            max_value=10000,
            value=st.session_state.rh["salaire_net_fondateur"],
            step=100,
            help=f"Coût annuel chargé: {st.session_state.rh['salaire_net_fondateur'] * (1 + st.session_state.TAUX_CHARGES_PATRONALES) * 12:,.0f} €"
        )

    with col2:
        st.session_state.rh["nb_salaries"] = st.number_input(
            "Nombre de salariés",
            min_value=0,
            max_value=10,
            value=st.session_state.rh["nb_salaries"]
        )

        st.session_state.rh["salaire_chargé_salarié"] = st.number_input(
            "Salaire brut chargé annuel/salarié (€)",
            min_value=20000,
            max_value=80000,
            value=st.session_state.rh["salaire_chargé_salarié"],
            step=1000
        )

        st.session_state.rh["nb_alternants"] = st.number_input(
            "Nombre d'alternants",
            min_value=0,
            max_value=5,
            value=st.session_state.rh["nb_alternants"]
        )

        st.session_state.rh["cout_alternant"] = st.number_input(
            "Coût annuel moyen alternant (€)",
            min_value=0,
            max_value=20000,
            value=st.session_state.rh["cout_alternant"],
            step=500
        )

    st.header("3. Charges fixes")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.charges_fixes["loyer"] = st.number_input(
            "Loyer / Bureau / Charges (€)",
            min_value=0,
            max_value=30000,
            value=st.session_state.charges_fixes["loyer"],
            step=100,
            help="Indexé sur l'inflation (2%)"
        )

        st.session_state.charges_fixes["logiciels"] = st.number_input(
            "Logiciels / outils (€)",
            min_value=0,
            max_value=15000,
            value=st.session_state.charges_fixes["logiciels"],
            step=100,
            help="Indexé sur le taux de croissance"
        )

        st.session_state.charges_fixes["deplacements"] = st.number_input(
            "Déplacements / événements (€)",
            min_value=0,
            max_value=15000,
            value=st.session_state.charges_fixes["deplacements"],
            step=100,
            help="Indexé sur le taux de croissance"
        )

    with col2:
        st.session_state.charges_fixes["materiel"] = st.number_input(
            "Matériel / serveurs (€)",
            min_value=0,
            max_value=15000,
            value=st.session_state.charges_fixes["materiel"],
            step=100,
            help="Indexé sur le taux de croissance"
        )

        st.session_state.charges_fixes["admin"] = st.number_input(
            "Compta / Assurance / Admin (€)",
            min_value=0,
            max_value=15000,
            value=st.session_state.charges_fixes["admin"],
            step=100,
            help="Indexé sur le taux de croissance"
        )

    st.info(f"**Total charges fixes annuelles: {sum(st.session_state.charges_fixes.values()):,.0f} €**")

    st.header("4. Projections")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.projection["annees"] = st.slider(
            "Nombre d'années de projection",
            min_value=1,
            max_value=5,
            value=st.session_state.projection["annees"]
        )

    with col2:
        st.session_state.projection["taux_croissance"] = st.slider(
            "Taux de croissance annuel",
            min_value=0.0,
            max_value=0.5,
            value=st.session_state.projection["taux_croissance"],
            step=0.05,
            format="%d %%",
            help="Impact sur le CA et les charges variables"
        )

    # Informations sur les constantes
    st.header("Informations complémentaires")
    st.markdown(f"""
    - Taux d'impôt sur les sociétés: **{st.session_state.TAUX_IS*100:.0f}%**
    - Taux de charges patronales: **{st.session_state.TAUX_CHARGES_PATRONALES*100:.0f}%**
    - Maintenance annuelle: **15%** du coût des projets sur mesure
    - Inflation annuelle des loyers: **2%**
    - Augmentation annuelle des salaires fondateurs: **2%**
    """)

# Onglet Résultats
with tabs[1]:
    # Calcul des résultats avec les paramètres actuels
    df_resultats = calculer_resultats(
        st.session_state.activite,
        st.session_state.rh,
        st.session_state.charges_fixes,
        st.session_state.projection
    )

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
    # Formater les colonnes monétaires
    for col in df_affichage.columns:
        if col not in ["Année", "Taux de marge"]:
            df_affichage[col] = df_affichage[col].map(lambda x: f"{x:,.0f} €")
    # Formater les pourcentages
    if "Taux de marge" in df_affichage.columns:
        df_affichage["Taux de marge"] = df_affichage["Taux de marge"].map(lambda x: f"{x:.1%}")

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
        # Graphique de répartition des charges (Année 1)
        resultat_net = df_resultats["Résultat net"].iloc[0]

        # Vérifier si les valeurs sont toutes non-négatives pour le graphique en camembert
        salaires_fondateurs = df_resultats["Salaires fondateurs"].iloc[0]
        autres_salaires = df_resultats["Autres salaires"].iloc[0]
        charges_fixes = df_resultats["Charges fixes"].iloc[0]
        impot = df_resultats["Impôt"].iloc[0]

        # Si le résultat net est positif, créer un camembert avec des valeurs positives
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

            ax2.bar(labels, values)
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

# Onglet Scénarios - Comparaison dynamique
with tabs[2]:
    st.header("Comparaison de scénarios")
    st.markdown("""
    Cette section permet de comparer votre **configuration actuelle** avec les scénarios prédéfinis ou personnalisés.
    Les calculs sont basés sur vos paramètres actuels, mais avec des taux de croissance différents.
    """)

    # Sélection des scénarios à comparer
    scenarios_a_comparer = st.multiselect(
        "Scénarios à comparer",
        ["Configuration actuelle"] + list(st.session_state.SCENARIOS.keys()),
        default=["Configuration actuelle", "Croissance modeste", "Croissance intéressante", "Croissance forte"]
    )

    # Création des dataframes pour les scénarios sélectionnés
    resultats_comparaison = []

    # Configuration actuelle
    if "Configuration actuelle" in scenarios_a_comparer:
        df_actuel = calculer_resultats(
            st.session_state.activite,
            st.session_state.rh,
            st.session_state.charges_fixes,
            st.session_state.projection
        )
        df_actuel["Scénario"] = "Configuration actuelle"
        resultats_comparaison.append(df_actuel)

    # Scénarios prédéfinis (appliqués dynamiquement à la configuration actuelle)
    for nom_scenario in st.session_state.SCENARIOS:
        if nom_scenario in scenarios_a_comparer:
            # Copie des paramètres actuels pour ce scénario
            projection_scenario = st.session_state.projection.copy()
            projection_scenario["taux_croissance"] = st.session_state.SCENARIOS[nom_scenario]["taux_croissance"]

            # Recalcul avec le taux de croissance du scénario
            df_scenario = calculer_resultats(
                st.session_state.activite,
                st.session_state.rh,
                st.session_state.charges_fixes,
                projection_scenario
            )
            df_scenario["Scénario"] = nom_scenario
            resultats_comparaison.append(df_scenario)

    if resultats_comparaison:
        # Concaténation des résultats
        df_comparaison = pd.concat(resultats_comparaison)

        # Graphique comparatif
        fig, ax = plt.subplots(figsize=(12, 6))

        for scenario in df_comparaison["Scénario"].unique():
            df_temp = df_comparaison[df_comparaison["Scénario"] == scenario]
            ax.plot(df_temp["Année"], df_temp["CA"], marker='o', linewidth=2, label=f"CA - {scenario}")
            ax.plot(df_temp["Année"], df_temp["Résultat net"], marker='s', linestyle='--', linewidth=2, label=f"Résultat net - {scenario}")

        ax.set_xlabel("Année")
        ax.set_ylabel("Montant (€)")
        ax.set_title("Comparaison des scénarios de croissance")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

        st.pyplot(fig)

        # Affichage des données comparatives
        st.subheader("Détails des scénarios")

        # --- formatage et tableau détaillé ---------------------------------
        df_comparaison_aff = df_comparaison.copy()

        # Colonnes numériques à formater en € (hors Année, Scénario et Taux de marge)
        cols_monnaie = [
            col for col in df_comparaison_aff.columns
            if col not in ("Année", "Scénario", "Taux de marge")
        ]
        for col in cols_monnaie:
            df_comparaison_aff[col] = df_comparaison_aff[col].map(
                lambda x: f"{x:,.0f} €"
            )

        # Formatage pourcentage
        if "Taux de marge" in df_comparaison_aff.columns:
            df_comparaison_aff["Taux de marge"] = df_comparaison_aff[
                "Taux de marge"
            ].map(lambda x: f"{x:.1%}")

        st.dataframe(df_comparaison_aff, use_container_width=True)

    else:
        st.info(
            "Sélectionnez au moins un scénario dans la liste pour afficher la comparaison."
        )
