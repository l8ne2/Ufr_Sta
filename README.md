# Site Web Vitrine — UFR STA

Site web vitrine de l'UFR Sciences et Technologies Avancées (UFR STA),
Université Amadou Mahtar Mbow (UAM) de Dakar.

Projet final — Cours de Programmation Web (Dr Lamine YADE), Licence 3 Informatique.

---

## 1. Équipe

| Membre | GitHub |
|---|---|
| Aliou BA | [@l8ne2](https://github.com/l8ne2) |
| Abdoul Guisse | [@guissemabo2005-hash](https://github.com/guissemabo2005-hash) |

Dépôt du projet : https://github.com/l8ne2/Ufr_Sta

## 2. Présentation du projet

Le site permet :

**Côté visiteurs**
- Consulter les informations générales de l'UFR (accueil, présentation)
- Découvrir les départements : **MIM** (Mathématiques, Informatique et
  Modélisation) et **SMU** (Sciences de la Mer et de l'Univers)
- Consulter les formations (filières **MPI** et **SML**) et leurs programmes détaillés
- Consulter les actualités (appels à candidature, réunions d'information…)
- Consulter le journal des activités (journées, participations à des événements…)
- Parcourir la galerie photos organisée par albums, avec **agrandissement des
  photos au clic (lightbox)**
- Consulter la liste des enseignants (photos centrées sur le visage)
- Contacter l'administration via un formulaire (nom, email, téléphone, message)

**Côté administration** (`/login`)
- Tableau de bord avec statistiques
- Gestion complète (ajouter / modifier / supprimer) des actualités, activités,
  formations, départements, enseignants et albums photos
- **Upload de fichiers réel** : les photos sont téléversées depuis l'ordinateur
  de l'administrateur et stockées dans `static/uploads/`
- Consultation et suppression des messages reçus via le formulaire de contact

## 3. Technologies utilisées

- **Frontend** : HTML5, CSS3 (responsive, mobile first), JavaScript (léger, sans framework)
- **Backend** : Flask (Python)
- **Base de données** : SQLite

## 4. Guide d'installation

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
au premier lancement, avec les données de démonstration (départements,
formations, actualités, activités, enseignants, galerie). Ce fichier n'est
pas versionné sur GitHub : si vous modifiez le code de `seed_demo_data()`
dans `app.py`, supprimez `database/ufr_sta.db` puis relancez `python app.py`
pour que les changements soient pris en compte.

### Accès administration

- URL : `http://127.0.0.1:5000/login`
- Identifiant : `admin`
- Mot de passe : `admin123`



## 5. Arborescence du projet

```
ufr-sta/
├── app.py                      # Application Flask (routes, logique, données de démo)
├── requirements.txt
├── README.md
├── TACHES.md                   # Répartition des tâches du groupe
├── .gitignore
│
├── database/
│   └── schema.sql               # Schéma SQL (tables)
│                                 # ufr_sta.db se crée ici automatiquement (non versionné)
│
├── static/
│   ├── css/style.css            # Feuille de style (palette navy / blanc / or)
│   ├── js/main.js               # Menu mobile, alertes, lightbox galerie
│   ├── images/                  # Photos "officielles" du site (versionnées)
│   │   ├── logo.png
│   │   ├── reunion_continuite_pedagogique.jpg
│   │   ├── anam_journee_gens_mer.jpg
│   │   ├── journee_excellence_1.jpg / _2.jpg
│   │   ├── excellence_anam_groupe.jpg / _audience.jpg / _remise_medailles.jpg / _ruban.jpg
│   │   ├── ens_amadou_dahirou_gueye.jpg
│   │   ├── ens_thierno_sow.jpg
│   │   ├── ens_makha_ndao.jpg
│   │   └── actu_recrutement_maths.jpg
│   └── uploads/                 # Photos ajoutées depuis l'admin (non versionné)
│
└── templates/
    ├── base.html                # Layout commun (navbar fixe + footer)
    ├── index.html                # Accueil
    ├── departements.html / departement_detail.html
    ├── formations.html / formation_detail.html
    ├── actualites.html / actualite_detail.html
    ├── activites.html / activite_detail.html
    ├── enseignants.html
    ├── galerie.html               # Avec lightbox
    ├── contact.html
    ├── login.html
    ├── 404.html
    └── admin/
        ├── base_admin.html        # Layout admin (sidebar)
        ├── dashboard.html
        ├── actualites.html / actualite_form.html
        ├── activites.html / activite_form.html
        ├── formations.html / formation_form.html
        ├── departements.html / departement_form.html
        ├── enseignants.html / enseignant_form.html
        ├── galerie.html / album_form.html
        └── messages.html
```

## 6. Structure académique du site (données réelles)

**Départements**
- **MIM** — Mathématiques, Informatique et Modélisation (regroupe les mentions
  Mathématiques et Modélisation (MM) et Informatique) — responsable : Dr Thierno
  Mohamadane Mansour Sow
- **SMU** — Sciences de la Mer et de l'Univers (regroupe les mentions Physique
  et Applications (PA) et Sciences de la Mer et du Littoral (SML)) —
  responsable : Dr Makha Ndao

**Filières / Formations**
- Licence **MPI** — Mathématiques, Physique et Informatique (dépt. MIM)
- Licence **SML** — Sciences de la Mer et du Littoral (dépt. SMU)

**Enseignants référencés**
- Amadou Dahirou Gueye — Informatique (MIM)
- Thierno Mohamadane Mansour Sow — Chef du département MIM
- Makha Ndao — Chef du département SMU

## 7. Travail collaboratif (GitHub)

Projet développé à deux avec :
- Un dépôt GitHub partagé (collaborateurs invités)
- Une branche dédiée par fonctionnalité
- Des Pull Requests relues puis fusionnées sur `main`




