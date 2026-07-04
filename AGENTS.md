# AGENTS.md — Guide pour agents IA / contributeurs

Ce document permet à un LLM (ou un développeur) de reprendre le projet
**Parlementia** sans contexte préalable. Il décrit l'architecture, le contrat
de chaque agent, le flux de données, les conventions et les points d'extension.

> Note pour Claude Code : ce fichier fait aussi office de `CLAUDE.md`.

---

## 1. Objectif du projet

Parlementia est un **copilote de prospective parlementaire** (projet de
hackathon Assemblée nationale). À partir de l'intention politique d'un·e
député·e, il :

1. cadre la demande (5 questions),
2. réalise un **diagnostic systémique + juridique**,
3. recueille des **données publiques** (data.gouv.fr),
4. construit **3 scénarios prospectifs** à ≤ 10 ans (réaliste / optimiste / pessimiste),
5. évalue leur **impact sur les 17 ODD** (Objectifs de Développement Durable),
6. produit une **synthèse parlementaire** avec **diagrammes radar ODD** par scénario.

Posture imposée : **neutralité politique**, distinction faits/hypothèses/opinions,
niveaux de confiance, sources de référence (GIEC, INSEE, ADEME, OCDE, Cour des
comptes, Commission européenne, ONU). L'outil **éclaire**, il ne prescrit pas.

---

## 2. Stack & prérequis

- **Python 3.11+** (développé/testé avec 3.14). Backend **FastAPI** + **uvicorn**.
- HTTP : **httpx**. Config : **python-dotenv**. Aucune base de données.
- Front : **HTML/CSS/JS pur** (aucun framework, aucune dépendance CDN).
  Le radar ODD est généré en **SVG côté client** dans `static/app.js`.
- Dépendances : voir `requirements.txt`.

---

## 3. Arborescence

```
parlementia/
├── config.py               # ODD (17), 5 questions de cadrage, accueil, sélection provider
├── server.py               # FastAPI : routes, sessions, flux SSE
├── requirements.txt
├── .env.example            # modèle de config (copier en .env, JAMAIS committer .env)
├── llm/
│   ├── __init__.py         # expose get_provider()
│   └── provider.py         # couche LLM interchangeable (mistral | ollama | mock)
├── data/
│   ├── __init__.py         # expose search_datasets()
│   └── datagouv.py         # client API data.gouv.fr (+ cache + repli)
├── agents/                 # UN MODULE PAR AGENT
│   ├── base.py             # BaseAgent, CHARTE commune, helpers (cadrage_bloc, extract_json)
│   ├── agent1_comprehension.py
│   ├── agent2_diagnostic.py
│   ├── agent3_donnees.py
│   ├── agent4_prospective.py
│   ├── agent5_odd.py
│   ├── agent6_evaluation.py
│   ├── agent7_arbitrages.py
│   ├── agent8_contre_analyse.py
│   ├── agent9_synthese.py
│   └── orchestrator.py     # enchaîne les agents 2→9
├── static/                 # UI (index.html, style.css, app.js) aux couleurs de la République
└── launcher/               # lanceur macOS double-clic (run.sh, stop.sh, icône)
```

---

## 4. Flux de données (vue d'ensemble)

```
Navigateur ──POST /api/start──▶ serveur : crée session, renvoie accueil + Q1
        ◀── question 1..5 ── (POST /api/answer, une réponse à la fois)
        ── à la 5e réponse : Agent 1 (compréhension) ──▶ reformulation
        ──GET /api/analyze (SSE)──▶ orchestrateur : agents 2→9, une étape émise à la fois
        ◀── event "final" : {odd, odd_scores, scenarios, synthese} ──
Navigateur : rend les radars (SVG) + le document parlementaire (Markdown → HTML)
```

Tout transite par **un dictionnaire de contexte partagé `ctx`** (voir §6),
stocké par session en mémoire (`SESSIONS` dans `server.py`).

---

## 5. Contrat de chaque agent

Chaque agent hérite de `BaseAgent` (`agents/base.py`) :
- `role_system` : instruction spécifique (concaténée à `CHARTE`).
- `build_user_prompt(ctx)` : construit la requête (par défaut) **ou** l'agent
  surcharge `run(ctx)` s'il a une logique propre (appels multiples, parsing JSON,
  appel réseau).
- `run(ctx)` : renvoie une string ; l'orchestrateur la stocke dans `ctx[key]`.

