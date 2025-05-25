# data.py
"""Données des services et templates de projets pour le calculateur Caribo"""

from models import Service, FacteurVariation, Projet, ServiceSelectionne
from typing import List, Dict


def creer_catalogue_services() -> Dict[str, Service]:
    """Crée et retourne le catalogue complet des services Caribo"""

    services = []

    # AUDIT
    services.append(Service(
        id="audit_intelligence_spatiale",
        categorie="Audit",
        nom="Audit en intelligence spatiale",
        description="Diagnostic complet du système d'information géospatial",
        livrable="Rapport 360° : diagnostic des données, besoins analytiques et leviers de valorisation",
        valeur_client="Vision complète des forces et faiblesses, alignement stratégique, recommandations ciblées",
        prix_min=4000,
        prix_max=12000,
        facteurs_variation=[
            FacteurVariation("Durée entretiens", "Nombre d'heures d'entretiens (2h à 12h)", 2, 12, 5),
            FacteurVariation("Nb interlocuteurs", "Nombre de personnes interrogées", 2, 10, 4),
            FacteurVariation("Axes analysés", "Nombre d'axes stratégiques", 1, 5, 2)
        ]
    ))

    # INGÉNIERIE ET GOUVERNANCE
    services.append(Service(
        id="conception_socle_donnees",
        categorie="Ingénierie et gouvernance des données spatiales",
        nom="Conception socle commun de données spatiales",
        description="Architecture et structuration des données spatiales",
        livrable="Registre des données (architecture des données structurées et non structurées)",
        valeur_client="Centralisation et simplification des données, conformité RGPD, meilleure collaboration",
        prix_min=4000,
        prix_max=12000,
        facteurs_variation=[
            FacteurVariation("Nb bases", "Nombre de bases à intégrer", 1, 10, 3),
            FacteurVariation("Diversité formats", "Complexité des formats", 1, 5, 2),
            FacteurVariation("Catalogue existant", "Absence de catalogue (0) ou présence (1)", 0, 1, 0)
        ]
    ))

    services.append(Service(
        id="nettoyage_harmonisation",
        categorie="Ingénierie et gouvernance des données spatiales",
        nom="Nettoyage, harmonisation et migration",
        description="Amélioration de la qualité des données",
        livrable="Base de données nettoyée, homogène, documentée",
        valeur_client="Fiabilité des données accrue, optimisation des processus",
        prix_min=4000,
        prix_max=10000,
        facteurs_variation=[
            FacteurVariation("Volume données", "Volume en Go", 1, 100, 10),
            FacteurVariation("Nb jeux", "Nombre de jeux de données", 1, 20, 5),
            FacteurVariation("Données non structurées", "Présence (1) ou absence (0)", 0, 1, 0)
        ]
    ))

    services.append(Service(
        id="automatisation_flux",
        categorie="Ingénierie et gouvernance des données spatiales",
        nom="Automatisation des flux de données (ETL, API)",
        description="Mise en place de pipelines de données automatisés",
        livrable="Service déployé sur Cloud ou serveur pour l'automatisation",
        valeur_client="Disponibilité des données pour utilisation métier et valorisation analytique",
        prix_min=6000,
        prix_max=20000,
        facteurs_variation=[
            FacteurVariation("Nb sources", "Nombre de sources à synchroniser", 1, 10, 3),
            FacteurVariation("Fréquence MAJ", "Quotidienne (1) vs mensuelle (0)", 0, 1, 0.5),
            FacteurVariation("Nb destinations", "Nombre de systèmes cibles", 1, 5, 2)
        ],
        maintenance_applicable=True
    ))

    # DATA SCIENCE & ANALYSE SPATIALE
    services.append(Service(
        id="analyse_exploratoire",
        categorie="Data Science & Analyse Spatiale",
        nom="Analyse exploratoire statistique",
        description="Exploration statistique des données",
        livrable="Rapport statistique exploratoire détaillé",
        valeur_client="Identification des distributions et tendances, validation des données",
        prix_min=2000,
        prix_max=5000,
        facteurs_variation=[
            FacteurVariation("Nb variables", "Nombre de variables à analyser", 5, 50, 20),
            FacteurVariation("Granularité", "Commune (1) vs IRIS (2) vs adresse (3)", 1, 3, 2),
            FacteurVariation("Prétraitement", "Nécessité de retraitement", 0, 1, 0.5)
        ]
    ))

    services.append(Service(
        id="modelisation_avancee",
        categorie="Data Science & Analyse Spatiale",
        nom="Modélisation avancée",
        description="Machine learning, séries temporelles, clustering",
        livrable="Modèles prédictifs, cartes prospectives",
        valeur_client="Anticipation efficace, optimisation des ressources, réduction des incertitudes",
        prix_min=5000,
        prix_max=15000,
        facteurs_variation=[
            FacteurVariation("Complexité modèle", "Simple (1) vs complexe (3)", 1, 3, 2),
            FacteurVariation("Taille échantillon", "En milliers de lignes", 1, 100, 10),
            FacteurVariation("Nb scénarios", "Nombre de versions du modèle", 1, 5, 2)
        ]
    ))

    services.append(Service(
        id="analyse_spatiale",
        categorie="Data Science & Analyse Spatiale",
        nom="Analyse spatiale",
        description="Analyse de la dimension géographique",
        livrable="Rapport d'analyse et données spatialisées",
        valeur_client="Compréhension de la dynamique spatiale du territoire",
        prix_min=5000,
        prix_max=15000,
        facteurs_variation=[
            FacteurVariation("Étendue territoire", "Commune (1) vs région (3)", 1, 3, 2),
            FacteurVariation("Nb couches", "Nombre de couches spatiales", 1, 10, 3),
            FacteurVariation("Analyse mobilité", "Avec (1) ou sans (0)", 0, 1, 0)
        ]
    ))

    # COLLECTE DE DONNÉES & TÉLÉDÉTECTION
    services.append(Service(
        id="collecte_terrain",
        categorie="Collecte de données & Télédétection",
        nom="Collecte des données terrain",
        description="Collecte de données sur le terrain",
        livrable="Outils de collecte, ateliers de cartographie participative",
        valeur_client="Valeurs réelles et fiables pour l'analyse du territoire",
        prix_min=8000,
        prix_max=25000,
        facteurs_variation=[
            FacteurVariation("Taille zone", "Surface en km²", 1, 100, 10),
            FacteurVariation("Nb points", "Points à collecter", 10, 500, 100),
            FacteurVariation("Méthode", "Papier (0) vs mobile (0.5) vs drone (1)", 0, 1, 0.5)
        ]
    ))

    services.append(Service(
        id="classification_images",
        categorie="Collecte de données & Télédétection",
        nom="Classification d'images satellite",
        description="Traitement et classification d'images",
        livrable="Cartographie de la classification, analyse de surfaces",
        valeur_client="Monitoring et évaluation de l'impact des projets",
        prix_min=5000,
        prix_max=12000,
        facteurs_variation=[
            FacteurVariation("Nb images", "Nombre d'images à traiter", 1, 50, 10),
            FacteurVariation("Résolution", "10m (0) vs 50cm (1)", 0, 1, 0.5),
            FacteurVariation("Nb classes", "Nombre de classes à discriminer", 2, 10, 4)
        ]
    ))

    # CARTOGRAPHIE & OUTILS MÉTIERS
    services.append(Service(
        id="cartographie_edition",
        categorie="Cartographie & Développement d'outils métiers",
        nom="Cartographie d'édition",
        description="Création de cartes pour l'édition",
        livrable="Charte graphique, atlas, fiches cartographiques",
        valeur_client="Identité graphique et diffusion adaptée au public cible",
        prix_min=3000,
        prix_max=10000,
        facteurs_variation=[
            FacteurVariation("Nb cartes", "Nombre de cartes finales", 1, 20, 5),
            FacteurVariation("Formats", "Nombre de formats différents", 1, 5, 2),
            FacteurVariation("Personnalisation", "Standard (0) vs sur-mesure (1)", 0, 1, 0.5)
        ]
    ))

    services.append(Service(
        id="cartes_web",
        categorie="Cartographie & Développement d'outils métiers",
        nom="Cartes web interactives",
        description="Développement de cartes web",
        livrable="Cartes web responsive et interactives",
        valeur_client="Accès grand public facilité, valorisation externe des données",
        prix_min=5000,
        prix_max=20000,
        facteurs_variation=[
            FacteurVariation("Nb couches", "Couches interactives", 1, 20, 5),
            FacteurVariation("Filtres dynamiques", "Présence (1) ou absence (0)", 0, 1, 1),
            FacteurVariation("Connexion BDD", "Live (1) ou statique (0)", 0, 1, 0)
        ],
        maintenance_applicable=True
    ))

    services.append(Service(
        id="dashboard",
        categorie="Cartographie & Développement d'outils métiers",
        nom="Tableaux de bord dynamiques",
        description="Création de dashboards interactifs",
        livrable="Dashboards interactifs personnalisés",
        valeur_client="Aide à la décision quotidienne, efficacité accrue",
        prix_min=5000,
        prix_max=20000,
        facteurs_variation=[
            FacteurVariation("Nb indicateurs", "Nombre d'indicateurs", 5, 50, 10),
            FacteurVariation("Fréquence actualisation", "Temps réel (1) vs hebdo (0)", 0, 1, 0.5),
            FacteurVariation("Nb sources", "Diversité des sources", 1, 10, 3)
        ],
        maintenance_applicable=True
    ))

    # SERVICE CLIENT
    services.append(Service(
        id="formation",
        categorie="Service client",
        nom="Formation et transfert de compétences",
        description="Sessions de formation aux outils et méthodes",
        livrable="Sessions de formation, documentation métier",
        valeur_client="Autonomie renforcée des équipes, réduction des coûts d'assistance",
        prix_min=1200,
        prix_max=2000,
        facteurs_variation=[
            FacteurVariation("Nb participants", "Nombre de participants", 1, 20, 5),
            FacteurVariation("Supports personnalisés", "Avec (1) ou sans (0)", 0, 1, 1),
            FacteurVariation("Exercices pratiques", "Avec (1) ou sans (0)", 0, 1, 1)
        ]
    ))

    # Créer un dictionnaire avec l'ID comme clé
    return {s.id: s for s in services}


