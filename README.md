# Guide utilisateur – Calculateur Financier Datamap

## 1. Objectif du calculateur
Le calculateur Datamap estime en quelques clics :
- le **chiffre d’affaires (CA)** généré par vos prestations,
- vos **charges** (personnel, fixes, impôts),
- le **résultat net** et la **marge** sur plusieurs années,
- l’impact de différents **scénarios de croissance**.

Il vous aide à tester rapidement des hypothèses (*what‑if*) avant de prendre des décisions de recrutement ou d’investissement.

---

## 2. Installation & lancement
1. Installez Python ≥ 3.9 puis :
```bash
pip install streamlit pandas numpy matplotlib
```
2. Placez le fichier `calculateur.py` dans le dossier de votre choix.
3. Démarrez l’application :
```bash
streamlit run calculateur.py
```
4. Le calculateur s’ouvre automatiquement dans votre navigateur par défaut (http://localhost:8501).

> **Astuce :** l’application peut tourner sur un serveur distant ; partagez simplement l’URL.

---

## 3. Structure de l’interface
| Onglet | Contenu principal |
|--------|------------------|
| **Paramètres** | Saisie de votre activité, des ressources humaines, des charges fixes et des projections. |
| **Résultats & Graphiques** | Tableau prévisionnel, KPIs visuels, graphiques de CA et ventilation des charges. |
| **Scénarios** | Comparaison dynamique entre votre configuration actuelle et 1 à n scénarios prédéfinis. |

---

## 4. Onglet **Paramètres**
### 4.1 Choix du scénario de base
- *Personnalisé* (valeurs manuelles) ou un des trois scénarios prédéfinis (**Croissance modeste / intéressante / forte**).
- Changer de scénario **remplit automatiquement** les champs, mais vous pouvez ensuite les ajuster.

### 4.2 Activité prévue
Pour chaque service :
1. Indiquez la **quantité** (nb d’audits, de jours de conseil, etc.).
2. Le prix unitaire est fixe (tiré du catalogue interne).
3. Le calculateur affiche instantanément le **CA prévisionnel année 1** (maintenance incluse : 15 % du sur‑mesure).

### 4.3 Ressources humaines
| Champ | Signification |
|-------|--------------|
| *Nombre de fondateurs* | Fondateurs opérationnels et rémunérés. |
| *Salaire net/mois/fondateur* | Montant **net** avant charges patronales (60 %). |
| *Nombre de salariés* | CDI ou CDD hors fondateurs. |
| *Salaire brut chargé/an* | Coût **total** employeur par salarié. |
| *Nombre d’alternants* & *Coût alternant* | Inclut apprentis & stagiaires longue durée. |

> **Info‑bulle** : passez la souris sur un champ pour connaître le coût chargé annuel.

### 4.4 Charges fixes
- Séparées en 5 postes : Loyer, Logiciels, Déplacements, Matériel, Administration.
- **Indexation** : le loyer suit l’inflation (2 %), les autres postes ½ du taux de croissance.

### 4.5 Projections
- **Nombre d’années** : 1 à 5.
- **Taux de croissance annuel** : 0 % à 50 % (impacte CA et charges variables).

### 4.6 Informations complémentaires
Un rappel des constantes (taux IS, charges patronales, inflation, etc.).

---

## 5. Onglet **Résultats & Graphiques**
### 5.1 KPIs année 1
- **CA**, **Total charges**, **Résultat net** (+ marge en %).

### 5.2 Tableau prévisionnel
| Colonne | Détail |
|---------|--------|
| *CA* | CA global par année (incluant maintenance). |
| *Salaires fondateurs* / *Autres* | Montants chargés. |
| *Charges fixes* | Loyer + autres charges indexées. |
| *Résultat brut* | CA − charges totales. |
| *Impôt* | 25 % si bénéfice positif. |
| *Résultat net* | Après impôt. |
| *Taux de marge* | Résultat net / CA. |

### 5.3 Graphiques
- **Ligne** : évolution CA vs résultat net.
- **Camembert / barres** : répartition charges + résultat (année 1).
- **Seuil de rentabilité** : CA nécessaire pour couvrir charges fixes.

---

## 6. Onglet **Scénarios**
1. Cochez un ou plusieurs scénarios à comparer.
2. Le calculateur applique simplement **un autre taux de croissance** à vos paramètres actuels (pas de reset des volumes).
3. Visualisez :
   - graphes CA / résultat pour chaque scénario,
   - tableau consolidé multi‑scénarios.

> **Important :** votre configuration de base reste inchangée ; la comparaison est *à la volée*.

---

## 7. Bonnes pratiques & astuces
- **Sauvegarde** : Streamlit conserve les valeurs tant que la page reste ouverte. Pour reprendre plus tard, exportez vos paramètres (bouton ≡ → *Download app state* si activé).
- **Sensibilités rapides** : modifiez d’abord le *taux de croissance* puis ajustez la répartition d’activité.
- **Salaires fondateurs** : contrôlez qu’ils restent cohérents avec le ratio CA‑salaires du scénario.

---

## 8. Personnalisation avancée
Vous pouvez :
- **Modifier le catalogue** (`st.session_state.SERVICES`) pour ajouter d’autres offres.
- Changer les **hypothèses d’indexation** (inflation, charges variables) dans `calculer_resultats`.
- Ajouter un bouton *Export CSV* pour récupérer le DataFrame `df_resultats`.

---

## 9. FAQ & dépannage
| Problème | Solution |
|----------|----------|
| *« Le script plante sur set_page_config »* | Assurez‑vous qu’aucun second appel à `st.set_page_config` n’est exécuté avant les imports. |
| *Valeurs négatives dans le camembert* | Cela arrive si le résultat net est < 0 ; le graphique passe automatiquement en barres. |
| *Scénario non pris en compte* | Vérifiez que vous avez bien coché le scénario dans la liste et observé le graphique/​tableau. |

---

## 10. Crédits
Développé par l’équipe Datamap. Document rédigé le 19 avril 2025.

## force push
