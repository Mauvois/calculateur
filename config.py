# config.py
"""Configuration et constantes pour le calculateur Caribô"""

# Constantes fiscales
TAUX_IS = 0.25  # Taux d'impôt sur les sociétés (25%)
TAUX_TVA = 0.085  # TVA DOM (8.5%)

# Taux de maintenance pour les services technologiques
TAUX_MAINTENANCE_MIN = 0.10  # 10% minimum
TAUX_MAINTENANCE_MAX = 0.15  # 15% maximum

# Catégories de services
CATEGORIES_SERVICES = [
    "Audit",
    "Ingénierie et gouvernance des données spatiales",
    "Data Science & Analyse Spatiale",
    "Collecte de données & Télédétection",
    "Cartographie & Développement d'outils métiers",
    "Service client"
]

# Types de clients pour les templates
TYPES_CLIENTS = [
    "Commune",
    "EPCI",
    "Collectivité territoriale sup",
    "Syndicat ou établissement public spécialisé",
    "Administration de l'État",
    "Promoteur ou aménageur immobilier",
    "Agence de conseil",
    "Acteur économique privé",
    "Association",
    "ONG"
]

# Niveaux de complexité
NIVEAUX_COMPLEXITE = {
    "Basique": 0.0,        # Projet simple, standard
    "Standard": 0.25,      # Projet classique
    "Intermédiaire": 0.5,  # Quelques spécificités
    "Avancé": 0.75,        # Complexité technique élevée
    "Expert": 1.0          # Projet très complexe, sur-mesure
}

# Charges fixes par défaut
CHARGES_FIXES_DEFAUT = {
    "loyer": 3000,
    "logiciels": 1500,
    "deplacements": 2000,
    "materiel": 1000,
    "admin": 1500
}

# Charges fixes détaillées pour SAS
CHARGES_FIXES_DETAILLEES = {
    "salaires_dirigeants": 0,          # Rémunération via dividendes
    "charges_sociales_minimales": 0,   # Pas de salaires = pas de charges
    "loyer_bureau": 3000,
    "logiciels_licences": 2000,        # Outils géomatique/SIG coûteux
    "materiel_informatique": 1500,     # Amortissement annuel
    "deplacements_missions": 2500,     # Missions terrain
    "assurances_rc": 800,              # RC pro + autres
    "comptabilite_juridique": 2000,    # Expert-comptable + formalités SAS
    "communication_marketing": 1000,   # Site web, comm
    "frais_bancaires": 200,
    "autres_frais": 500
}

OBJECTIFS_REMUNERATION = {
    "dividendes_nets_par_associe": 36000,  # 36k€ nets par associé
    "nb_associes": 2,
    "total_dividendes_nets": 72000,
    "dividendes_bruts_necessaires": 103000,  # Avec flat tax 30%
    "benefice_avant_is_necessaire": 137000   # Avec IS 25%
}

# Scénarios de croissance
SCENARIOS_CROISSANCE = {
    "Prudent": {
        "description": "Démarrage progressif, consolidation de l'activité",
        "ca_objectif_annee_1": 160000,  # Pour 137k€ bénéfice + charges
        "taux_croissance": 0.08,        # 8% croissance/an
        "taux_inflation_charges": 0.02,
        "mix_projets": {
            "gros_projets": {"nb": 1, "ca_moyen": 50000, "description": "1 gros projet (40-60k€)"},
            "projets_moyens": {"nb": 3, "ca_moyen": 20000, "description": "3 projets moyens (15-25k€)"},
            "petits_projets": {"nb": 5, "ca_moyen": 10000, "description": "5 petits projets (5-15k€)"}
        },
        "charges_fixes_initiales": 12000
    },
    "Réaliste": {
        "description": "Développement équilibré avec montée en gamme",
        "ca_objectif_annee_1": 200000,
        "taux_croissance": 0.12,        # 12% croissance/an
        "taux_inflation_charges": 0.025,
        "mix_projets": {
            "gros_projets": {"nb": 2, "ca_moyen": 55000, "description": "2 gros projets (45-65k€)"},
            "projets_moyens": {"nb": 3, "ca_moyen": 25000, "description": "3 projets moyens (20-30k€)"},
            "petits_projets": {"nb": 2, "ca_moyen": 12500, "description": "2 petits projets (10-15k€)"}
        },
        "charges_fixes_initiales": 15000
    },
    "Ambitieux": {
        "description": "Croissance forte avec projets premium",
        "ca_objectif_annee_1": 280000,
        "taux_croissance": 0.18,        # 18% croissance/an
        "taux_inflation_charges": 0.03,
        "mix_projets": {
            "gros_projets": {"nb": 3, "ca_moyen": 60000, "description": "3 gros projets premium (50-70k€)"},
            "projets_moyens": {"nb": 3, "ca_moyen": 30000, "description": "3 projets moyens (25-35k€)"},
            "petits_projets": {"nb": 1, "ca_moyen": 10000, "description": "1 petit projet (complément)"}
        },
        "charges_fixes_initiales": 18000
    }
}

# Configuration de l'application
APP_CONFIG = {
    "title": "Calculateur Financier - Caribô",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuration des graphiques
GRAPH_CONFIG = {
    "figsize": (10, 6),
    "dpi": 100,
    "style": "seaborn-v0_8-darkgrid",
    "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
}

# Options d'export PDF
PDF_CONFIG = {
    "page_size": "A4",
    "margin": 72,  # 1 inch
    "font_family": "Helvetica",
    "font_size": 10,
    "title_size": 16,
    "subtitle_size": 14
}

# Paramètres de simulation
SIMULATION_PARAMS = {
    "duree_gros_projet_mois": 8,      # 6-10 mois
    "duree_projet_moyen_mois": 4,     # 3-5 mois
    "duree_petit_projet_mois": 2,     # 1-3 mois
    "capacite_simultanee_annee_1": 1, # 1 projet à la fois
    "capacite_simultanee_annee_3": 2, # 2 projets simultanés en année 3
    "gain_efficacite_annuel": 0.10   # 10% de gain d'efficacité par an
}
