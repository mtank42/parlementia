"""Agent 4 — Prospective : 3 scénarios de futurs possibles (≤ 10 ans).

Produit trois scénarios (réaliste/probable, optimiste/souhaitable, pessimiste)
découlant de la décision, à horizon 10 ans maximum, avec pour critère la
réalisation des ODD. Sortie structurée en JSON pour alimenter les agents 5/6
et les diagrammes radar.
"""
from __future__ import annotations

from agents.base import BaseAgent, cadrage_bloc, extract_json


class Agent4Prospective(BaseAgent):
    temperature = 0.6
    role_system = (
        "RÔLE : Agent prospectif. Construis exactement TROIS scénarios à "
        "horizon 10 ans maximum découlant de la décision, avec pour critère "
        "la réalisation des ODD : 'realiste' (probable), 'optimiste' "
        "(souhaitable) et 'pessimiste'. Réponds UNIQUEMENT en JSON valide :\n"
        "{\"scenarios\": [{\"type\": \"realiste|optimiste|pessimiste\", "
        "\"titre\": \"...\", \"horizon\": \"2035\", \"recit\": \"3-5 phrases\", "
        "\"hypotheses\": [\"...\"], \"declencheurs\": [\"...\"]}]}"
    )

    def run(self, ctx: dict) -> str:
        user = (
            "Demande :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            "Diagnostic systémique et juridique :\n"
            f"{ctx.get('diagnostic', '—')}\n\n"
            "Données disponibles :\n"
            f"{ctx.get('donnees', '—')}\n\n"
            "Génère les trois scénarios au format JSON demandé."
        )
        raw = self.llm.complete(self.system_prompt(), user, self.temperature)
        data = extract_json(raw) or {}
        scenarios = data.get("scenarios", [])

        # Normalisation + repli minimal pour ne jamais casser le pipeline.
        if not scenarios:
            scenarios = [
                {"type": t, "titre": f"Scénario {t}", "horizon": "2035",
                 "recit": "(non généré)", "hypotheses": [], "declencheurs": []}
                for t in ("realiste", "optimiste", "pessimiste")
            ]
        ctx["scenarios"] = scenarios

        blocs = []
        for s in scenarios:
            hyp = "; ".join(s.get("hypotheses", []))
            blocs.append(
                f"### {s.get('titre', s.get('type'))} "
                f"({s.get('type')}, horizon {s.get('horizon', '—')})\n"
                f"{s.get('recit', '')}\n\n*Hypothèses :* {hyp or '—'}"
            )
        return "\n\n".join(blocs)