| Agent | Fichier | Lit dans `ctx` | Écrit dans `ctx` | Particularité |
|------|---------|----------------|------------------|---------------|
| 1 | `agent1_comprehension.py` | `cadrage` | `comprehension` | Appelé par le **serveur** (hors pipeline) |
| 2 | `agent2_diagnostic.py` | `cadrage`, `comprehension` | `diagnostic` | Expertise juridique (pas d'API Légifrance — signale les réf. à vérifier) |
| 3 | `agent3_donnees.py` | `cadrage` | `donnees`, **`datasets`** | `run()` surchargé : LLM → mots-clés JSON → API data.gouv.fr → commentaire |
| 4 | `agent4_prospective.py` | `cadrage`, `diagnostic`, `donnees` | `prospective`, **`scenarios`** | `run()` surchargé : **sortie JSON** (3 scénarios) parsée |
| 5 | `agent5_odd.py` | `cadrage`, `scenarios` | `analyse_odd`, **`odd_scores`** | `run()` surchargé : **JSON** {type→{ODD id→score 0-100}} pour les radars |
| 6 | `agent6_evaluation.py` | `cadrage`, `prospective`, `analyse_odd` | `evaluation` | — |
| 7 | `agent7_arbitrages.py` | `cadrage`, `analyse_odd`, `evaluation` | `arbitrages` | — |
| 8 | `agent8_contre_analyse.py` | `cadrage`, `arbitrages`, `evaluation` | `contre_analyse` | Posture critique (avocat du diable) |
| 9 | `agent9_synthese.py` | **tout** | `synthese` | Document final (plan imposé, Markdown) |

L'ordre du pipeline 2→9 est défini dans `orchestrator.py` (`PIPELINE`).

---

## 6. Schéma du contexte partagé `ctx`

```python
ctx = {
  # rempli par le serveur pendant la phase conversationnelle
  "cadrage": {
      "objectif": str, "leviers": str, "indicateurs": str,
      "territoire": str, "odd": str,
  },
  "q_index": int,                 # interne serveur

  "comprehension": str,           # agent 1
  "diagnostic": str,              # agent 2
  "donnees": str,                 # agent 3 (texte)
  "datasets": [                   # agent 3 (structuré) — liste de jeux data.gouv.fr
      {"title": str, "organization": str, "description": str, "url": str}, ...
  ],
  "prospective": str,             # agent 4 (texte)
  "scenarios": [                  # agent 4 (structuré)
      {"type": "realiste|optimiste|pessimiste", "titre": str,
       "horizon": str, "recit": str, "hypotheses": [str], "declencheurs": [str]}, ...
  ],
  "analyse_odd": str,             # agent 5 (texte)
  "odd_scores": {                 # agent 5 (structuré) — alimente les radars
      "realiste":  {1: int, ..., 17: int},   # scores 0-100, 50 = neutre
      "optimiste": {...}, "pessimiste": {...},
  },
  "evaluation": str,              # agent 6
  "arbitrages": str,              # agent 7
  "contre_analyse": str,          # agent 8
  "synthese": str,                # agent 9 (Markdown, document final)
}
```

**Règle importante** : si vous modifiez la clé lue/écrite par un agent, mettez à
jour l'agent producteur, l'agent consommateur ET ce tableau.

---

## 7. Couche LLM interchangeable (`llm/provider.py`)

Interface unique : `complete(system: str, user: str, temperature: float) -> str`.
On change de modèle avec **une seule variable** `LLM_PROVIDER` (dans `.env`) :

- `mistral` — API Mistral (La Plateforme). Requiert `MISTRAL_API_KEY`. Modèle via `MISTRAL_MODEL`.
- `ollama` — Mistral **local, sans clé, souverain** (`ollama run mistral`). `OLLAMA_HOST`, `OLLAMA_MODEL`.
- `mock` — réponses simulées, **aucun réseau** (démo de secours ; renvoie un JSON valide quand du JSON est attendu).
- `auto` — `mistral` si clé présente, sinon `ollama`.

`get_provider()` est un singleton. **Pour ajouter un fournisseur** : créer une
classe `LLMProvider` (attribut `name`, méthode `complete`) et l'enregistrer dans
`_build()`.

---

## 8. Client data.gouv.fr (`data/datagouv.py`)

- `search_datasets(query, page_size)` → liste normalisée (`title`, `organization`,
  `description`, `url`). **Aucune clé requise** (API publique).
- Cache mémoire par requête ; **repli** sur des jeux de référence (ADEME
  Transition(s) 2050) si l'API échoue → le pipeline ne casse jamais.

---

## 9. Serveur & endpoints (`server.py`)

| Méthode | Route | Rôle |
|--------|-------|------|
| GET | `/` | sert `static/index.html` |
| GET | `/api/config` | `{odd: [...], provider: "mistral"}` (métadonnées front) |
| POST | `/api/start` | crée une session → `{session_id, greeting, question, step, total}` |
| POST | `/api/answer` | `{session_id, answer}` → question suivante, ou `{done:true, comprehension}` à la 5e |
| GET | `/api/analyze?session_id=` | **flux SSE** : un event par agent, puis event `step:"final"` |

Sessions **en mémoire** (`SESSIONS`) : suffisant pour une démo mono-utilisateur.
Pour du multi-utilisateur/production → externaliser (Redis, etc.).
Les chemins statiques sont résolus via `BASE_DIR` (indépendant du répertoire de lancement).

---

## 10. Lancer le projet

### Développement
```bash
cd parlementia
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # renseigner MISTRAL_API_KEY, ou LLM_PROVIDER=ollama, ou =mock
uvicorn server:app --reload --port 8000
# → http://localhost:8000
```

### Lanceur macOS (double-clic)
`Parlementia.app` (bundle dans le dépôt) démarre le serveur en arrière-plan et
ouvre le navigateur, sans console. `launcher/run.sh` crée le venv + installe les
deps au 1er lancement. `Arrêter Parlementia.command` stoppe le serveur.
Reconstruire l'app : `osacompile -o Parlementia.app launcher/*.applescript` (le
script source de compilation n'est pas versionné ; voir `launcher/run.sh` pour la logique).

### Sans clé ni réseau
`LLM_PROVIDER=mock` fait tourner toute la chaîne avec des réponses simulées (utile pour tests UI/CI).

---

## 11. Conventions du code

- **Langue** : tout en **français** (prompts, commentaires, UI, sorties LLM).
- **Un module par agent** dans `agents/`, nommé `agentN_role.py`, classe `AgentNRole`.
- Les prompts système commencent par `RÔLE : …` et héritent de `CHARTE` (posture PARLEMENTIA).
- Sorties structurées : demander du **JSON strict** dans le prompt et parser avec
  `extract_json()` (`agents/base.py`), **toujours avec un repli** si le parsing échoue
  (ne jamais casser le pipeline).
- Couleurs République dans `static/style.css` : bleu `#000091`, rouge `#e1000f`, blanc.

---

## 12. Points d'extension courants

- **Ajouter un agent au pipeline** : créer `agents/agentX_*.py`, puis l'insérer dans
  `PIPELINE` (`orchestrator.py`) au bon rang avec sa clé `ctx`.
- **Changer de LLM** : `LLM_PROVIDER` (§7), ou ajouter un provider.
- **Nouvelle source de données** : ajouter un module dans `data/` sur le modèle de `datagouv.py`.
- **Modifier les radars** : `radarSVG()` dans `static/app.js` (17 axes, scores 0-100).

---

## 13. Limites connues / TODO (post-hackathon)

- **Agent 2 juridique** : raisonne sans API **Légifrance** → références à vérifier
  manuellement. Brancher une API juridique améliorerait la traçabilité.
- **Export du document** : actuellement via l'impression navigateur (bouton
  « Imprimer / PDF »). Un export PDF serveur (ex. WeasyPrint) reste à faire.
- **ISP (Indice de Soutenabilité Parlementaire)** — 6 dimensions (impact ODD,
  résilience, robustesse, équité, faisabilité, traçabilité) évoqué dans le cahier
  des charges : **non implémenté**, candidat naturel à un nouvel agent + affichage.
- **Sessions en mémoire** : non persistantes, mono-instance.
- **Sécurité** : le principe de moindre privilège (chaque agent ne reçoit que le
  strict nécessaire) n'est pas encore strictement appliqué — actuellement tous les
  agents partagent `ctx`.

---

## 14. Sécurité / secrets

- **Ne jamais committer `.env`** (déjà dans `.gitignore`). Utiliser `.env.example` comme modèle.
- La clé LLM se met uniquement dans `.env` local.
