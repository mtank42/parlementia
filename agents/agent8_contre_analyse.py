"""Agent 8 — Contre-analyse par un expert du sujet abordé.

Adopte une posture critique (avocat du diable) pour tester la robustesse des
conclusions : biais, angles morts, hypothèses fragiles, effets pervers.
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc


class Agent8ContreAnalyse(BaseAgent):
    temperature = 0.5
    role_system = (
        "RÔLE : Expert indépendant chargé de la contre-analyse. Adopte une "
        "posture critique rigoureuse : identifie les angles morts, les biais, "
        "les hypothèses fragiles, les effets pervers et externalités négatives "
        "non anticipées, les scénarios manquants et les points où les preuves "
        "sont insuffisantes. Reste factuel et constructif : ton but est de "
        "renforcer la qualité de la décision, pas de la disqualifier."
    )

    def build_user_prompt(self, ctx: dict) -> str:
        return (
            "Demande :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "Recommandations d'arbitrage (agent 7) :\n"
            f"{ctx.get('arbitrages', '—')}\n\n"
            "Évaluation scientifique (agent 6) :\n"
            f"{ctx.get('evaluation', '—')}\n\n"
            "Produis une contre-analyse critique et constructive."
        )
