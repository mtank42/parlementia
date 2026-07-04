"""Configuration centrale de Parlementia.

Toutes les constantes partagées (provider LLM, liste des ODD, questions de
cadrage, textes d'accueil) sont regroupées ici pour rester facilement
modifiables pendant le hackathon.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# --- Sélection du LLM ------------------------------------------------------
# "auto" choisit mistral (si clé) > ollama > mock.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# --- Les 17 Objectifs de Développement Durable -----------------------------
# id = numéro officiel ONU ; short = étiquette courte pour le radar.
ODD = [
    {"id": 1, "short": "Pauvreté", "label": "Pas de pauvreté"},
    {"id": 2, "short": "Faim", "label": "Faim zéro"},
    {"id": 3, "short": "Santé", "label": "Bonne santé et bien-être"},
    {"id": 4, "short": "Éducation", "label": "Éducation de qualité"},
    {"id": 5, "short": "Égalité F/H", "label": "Égalité entre les sexes"},
    {"id": 6, "short": "Eau", "label": "Eau propre et assainissement"},
    {"id": 7, "short": "Énergie", "label": "Énergie propre et abordable"},
    {"id": 8, "short": "Travail", "label": "Travail décent et croissance"},
    {"id": 9, "short": "Industrie", "label": "Industrie, innovation, infrastructure"},
    {"id": 10, "short": "Inégalités", "label": "Inégalités réduites"},
    {"id": 11, "short": "Villes", "label": "Villes et communautés durables"},
    {"id": 12, "short": "Consommation", "label": "Consommation responsable"},
    {"id": 13, "short": "Climat", "label": "Lutte contre le changement climatique"},
    {"id": 14, "short": "Vie aquatique", "label": "Vie aquatique"},
    {"id": 15, "short": "Vie terrestre", "label": "Vie terrestre"},
    {"id": 16, "short": "Institutions", "label": "Paix, justice, institutions efficaces"},
    {"id": 17, "short": "Partenariats", "label": "Partenariats pour les objectifs"},
]

# --- Questions de cadrage posées par l'agent 1 -----------------------------
FRAMING_QUESTIONS = [
    "Quel est l'objectif principal de votre intervention politique ou législative ?",
    "Quels sont vos principaux leviers d'action (loi, budget, réglementation, "
    "partenariats, collectivités, etc.) ?",
    "Comment saurez-vous, dans cinq ans, que cette politique est une réussite ? "
    "Quels indicateurs utiliseriez-vous ?",
    "Quel territoire et quelles populations sont concernés ?",
    "Parmi les 17 Objectifs de Développement Durable, quels sont les 3 à 5 ODD "
    "que vous souhaitez placer au cœur de votre vision ?",
]

GREETING = (
    "Bonjour, je suis **Parlementia**, votre copilote de prospective parlementaire. "
    "Je vous aide à construire des futurs souhaitables et à réaliser le backcasting "
    "de vos décisions, en cohérence avec les 17 Objectifs de Développement Durable. "
    "Je reste strictement neutre : je n'éclaire pas pour convaincre, mais pour décider.\n\n"
    "Pour commencer, j'ai besoin de cerner votre intention."
)
