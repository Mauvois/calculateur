# models.py
"""Modèles de données et logique métier pour le calculateur Caribo"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from config import (
    TAUX_IS, TAUX_TVA, TAUX_MAINTENANCE_MIN, TAUX_MAINTENANCE_MAX,
    NIVEAUX_COMPLEXITE
)


@dataclass
class FacteurVariation:
    """Représente un facteur qui influence le prix d'un service"""
    nom: str
    description: str
    impact_min: float  # Multiplicateur minimum (ex: 1.0)
    impact_max: float  # Multiplicateur maximum (ex: 2.0)
    valeur_defaut: float = 1.0


@dataclass
class Service:
    """Représente un service du catalogue Caribô"""
    id: str
    categorie: str
    nom: str
    description: str
    livrable: str
    valeur_client: str
    prix_min: float
    prix_max: float
    facteurs_variation: List[FacteurVariation] = field(default_factory=list)
    maintenance_applicable: bool = False

    def calculer_prix(self, complexite: str = "Moyenne", facteurs_custom: Dict[str, float] = None) -> float:
        """Calcule le prix du service en fonction de la complexité ou des facteurs personnalisés"""
        if facteurs_custom:
            # Mode avancé : calcul basé sur les facteurs personnalisés
            prix_base = self.prix_min
            ecart = self.prix_max - self.prix_min

            # Calculer l'impact moyen des facteurs
            impacts = []
            for facteur in self.facteurs_variation:
                valeur = facteurs_custom.get(facteur.nom, facteur.valeur_defaut)
                # Normaliser la valeur entre 0 et 1
                impact_normalise = (valeur - facteur.impact_min) / (facteur.impact_max - facteur.impact_min)
                impacts.append(impact_normalise)

            impact_moyen = sum(impacts) / len(impacts) if impacts else 0.5
            return prix_base + (ecart * impact_moyen)
        else:
            # Mode simple : utiliser le niveau de complexité
            niveau = NIVEAUX_COMPLEXITE.get(complexite, 0.5)
            return self.prix_min + (self.prix_max - self.prix_min) * niveau


@dataclass
class ServiceSelectionne:
    """Représente un service sélectionné pour un projet avec ses paramètres"""
    service: Service
    complexite: str = "Moyenne"
    facteurs_custom: Dict[str, float] = field(default_factory=dict)
    quantite: int = 1
    prix_unitaire: float = 0.0

    def __post_init__(self):
        # CORRECTION : Initialiser automatiquement les facteurs_custom avec les valeurs par défaut
        # si ils n'existent pas et que le service a des facteurs_variation
        if not self.facteurs_custom and self.service.facteurs_variation:
            for facteur in self.service.facteurs_variation:
                self.facteurs_custom[facteur.nom] = facteur.valeur_defaut

        if self.prix_unitaire == 0:
            # Utiliser les facteurs_custom si disponibles, sinon la complexité
            if self.facteurs_custom:
                self.prix_unitaire = self.service.calculer_prix(facteurs_custom=self.facteurs_custom)
            else:
                self.prix_unitaire = self.service.calculer_prix(self.complexite)

    @property
    def prix_total(self) -> float:
        return self.prix_unitaire * self.quantite

    @property
    def maintenance_annuelle(self) -> float:
        if self.service.maintenance_applicable:
            return self.prix_total * TAUX_MAINTENANCE_MIN
        return 0.0


