"""Agent 2 — Diagnostic systémique + expertise juridique.

Affine la demande via une cartographie systémique (causes, conséquences,
boucles de rétroaction) et identifie la jurisprudence et le cadre juridique
pertinents (constitutionnel, législatif, droit européen).
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc


class Agent2Diagnostic(BaseAgent):
    role_system = (
        "RÔLE : Agent de diagnostic systémique doté d'une expertise juridique. "
        "1) Cartographie systémique : causes, conséquences, boucles de "
        "rétroaction, effets indirects, parties prenantes clés. "
        "2) Cadre juridique : identifie les textes, la jurisprudence pertinente "
        "(Conseil constitutionnel, Conseil d'État, CJUE, CEDH), les risques "
        "constitutionnels et la compatibilité avec le droit de l'Union. "
        "Précise ton niveau de confiance. IMPORTANT : sans accès à une base "
        "juridique en temps réel, signale explicitement quand une référence "
        "doit être vérifiée sur Légifrance."
    )

    def build_user_prompt(self, ctx: dict) -> str:
        return (
            "Cadrage du député :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "Reformulation de l'agent 1 :\n"
            f"{ctx.get('comprehension', '—')}\n\n"
            "Produis : (a) une cartographie systémique synthétique, puis "
            "(b) une analyse juridique (textes, jurisprudence, risques "
            "constitutionnels et compatibilité européenne)."
        )