def creer_templates_projets(catalogue_services: Dict[str, Service]) -> Dict[str, Projet]:
    """Crée les templates de projets basés sur les 5 exemples fournis"""

    templates = {}

    # 1. EPCI - Intercommunalité
    epci = Projet(
        nom="EPCI - Projet ZAN et gestion foncière",
        client="Intercommunalité type",
        type_client="EPCI / Intercommunalité"
    )
    epci.ajouter_service(catalogue_services["audit_intelligence_spatiale"], "Moyenne", 1,
                        {"Durée entretiens": 6, "Nb interlocuteurs": 6, "Axes analysés": 4})
    epci.ajouter_service(catalogue_services["conception_socle_donnees"], "Forte", 1,
                        {"Nb bases": 7, "Diversité formats": 4, "Catalogue existant": 0})
    epci.ajouter_service(catalogue_services["nettoyage_harmonisation"], "Forte", 1,
                        {"Volume données": 50, "Nb jeux": 10, "Données non structurées": 1})
    epci.ajouter_service(catalogue_services["automatisation_flux"], "Moyenne", 1,
                        {"Nb sources": 5, "Fréquence MAJ": 0.5, "Nb destinations": 3})
    epci.ajouter_service(catalogue_services["dashboard"], "Moyenne", 1,
                        {"Nb indicateurs": 15, "Fréquence actualisation": 0.5, "Nb sources": 4})
    epci.ajouter_service(catalogue_services["formation"], "Forte", 3)
    templates["epci"] = epci

    # 2. Petite commune rurale
    commune = Projet(
        nom="Commune - Diagnostic vacance",
        client="Petite commune rurale",
        type_client="Petite commune rurale"
    )
    commune.ajouter_service(catalogue_services["audit_intelligence_spatiale"], "Faible", 1,
                           {"Durée entretiens": 3, "Nb interlocuteurs": 3, "Axes analysés": 2})
    commune.ajouter_service(catalogue_services["analyse_exploratoire"], "Faible", 1,
                           {"Nb variables": 15, "Granularité": 2, "Prétraitement": 0.5})
    commune.ajouter_service(catalogue_services["analyse_spatiale"], "Moyenne", 1,
                           {"Étendue territoire": 1, "Nb couches": 4, "Analyse mobilité": 0})
    commune.ajouter_service(catalogue_services["cartographie_edition"], "Faible", 1,
                           {"Nb cartes": 4, "Formats": 1, "Personnalisation": 0})
    templates["commune"] = commune

    # 3. Promoteur immobilier
    promoteur = Projet(
        nom="Promoteur - Analyse de marché 300 logements",
        client="Promoteur immobilier",
        type_client="Promoteur immobilier"
    )
    promoteur.ajouter_service(catalogue_services["audit_intelligence_spatiale"], "Faible", 1,
                             {"Durée entretiens": 2, "Nb interlocuteurs": 2, "Axes analysés": 1})
    promoteur.ajouter_service(catalogue_services["modelisation_avancee"], "Forte", 1,
                             {"Complexité modèle": 2.5, "Taille échantillon": 12, "Nb scénarios": 2})
    promoteur.ajouter_service(catalogue_services["analyse_spatiale"], "Moyenne", 1,
                             {"Étendue territoire": 2, "Nb couches": 5, "Analyse mobilité": 1})
    promoteur.ajouter_service(catalogue_services["dashboard"], "Faible", 1,
                             {"Nb indicateurs": 8, "Fréquence actualisation": 0, "Nb sources": 2})
    templates["promoteur"] = promoteur

    # 4. CTM - Collectivité Territoriale de Martinique
    ctm = Projet(
        nom="CTM - Système d'observation spatiale SOSTE",
        client="Collectivité Territoriale de Martinique",
        type_client="Collectivité territoriale"
    )
    ctm.ajouter_service(catalogue_services["audit_intelligence_spatiale"], "Moyenne", 1,
                       {"Durée entretiens": 8, "Nb interlocuteurs": 8, "Axes analysés": 4})
    ctm.ajouter_service(catalogue_services["conception_socle_donnees"], "Forte", 1,
                       {"Nb bases": 6, "Diversité formats": 4, "Catalogue existant": 0})
    ctm.ajouter_service(catalogue_services["nettoyage_harmonisation"], "Forte", 1,
                       {"Volume données": 80, "Nb jeux": 12, "Données non structurées": 1})
    ctm.ajouter_service(catalogue_services["cartographie_edition"], "Forte", 1,
                       {"Nb cartes": 30, "Formats": 2, "Personnalisation": 1})
    ctm.ajouter_service(catalogue_services["cartes_web"], "Moyenne", 1,
                       {"Nb couches": 8, "Filtres dynamiques": 1, "Connexion BDD": 0})
    ctm.ajouter_service(catalogue_services["dashboard"], "Moyenne", 1,
                       {"Nb indicateurs": 20, "Fréquence actualisation": 0.5, "Nb sources": 5})
    ctm.ajouter_service(catalogue_services["formation"], "Moyenne", 3)
    templates["ctm"] = ctm

    # 5. Association mangrove
    association = Projet(
        nom="Association - Cartographie participative mangrove",
        client="Association de sauvegarde",
        type_client="Association"
    )
    association.ajouter_service(catalogue_services["collecte_terrain"], "Faible", 1,
                               {"Taille zone": 5, "Nb points": 50, "Méthode": 0.5})
    association.ajouter_service(catalogue_services["cartographie_edition"], "Faible", 1,
                               {"Nb cartes": 3, "Formats": 1, "Personnalisation": 0})
    association.ajouter_service(catalogue_services["formation"], "Moyenne", 1,
                               {"Nb participants": 10, "Supports personnalisés": 0, "Exercices pratiques": 1})
    templates["association"] = association

    return templates
