"""Agent 6 — Évaluation scientifique de la réalisation des 3 scénarios.

Estime la plausibilité de chaque scénario, la robustesse des preuves et les
niveaux de confiance, en s'appuyant sur les sources de référence.
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc


class Agent6Evaluation(BaseAgent):
    role_system = (
        "RÔLE : Évaluateur scientifique. Pour chacun des trois scénarios, "
        "estime la probabilité de réalisation, la robustesse des preuves "
        "(hiérarchie : littérature évaluée par les pairs, GIEC, INSEE, ADEME, "
        "OCDE, Cour des comptes, Commission européenne, ONU), les signaux "
        "faibles et les facteurs déterminants. Indique un niveau de confiance "
        "(Très élevé / Élevé / Moyen / Faible) et distingue clairement faits, "
        "hypothèses et incertitudes."
    )

    def build_user_prompt(self, ctx: dict) -> str:
        return (
            "Demande :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "Scénarios (agent 4) :\n"
            f"{ctx.get('prospective', '—')}\n\n"
            "Analyse ODD (agent 5) :\n"
            f"{ctx.get('analyse_odd', '—')}\n\n"
            "Évalue scientifiquement la réalisation de chaque scénario."
        )
