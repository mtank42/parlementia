"""Socle commun à tous les agents.

Un agent = une identité PARLEMENTIA (posture neutre, factuelle, sourcée) +
un rôle spécialisé (système) + une méthode `run` qui construit le prompt
utilisateur à partir du contexte partagé et appelle le LLM.
"""
from __future__ import annotations

import json
import re

from llm import get_provider

# Charte commune injectée dans tous les agents (extrait du prompt PARLEMENTIA).
CHARTE = (
    "Tu es PARLEMENTIA, conseiller stratégique indépendant au service des "
    "députés. Tu es politiquement neutre, tu ne cherches jamais à convaincre. "
    "Tu distingues strictement faits, hypothèses et opinions ; tu explicites "
    "tes incertitudes et un niveau de confiance ; tu privilégies les sources "
    "de référence (GIEC, INSEE, ADEME, OCDE, Cour des comptes, Commission "
    "européenne, ONU). Tu raisonnes en cohérence avec les 17 Objectifs de "
    "Développement Durable. Réponses synthétiques, claires, exploitables par "
    "un député ou son équipe."
)


class BaseAgent:
    role_system = ""       # instruction spécifique de l'agent
    temperature = 0.4

    def __init__(self) -> None:
        self.llm = get_provider()

    def system_prompt(self) -> str:
        return f"{CHARTE}\n\n{self.role_system}"

    def build_user_prompt(self, ctx: dict) -> str:
        """À surcharger : construit la requête à partir du contexte."""
        raise NotImplementedError

    def run(self, ctx: dict) -> str:
        prompt = self.build_user_prompt(ctx)
        return self.llm.complete(self.system_prompt(), prompt, self.temperature)


def cadrage_bloc(ctx: dict) -> str:
    """Formate les 5 réponses de cadrage pour les injecter dans un prompt."""
    answers = ctx.get("cadrage", {})
    lignes = [
        f"- Objectif : {answers.get('objectif', '—')}",
        f"- Leviers d'action : {answers.get('leviers', '—')}",
        f"- Indicateurs de succès à 5 ans : {answers.get('indicateurs', '—')}",
        f"- Territoire et populations : {answers.get('territoire', '—')}",
        f"- ODD prioritaires : {answers.get('odd', '—')}",
    ]
    return "\n".join(lignes)


def extract_json(text: str) -> dict | None:
    """Extrait le premier objet JSON présent dans un texte LLM."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
