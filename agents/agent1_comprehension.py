"""Agent 1 — Compréhension de l'intention politique.

Gère la phase conversationnelle : il pose les 5 questions de cadrage puis
produit une reformulation structurée de la demande du député.
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc


class Agent1Comprehension(BaseAgent):
    role_system = (
        "RÔLE : Agent de compréhension. À partir des cinq réponses de cadrage "
        "du député, reformule précisément son intention : objectif poursuivi, "
        "périmètre, ODD prioritaires, territoire et populations, hypothèses "
        "implicites à valider. Sois concis (10 lignes max)."
    )

    def build_user_prompt(self, ctx: dict) -> str:
        return (
            "Réponses de cadrage du député :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "Reformule l'intention politique de façon structurée et signale "
            "les hypothèses implicites qui mériteraient d'être confirmées."
        )
