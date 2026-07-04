"""Agent 9 — Synthèse et rédaction du document parlementaire.

Agrège tout le pipeline en un document structuré (format PARLEMENTIA), prêt à
être remis à un député. Les diagrammes radar ODC sont ajoutés par l'interface
à partir des scores de l'agent 5 (ctx['odd_scores']).
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc


class Agent9Synthese(BaseAgent):
    temperature = 0.3
    role_system = (
        "RÔLE : Rédacteur du document parlementaire. Rédige une synthèse "
        "structurée et directement exploitable, dans cet ordre :\n"
        "1. Résumé exécutif (une page max)\n"
        "2. Vision du futur souhaitable\n"
        "3. ODD retenus et justification\n"
        "4. Les trois scénarios (réaliste, optimiste, pessimiste)\n"
        "5. Backcasting : vision cible puis étapes 2035 → aujourd'hui\n"
        "6. Mesures publiques prioritaires\n"
        "7. Parties prenantes\n"
        "8. Indicateurs de suivi (KPI)\n"
        "9. Principaux risques et arbitrages\n"
        "Utilise le Markdown (titres ##, listes). Reste neutre et sourcé."
    )

    def build_user_prompt(self, ctx: dict) -> str:
        return (
            "Cadrage du député :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "=== Matériaux du pipeline ===\n"
            f"[Compréhension]\n{ctx.get('comprehension', '—')}\n\n"
            f"[Diagnostic systémique et juridique]\n{ctx.get('diagnostic', '—')}\n\n"
            f"[Données data.gouv.fr]\n{ctx.get('donnees', '—')}\n\n"
            f"[Scénarios prospectifs]\n{ctx.get('prospective', '—')}\n\n"
            f"[Analyse ODD]\n{ctx.get('analyse_odd', '—')}\n\n"
            f"[Évaluation scientifique]\n{ctx.get('evaluation', '—')}\n\n"
            f"[Arbitrages]\n{ctx.get('arbitrages', '—')}\n\n"
            f"[Contre-analyse]\n{ctx.get('contre_analyse', '—')}\n\n"
            "Rédige le document parlementaire final selon le plan imposé."
        )
