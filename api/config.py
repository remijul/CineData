"""
config.py
Chargement de la configuration du projet pour l'API.

Chemins calculés à partir de l'emplacement de ce fichier (__file__), pas du
répertoire courant : l'API doit fonctionner qu'on la lance depuis la racine
du projet ou depuis un autre dossier (même piège que rencontré avec les
chemins relatifs dans les notebooks).
"""

from pathlib import Path
import yaml

RACINE_PROJET = Path(__file__).resolve().parent.parent


def charger_config():
    """Charge config.yaml à la racine du projet."""
    chemin_config = RACINE_PROJET / "config.yaml"
    with open(chemin_config, "r", encoding="utf-8") as fichier:
        return yaml.safe_load(fichier)


CONFIG = charger_config()

CHEMIN_DB = RACINE_PROJET / CONFIG["database"]["chemin"]
CHEMIN_SQL = RACINE_PROJET / Path(CONFIG["database"]["schema"]).parent