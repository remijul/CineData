# Guide étudiant — Git & Configuration de l'environnement
## Jour 1 · Projet CinéData

---

## Introduction

Avant d'écrire la moindre ligne de code d'extraction, deux choses doivent être en place : un système qui garde une trace de votre travail (Git), et un environnement Python isolé et reproductible (le venv). Ce guide couvre les deux, dans l'ordre où vous en aurez besoin.

À la fin de cette journée, vous devez avoir : un dépôt Git fonctionnel, un environnement virtuel actif, les dépendances installées, et un kernel Jupyter prêt à l'emploi si vous travaillez avec des notebooks.

---

## Partie 1 — Git

### Concepts

Git est un système de **versionnement** : il garde un historique de toutes les modifications apportées à votre code, vous permet de revenir en arrière, et de travailler sur plusieurs pistes en parallèle (les branches) sans tout mélanger.

Sans Git, un projet qui évolue ressemble vite à une suite de fichiers `script_v2_final_vraiment_final.py`. Avec Git, chaque étape importante est un **commit** : un instantané daté et commenté de l'état du code à ce moment-là.

### Définitions

| Terme | Signification |
|---|---|
| Dépôt (repository) | Le dossier de projet suivi par Git |
| Commit | Un instantané du code, avec un message qui explique ce qui a changé |
| Branche | Une piste de travail indépendante, qui peut être fusionnée avec une autre |
| `.gitignore` | Un fichier qui liste ce que Git doit ignorer (ex. clés API, environnement virtuel) |
| Remote | La copie du dépôt hébergée en ligne (ex. GitHub) |
| Push / Pull | Envoyer ses commits vers le remote / récupérer ceux des autres |

### Mise en œuvre

**1. Configuration initiale** (une seule fois sur votre machine) :
```bash
git config --global user.name "Votre Nom"
git config --global user.email "vous@exemple.com"
```

**2. Initialiser votre dépôt de projet :**
```bash
mkdir cinedata-<votre-prenom>
cd cinedata-<votre-prenom>
git init
```

**3. Créer la structure de dossiers :**
```
cinedata-<votre-prenom>/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── raw/
├── src/
└── notebooks/
```

**4. Créer le `.gitignore` AVANT toute clé API :**
```
.env
__pycache__/
*.pyc
venv/
.venv/
*.db
data/raw/*.csv
data/raw/*.json
```

**5. Premier commit :**
```bash
git add .
git commit -m "Initial commit: structure du projet"
```

**6. Notion de branche** (à utiliser si vous voulez tester une idée sans risquer votre code principal) :
```bash
git checkout -b essai-scraping
# ... modifications ...
git add .
git commit -m "Essai scraping"
git checkout main
git merge essai-scraping
```

**7. Connecter un dépôt distant (GitHub) :**
Créez un dépôt vide sur GitHub (sans README ni `.gitignore` auto-générés, pour éviter un conflit dès le premier push), puis :
```bash
git remote add origin <URL_DE_VOTRE_REPO>
git push -u origin main
```

**Vérification avant de continuer :** `git status` doit être propre (rien à committer), votre premier commit doit apparaître avec `git log --oneline`, et votre code doit être visible sur GitHub.

---

## Partie 2 — Configuration de l'environnement (venv)

### Concepts

Un environnement virtuel (venv) isole les dépendances Python de votre projet du reste de votre machine. Sans ça, installer une bibliothèque pour ce projet peut entrer en conflit avec une version différente utilisée par un autre projet. Le venv garantit aussi que n'importe qui peut reproduire exactement votre environnement à partir d'un simple fichier `requirements.txt`.

### Définitions

| Terme | Signification |
|---|---|
| venv | Un environnement Python isolé, propre à un projet |
| `requirements.txt` | La liste des bibliothèques nécessaires au projet, avec leurs versions |
| Activer / désactiver | Basculer le terminal pour qu'il utilise le Python du venv plutôt que celui du système |
| Kernel (Jupyter) | Le moteur d'exécution Python utilisé par un notebook — doit correspondre au venv |

### Mise en œuvre

**1. Créer le venv, à la racine du projet :**
```bash
# Windows
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

**2. Activer le venv :**
```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (cmd)
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```
Le prompt du terminal doit maintenant commencer par `(venv)`.

**3. Créer `requirements.txt`** à la racine (contenu qui grandira au fil de la semaine) :
```
requests
python-dotenv
beautifulsoup4
pandas
jupyterlab
sqlalchemy
fastapi
uvicorn
```

**4. Installer les dépendances :**
```bash
pip install -r requirements.txt
```

**5. Créer un kernel Jupyter dédié au projet** (si vous utilisez VS Code ou Jupyter Lab) :
```bash
python -m ipykernel install --user --name=cinedata --display-name "Python (cinedata)"
```
Puis, dans votre notebook, sélectionnez le kernel "Python (cinedata)" dans le sélecteur en haut à droite.

**6. Vérifier que le bon environnement est utilisé**, dans une cellule de notebook :
```python
import sys
print(sys.executable)
```
Le chemin affiché doit pointer vers votre dossier `venv` — sinon les imports échoueront même si l'installation a fonctionné.

**7. Désactiver le venv en fin de session :**
```bash
deactivate
```

### Checklist de fin de journée

- [ ] Dépôt Git initialisé, `.gitignore` en place avant toute clé API, premier commit poussé sur GitHub
- [ ] venv créé et activé
- [ ] `requirements.txt` installé sans erreur
- [ ] Kernel Jupyter dédié créé et sélectionné (si notebook utilisé)
- [ ] `sys.executable` confirme que le bon environnement est actif

---

## Ressource complémentaire

**[Learn Git Branching](https://learngitbranching.js.org/)** — outil interactif et visuel (disponible en français), pour consolider la notion de commit et de branche en dehors de l'atelier. Les 4-5 premiers niveaux de la section "Introduction Sequence" suffisent largement pour ce projet.
