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
    "EPCI / Intercommunalité",
    "Petite commune rurale",
    "Promoteur immobilier",
    "Collectivité territoriale",
    "Association"
]

# Niveaux de complexité
NIVEAUX_COMPLEXITE = {
    "Faible": 0.0,    # Prix minimum
    "Moyenne": 0.5,   # Prix médian
    "Forte": 1.0      # Prix maximum
}

# Charges fixes par défaut
CHARGES_FIXES_DEFAUT = {
    "loyer": 3000,
    "logiciels": 1500,
    "deplacements": 2000,
    "materiel": 1000,
    "admin": 1500
}

# Scénarios de croissance
SCENARIOS_CROISSANCE = {
    "Prudent": {
        "description": "Croissance modeste, approche conservatrice",
        "taux_croissance": 0.10,
        "nb_projets_annee_1": 15,
        "taux_inflation_charges": 0.02
    },
    "Réaliste": {
        "description": "Croissance progressive et maîtrisée",
        "taux_croissance": 0.20,
        "nb_projets_annee_1": 25,
        "taux_inflation_charges": 0.03
    },
    "Ambitieux": {
        "description": "Forte croissance et développement rapide",
        "taux_croissance": 0.35,
        "nb_projets_annee_1": 40,
        "taux_inflation_charges": 0.05
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
