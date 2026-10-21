"""
assistant_llm.py
Rédige, avec un LLM (Mistral), une recommandation argumentée à partir des
films déjà choisis par le moteur de similarité (moteur_recommandation.py).

Le LLM ne choisit rien : il commente une liste qu'on lui fournit. Le calcul
de similarité reste déterministe et gratuit ; seul le commentaire passe par
un service externe, avec ses quotas, sa latence et ses pannes possibles.

Ce module ne connaît pas HTTP : en cas de problème il lève ErreurLLM, et c'est
la route (routers/recommendation.py) qui la traduit en réponse 503.
"""

import os
import time

from dotenv import load_dotenv

from config import RACINE_PROJET, CONFIG

try:
    from mistralai.client import Mistral   # SDK 2.x
except ImportError:
    from mistralai import Mistral          # SDK 1.x

# La clé est lue dans le .env à la racine du projet (chemin calculé, pas
# relatif au dossier de lancement), jamais écrite dans le code.
load_dotenv(RACINE_PROJET / ".env")

CONFIG_LLM = CONFIG["llm"]
MODELE = CONFIG_LLM["modele"]
TEMPERATURE = CONFIG_LLM["temperature"]
MAX_TOKENS = CONFIG_LLM["max_tokens"]
MAX_TENTATIVES = CONFIG_LLM.get("max_tentatives", 3)
PAUSE_INITIALE = CONFIG_LLM.get("pause_initiale", 2.0)

MESSAGE_SYSTEME = (
    "Tu es un critique de cinéma qui recommande des films de façon "
    "argumentée et concise."
)

_client = None


class ErreurLLM(Exception):
    """Le service LLM n'a pas pu fournir de réponse exploitable."""


def obtenir_client():
    """
    Crée le client Mistral au premier besoin (et non à l'import) : l'API
    démarre et sert /recommendation même si la clé est absente ; seule la
    route enrichie échoue, avec un message clair.
    """
    global _client
    if _client is None:
        cle = os.getenv("MISTRAL_API_KEY")
        if not cle:
            raise ErreurLLM("Clé MISTRAL_API_KEY absente : le service de recommandation enrichie n'est pas configuré.")
        _client = Mistral(api_key=cle)
    return _client


def construire_prompt(titre_source, candidats):
    """Même prompt que dans notebooks/enhanced_recommendation_demo.ipynb."""
    lignes = []
    for film in candidats:
        genres = ", ".join(film["genres"]) if film["genres"] else "genres non renseignés"
        acteurs = ", ".join(film["actors"][:3]) if film["actors"] else "casting non renseigné"
        realisateurs = ", ".join(film["directors"]) if film["directors"] else "réalisateur non renseigné"
        lignes.append(
            f"- {film['title']} ({genres}) — réalisé par {realisateurs}, "
            f"avec {acteurs}, score de similarité {film['score_similarite']}"
        )
    liste_candidats = "\n".join(lignes)

    return (
        f"Un utilisateur vient d'apprécier le film \"{titre_source}\".\n"
        f"Voici {len(candidats)} films sélectionnés algorithmiquement pour leur proximité "
        f"de genre, casting et thématique :\n\n{liste_candidats}\n\n"
        f"Rédige une recommandation courte (150 mots maximum), sur le ton d'une critique "
        f"de cinéma argumentée : explique pourquoi ces films devraient plaire à quelqu'un "
        f"qui a aimé \"{titre_source}\", en t'appuyant uniquement sur les informations "
        f"ci-dessus (genre, réalisateur, acteurs). N'invente aucune information absente "
        f"de la liste."
    )


def generer_argumentaire(titre_source, candidats):
    """
    Retourne le texte de la recommandation, ou lève ErreurLLM.

    Différence avec la version du notebook : ici on ne renvoie pas None en
    cas d'erreur, on lève une exception. Le code appelant ne peut pas
    "oublier" de tester le résultat, et la route sait quoi répondre.

    Un 429 (limite de débit) est réessayé quelques fois avec une attente
    croissante ; toute autre erreur est remontée tout de suite.
    """
    client = obtenir_client()
    messages = [
        {"role": "system", "content": MESSAGE_SYSTEME},
        {"role": "user", "content": construire_prompt(titre_source, candidats)},
    ]

    pause = PAUSE_INITIALE
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            reponse = client.chat.complete(
                model=MODELE,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
        except Exception as erreur:
            code = getattr(erreur, "status_code", None)
            if code == 429:
                if tentative < MAX_TENTATIVES:
                    time.sleep(pause)
                    pause *= 2
                    continue
                raise ErreurLLM(
                    "Service de recommandation enrichie saturé ou quota atteint, réessayez dans quelques instants."
                ) from erreur
            raise ErreurLLM(
                "Service de recommandation enrichie momentanément indisponible."
            ) from erreur

        texte = reponse.choices[0].message.content
        if not texte:
            raise ErreurLLM("Le service de recommandation enrichie a renvoyé une réponse vide.")
        return texte

    raise ErreurLLM("Service de recommandation enrichie indisponible.")
