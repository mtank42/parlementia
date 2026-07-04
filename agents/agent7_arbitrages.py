"""Agent 7 — Recommandations d'arbitrage.

Hiérarchise des recommandations mesurables, réversibles et compatibles avec
les ODD, en identifiant gagnants, perdants et compromis possibles.
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc


class Agent7Arbitrages(BaseAgent):
    role_system = (
        "RÔLE : Conseiller en arbitrage. Propose des recommandations "
        "hiérarchisées, argumentées, mesurables, réversibles et évaluables, "
        "compatibles avec les ODD prioritaires. Identifie les gagnants, les "
        "perdants, les groupes vulnérables, les synergies et les arbitrages "
        "entre ODD. Présente les arguments favorables ET défavorables sans "
        "trancher, en indiquant la robustesse des preuves. Tu éclaires, tu "
        "ne prescris pas."
    )

    def build_user_prompt(self, ctx: dict) -> str:
        return (
            "Demande :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "Analyse ODD :\n"
            f"{ctx.get('analyse_odd', '—')}\n\n"
            "Évaluation scientifique :\n"
            f"{ctx.get('evaluation', '—')}\n\n"
            "Propose les arbitrages et recommandations hiérarchisées."
        )
