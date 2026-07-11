# Site Web Vitrine — UFR STA

Site web vitrine de l'UFR Sciences et Technologies Avancées (UFR STA),
Université Amadou Mahtar Mbow (UAM) de Dakar.

Projet final — Cours de Programmation Web (Dr Lamine YADE), Licence 3 Informatique.

## 1. Présentation du projet

Le site permet :

**Côté visiteurs**
- Consulter les informations générales de l'UFR (accueil, mot du directeur)
- Découvrir les départements (Informatique, Mathématiques, Physique)
- Consulter les formations et leurs programmes détaillés
- Consulter les actualités (séminaires, conférences, appels à candidature…)
- Consulter le journal des activités (ateliers, hackathons, visites…)
- Parcourir la galerie photos organisée par albums
- Consulter la liste des enseignants
- Contacter l'administration via un formulaire

**Côté administration** (`/login`)
- Tableau de bord avec statistiques
- Gestion complète (ajouter / modifier / supprimer) des actualités, activités,
  formations, départements, enseignants et albums photos
- **Upload de fichiers réel** : les photos (actualités, activités, enseignants,
  albums) sont téléversées depuis l'ordinateur de l'administrateur et stockées
  dans `static/uploads/`, pas de simples liens externes
- Consultation et suppression des messages reçus via le formulaire de contact

## 2. Technologies utilisées

- **Frontend** : HTML5, CSS3 (responsive, mobile first), JavaScript (léger)
- **Backend** : Flask (Python)
- **Base de données** : SQLite

## 3. Guide d'installation

### Prérequis
- Python 3.9 ou supérieur

### Étapes

```bash
# 1. Se placer dans le dossier du projet
cd ufr-sta

# 2. Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate        # sous Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

L'application est accessible sur : **http://127.0.0.1:5000**

La base de données SQLite (`database/ufr_sta.db`) est créée automatiquement
au premier lancement, avec des données de démonstration.

### Accès administration

- URL : `http://127.0.0.1:5000/login`
- Identifiant : `admin`
- Mot de passe : `admin123`

> ⚠️ Pensez à changer ce mot de passe et la clé secrète (`SECRET_KEY`
> dans `app.py`) avant tout déploiement en production.

## 4. Arborescence du projet

```
ufr-sta/
├── app.py                  # Application Flask (routes + logique)
├── requirements.txt
├── database/
│   └── schema.sql           # Schéma SQL (tables)
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/logo.png
└── templates/
    ├── base.html
    ├── index.html
    ├── departements.html / departement_detail.html
    ├── formations.html / formation_detail.html
    ├── actualites.html / actualite_detail.html
    ├── activites.html / activite_detail.html
    ├── enseignants.html
    ├── galerie.html
    ├── contact.html
    ├── login.html
    ├── 404.html
    └── admin/
        ├── base_admin.html
        ├── dashboard.html
        ├── actualites.html / actualite_form.html
        ├── activites.html / activite_form.html
        ├── formations.html / formation_form.html
        ├── departements.html / departement_form.html
        ├── enseignants.html / enseignant_form.html
        ├── galerie.html / album_form.html
        └── messages.html
```

## 5. Travail collaboratif (GitHub)

Ce projet est destiné à être développé en groupe de 2 à 3 étudiants avec :
- Un dépôt GitHub partagé
- Une branche par fonctionnalité (`feature/actualites`, `feature/admin`, ...)
- Des commits réguliers et explicites
- Des Pull Requests pour fusionner les contributions

## 6. Captures d'écran

_À compléter avec des captures d'écran des pages principales (accueil,
formations, galerie, tableau de bord admin) avant la soutenance._

---
Dr Lamine Yade, UAM@2026
