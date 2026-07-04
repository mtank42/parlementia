# Parlementia — Copilote de prospective parlementaire

Outil d'aide à la décision pour les élus : à partir d'une intention politique,
il construit des **futurs souhaitables** et réalise le **backcasting**, en
cohérence avec les 17 **Objectifs de Développement Durable (ODD)**.

## Architecture — 9 agents + orchestrateur (un module par agent)

| Agent | Module | Rôle |
|------|--------|------|
| 1 | `agents/agent1_comprehension.py` | Compréhension : pose les 5 questions de cadrage, reformule l'intention |
| 2 | `agents/agent2_diagnostic.py` | Diagnostic systémique + expertise juridique (jurisprudence) |
| 3 | `agents/agent3_donnees.py` | Identification & recueil des données via l'API data.gouv.fr |
| 4 | `agents/agent4_prospective.py` | 3 scénarios à 10 ans (réaliste / optimiste / pessimiste) |
| 5 | `agents/agent5_odd.py` | Analyse des conséquences au prisme des 17 ODD (scores radar) |
| 6 | `agents/agent6_evaluation.py` | Évaluation scientifique de la réalisation des scénarios |
| 7 | `agents/agent7_arbitrages.py` | Recommandations d'arbitrage |
| 8 | `agents/agent8_contre_analyse.py` | Contre-analyse critique par un expert |
| 9 | `agents/agent9_synthese.py` | Synthèse & document parlementaire (+ radars ODD) |

L'orchestrateur (`agents/orchestrator.py`) enchaîne les agents 2→9 sur un
contexte partagé et émet une étape à la fois (affichage en direct).

## Couche LLM interchangeable

`llm/provider.py` expose une interface unique. On change de modèle avec la
**seule** variable `LLM_PROVIDER` :

- `mistral` — API Mistral (nécessite `MISTRAL_API_KEY`)
- `ollama` — Mistral local, **sans clé**, souverain (`ollama run mistral`)
- `mock` — réponses simulées, aucune dépendance réseau (démo de secours)
- `auto` — mistral si clé présente, sinon ollama

## Lancer

```bash
cd parlementia
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # puis renseigner MISTRAL_API_KEY (ou LLM_PROVIDER=ollama)
uvicorn server:app --reload --port 8000
```

Ouvrir http://localhost:8000

> ⚠️ Ne committez jamais `.env` (déjà dans `.gitignore`). Régénérez toute clé
> exposée.
