"""Agent 5 — Analyse des conséquences de chaque scénario au prisme des ODD.

Pour chaque scénario, attribue un score d'impact 0-100 sur chacun des 17 ODD
(50 = neutre, > 50 = renforcé, < 50 = fragilisé) et un commentaire.
Ces scores alimentent les diagrammes radar de l'agent 9.
"""
from __future__ import annotations

import json

from agents.base import BaseAgent, cadrage_bloc, extract_json
from config import ODD

_ODD_LISTE = "\n".join(f"{o['id']}. {o['label']}" for o in ODD)


class Agent5AnalyseODD(BaseAgent):
    role_system = (
        "RÔLE : Analyste ODD. Pour chaque scénario, évalue l'impact sur les 17 "
        "ODD par un score entier de 0 à 100 (50 = neutre, >50 = renforcé, "
        "<50 = fragilisé). Réponds UNIQUEMENT en JSON valide :\n"
        "{\"analyses\": {\"<type_scenario>\": {\"scores\": {\"1\": <int>, ..., "
        "\"17\": <int>}, \"commentaire\": \"synergies et arbitrages majeurs\"}}}\n"
        f"Liste des 17 ODD :\n{_ODD_LISTE}"
    )

    def run(self, ctx: dict) -> str:
        scenarios = ctx.get("scenarios", [])
        resume = "\n".join(
            f"- {s.get('type')} : {s.get('titre')} — {s.get('recit')}"
            for s in scenarios
        )
        user = (
            "Demande :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            f"Scénarios à évaluer :\n{resume}\n\n"
            "Évalue chaque scénario sur les 17 ODD au format JSON demandé."
        )
        raw = self.llm.complete(self.system_prompt(), user, self.temperature)
        data = extract_json(raw) or {}
        analyses = data.get("analyses", {})

        # Stockage normalisé des scores pour les radars (clé = type de scénario).
        scores_par_scenario: dict[str, dict[int, int]] = {}
        for s in scenarios:
            t = s.get("type", "")
            entry = analyses.get(t, {})
            raw_scores = entry.get("scores", {})
            clean = {}
            for o in ODD:
                try:
                    val = int(raw_scores.get(str(o["id"]), 50))
                except (TypeError, ValueError):
                    val = 50
                clean[o["id"]] = max(0, min(100, val))
            scores_par_scenario[t] = clean
        ctx["odd_scores"] = scores_par_scenario

        parts = []
        for s in scenarios:
            t = s.get("type", "")
            com = analyses.get(t, {}).get("commentaire", "—")
            parts.append(f"### {s.get('titre', t)}\n{com}")
        return "\n\n".join(parts) or "(analyse ODD non disponible)"