@dataclass
class Projet:
    """Représente un projet client avec l'ensemble des services sélectionnés"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nom: str = "Nouveau projet"
    client: str = ""
    type_client: str = ""
    date_creation: datetime = field(default_factory=datetime.now)
    services: List[ServiceSelectionne] = field(default_factory=list)
    taux_maintenance: float = TAUX_MAINTENANCE_MIN

    @property
    def total_ht(self) -> float:
        return sum(s.prix_total for s in self.services)

    @property
    def tva(self) -> float:
        return self.total_ht * TAUX_TVA

    @property
    def total_ttc(self) -> float:
        return self.total_ht + self.tva

    @property
    def maintenance_annuelle_ht(self) -> float:
        services_tech = [s for s in self.services if s.service.maintenance_applicable]
        return sum(s.prix_total * self.taux_maintenance for s in services_tech)

    def ajouter_service(self, service: Service, complexite: str = "Moyenne",
                       quantite: int = 1, facteurs_custom: Dict[str, float] = None):
        """Ajoute un service au projet"""
        service_sel = ServiceSelectionne(
            service=service,
            complexite=complexite,
            quantite=quantite,
            facteurs_custom=facteurs_custom or {}
        )
        self.services.append(service_sel)

    def retirer_service(self, index: int):
        """Retire un service du projet par son index"""
        if 0 <= index < len(self.services):
            self.services.pop(index)

    def dupliquer(self) -> 'Projet':
        """Crée une copie du projet avec un nouvel ID"""
        nouveau = Projet(
            nom=f"{self.nom} (copie)",
            client=self.client,
            type_client=self.type_client,
            taux_maintenance=self.taux_maintenance
        )
        for service in self.services:
            nouveau.services.append(ServiceSelectionne(
                service=service.service,
                complexite=service.complexite,
                facteurs_custom=service.facteurs_custom.copy(),
                quantite=service.quantite,
                prix_unitaire=service.prix_unitaire
            ))
        return nouveau


@dataclass
class PrevisionAnnuelle:
    """Représente les prévisions pour une année"""
    annee: int
    projets: List[Projet] = field(default_factory=list)
    charges_fixes: Dict[str, float] = field(default_factory=dict)
    taux_croissance: float = 0.0

    @property
    def ca_projets(self) -> float:
        return sum(p.total_ht for p in self.projets)

    @property
    def ca_maintenance(self) -> float:
        return sum(p.maintenance_annuelle_ht for p in self.projets)

    @property
    def ca_total(self) -> float:
        ca_base = self.ca_projets + self.ca_maintenance
        if self.annee > 1:
            return ca_base * (1 + self.taux_croissance) ** (self.annee - 1)
        return ca_base

    @property
    def total_charges_fixes(self) -> float:
        return sum(self.charges_fixes.values())

    @property
    def resultat_brut(self) -> float:
        return self.ca_total - self.total_charges_fixes

    @property
    def impot(self) -> float:
        return max(0, self.resultat_brut * TAUX_IS)

    @property
    def resultat_net(self) -> float:
        return self.resultat_brut - self.impot

    @property
    def taux_marge(self) -> float:
        if self.ca_total > 0:
            return self.resultat_net / self.ca_total
        return 0.0


@dataclass
class Previsions:
    """Gère l'ensemble des prévisions sur plusieurs années"""
    nom_scenario: str = "Personnalisé"
    annees: List[PrevisionAnnuelle] = field(default_factory=list)

    def ajouter_annee(self, prevision: PrevisionAnnuelle):
        self.annees.append(prevision)

    def generer_projections(self, nb_annees: int, taux_croissance: float,
                          charges_fixes_base: Dict[str, float],
                          taux_inflation: float = 0.02):
        """Génère des projections sur plusieurs années"""
        if not self.annees:
            return

        # Année 1 est déjà configurée
        annee_base = self.annees[0]

        # Générer les années suivantes
        for i in range(2, nb_annees + 1):
            # Évolution des charges fixes avec inflation
            charges_fixes = {}
            for charge, montant in charges_fixes_base.items():
                charges_fixes[charge] = montant * (1 + taux_inflation) ** (i - 1)

            # Créer la prévision pour l'année
            prevision = PrevisionAnnuelle(
                annee=i,
                projets=annee_base.projets,  # Mêmes projets de base
                charges_fixes=charges_fixes,
                taux_croissance=taux_croissance
            )

            self.ajouter_annee(prevision)

    def get_dataframe_resultats(self):
        """Retourne un DataFrame avec les résultats pour toutes les années"""
        import pandas as pd

        resultats = []
        for prev in self.annees:
            resultats.append({
                "Année": prev.annee,
                "CA Projets": prev.ca_projets,
                "CA Maintenance": prev.ca_maintenance,
                "CA Total": prev.ca_total,
                "Charges fixes": prev.total_charges_fixes,
                "Résultat brut": prev.resultat_brut,
                "Impôt": prev.impot,
                "Résultat net": prev.resultat_net,
                "Taux de marge": prev.taux_marge
            })

        return pd.DataFrame(resultats)
