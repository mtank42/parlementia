"""Agent 3 — Identification et recueil des données (data.gouv.fr).

Étape 1 : le LLM propose des mots-clés de recherche ciblés (JSON).
Étape 2 : on interroge l'API data.gouv.fr (recherche dynamique, sans clé).
Étape 3 : le LLM commente la pertinence des jeux trouvés.

Le résultat brut (liste de datasets) est stocké dans le contexte pour les
agents suivants.
"""
from __future__ import annotations

import json

from agents.base import BaseAgent, cadrage_bloc, extract_json
from data import search_datasets


class Agent3Donnees(BaseAgent):
    role_system = (
        "RÔLE : Agent d'identification des données. À partir de la demande, "
        "tu détermines quelles données publiques seraient utiles puis tu "
        "commentes la pertinence des jeux de données réellement trouvés sur "
        "data.gouv.fr. Signale les manques et la fraîcheur des données."
    )

    def _keywords(self, ctx: dict) -> list[str]:
        system = (
            "Tu proposes des requêtes de recherche pour l'API data.gouv.fr. "
            "Réponds UNIQUEMENT en JSON : {\"requetes\": [\"...\", \"...\"]} "
            "avec 2 à 3 requêtes courtes (2-4 mots) en français."
        )
        user = f"Demande du député :\n{cadrage_bloc(ctx)}"
        raw = self.llm.complete(system, user, temperature=0.2)
        data = extract_json(raw) or {}
        reqs = data.get("requetes") or []
        if not reqs:
            # Repli : on dérive une requête de l'objectif.
            reqs = [ctx.get("cadrage", {}).get("objectif", "développement durable")]
        return reqs[:3]

    def run(self, ctx: dict) -> str:
        requetes = self._keywords(ctx)
        found: list[dict] = []
        seen = set()
        for q in requetes:
            for ds in search_datasets(q, page_size=4):
                if ds["url"] in seen:
                    continue
                seen.add(ds["url"])
                found.append(ds)

        ctx["datasets"] = found  # exploité par les agents suivants

        catalogue = json.dumps(found, ensure_ascii=False, indent=2)
        user = (
            "Demande :\n"
            f"{cadrage_bloc(ctx)}\n\n"
            f"Requêtes lancées sur data.gouv.fr : {requetes}\n\n"
            f"Jeux de données trouvés (JSON) :\n{catalogue}\n\n"
            "Commente leur pertinence pour l'analyse prospective, identifie "
            "les données manquantes et propose comment les mobiliser."
        )
        commentaire = self.llm.complete(self.system_prompt(), user, self.temperature)

        liste_md = "\n".join(
            f"- [{d['title']}]({d['url']}) — *{d['organization']}*" for d in found
        )
        return f"**Jeux de données identifiés :**\n{liste_md}\n\n{commentaire}"
