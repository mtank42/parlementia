"""Orchestrateur du pipeline Parlementia.

Enchaîne les agents 2 à 9 sur un contexte partagé (`ctx`). L'agent 1 (phase
conversationnelle) est géré en amont par le serveur ; ses réponses de cadrage
et sa reformulation sont déjà présentes dans `ctx` au lancement.

`run_pipeline` est un générateur : il produit un événement par étape, ce qui
permet au serveur d'afficher la progression en direct.
"""
from __future__ import annotations

from typing import Iterator

from agents.agent2_diagnostic import Agent2Diagnostic
from agents.agent3_donnees import Agent3Donnees
from agents.agent4_prospective import Agent4Prospective
from agents.agent5_odd import Agent5AnalyseODD
from agents.agent6_evaluation import Agent6Evaluation
from agents.agent7_arbitrages import Agent7Arbitrages
from agents.agent8_contre_analyse import Agent8ContreAnalyse
from agents.agent9_synthese import Agent9Synthese

# (clé de contexte, libellé affiché, classe d'agent)
PIPELINE = [
    ("diagnostic", "Diagnostic systémique & juridique", Agent2Diagnostic),
    ("donnees", "Recueil des données (data.gouv.fr)", Agent3Donnees),
    ("prospective", "Scénarios prospectifs", Agent4Prospective),
    ("analyse_odd", "Analyse au prisme des ODD", Agent5AnalyseODD),
    ("evaluation", "Évaluation scientifique", Agent6Evaluation),
    ("arbitrages", "Recommandations d'arbitrage", Agent7Arbitrages),
    ("contre_analyse", "Contre-analyse experte", Agent8ContreAnalyse),
    ("synthese", "Synthèse parlementaire", Agent9Synthese),
]


def run_pipeline(ctx: dict) -> Iterator[dict]:
    """Exécute les agents 2→9. Émet un événement par étape.

    Événement : {"step": <index>, "key": ..., "label": ..., "content": ...}
    """
    for i, (key, label, cls) in enumerate(PIPELINE, start=1):
        agent = cls()
        result = agent.run(ctx)
        ctx[key] = result
        yield {"step": i, "key": key, "label": label, "content": result}
