"""Serveur Parlementia (FastAPI).

Flux :
  1. /api/start      → crée une session, renvoie l'accueil + 1re question.
  2. /api/answer     → enregistre la réponse, renvoie la question suivante ;
                       à la 5e, lance l'agent 1 (compréhension) et la renvoie
                       pour validation (l'analyse ne démarre pas encore).
  3. /api/valider-comprehension → enregistre la reformulation validée (ou
                       corrigée par l'utilisateur) et autorise le lancement
                       de l'analyse.
  4. /api/analyze    → flux SSE : exécute les agents 2→9 et pousse chaque étape,
                       puis les scores ODD (pour les radars).

Sessions stockées en mémoire (suffisant pour une démo mono-utilisateur).
"""
from __future__ import annotations

import json
import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.agent1_comprehension import Agent1Comprehension
from agents.orchestrator import run_pipeline
from config import FRAMING_QUESTIONS, GREETING, ODD
from llm import get_provider

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="Parlementia")

# Ordre des clés de cadrage, aligné sur FRAMING_QUESTIONS.
CADRAGE_KEYS = ["objectif", "leviers", "indicateurs", "territoire", "odd"]

SESSIONS: dict[str, dict] = {}


class AnswerIn(BaseModel):
    session_id: str
    answer: str


class ComprehensionIn(BaseModel):
    session_id: str
    comprehension: str


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/config")
def get_config():
    """Métadonnées utiles au front (liste des ODD, provider actif)."""
    return {"odd": ODD, "provider": get_provider().name}


@app.post("/api/start")
def start():
    sid = uuid.uuid4().hex
    SESSIONS[sid] = {"cadrage": {}, "q_index": 0}
    return {
        "session_id": sid,
        "greeting": GREETING,
        "question": FRAMING_QUESTIONS[0],
        "key": CADRAGE_KEYS[0],
        "step": 1,
        "total": len(FRAMING_QUESTIONS),
    }


@app.post("/api/answer")
def answer(payload: AnswerIn):
    sess = SESSIONS.get(payload.session_id)
    if sess is None:
        raise HTTPException(404, "Session inconnue")

    idx = sess["q_index"]
    sess["cadrage"][CADRAGE_KEYS[idx]] = payload.answer.strip()
    idx += 1
    sess["q_index"] = idx

    # Encore des questions ?
    if idx < len(FRAMING_QUESTIONS):
        return {
            "done": False,
            "question": FRAMING_QUESTIONS[idx],
            "key": CADRAGE_KEYS[idx],
            "step": idx + 1,
            "total": len(FRAMING_QUESTIONS),
        }

    # Cadrage terminé → agent 1 (reformulation), soumise à validation.
    comprehension = Agent1Comprehension().run(sess)
    sess["comprehension"] = comprehension
    return {
        "done": True,
        "comprehension": comprehension,
    }


@app.post("/api/valider-comprehension")
def valider_comprehension(payload: ComprehensionIn):
    sess = SESSIONS.get(payload.session_id)
    if sess is None:
        raise HTTPException(404, "Session inconnue")

    texte = payload.comprehension.strip()
    if not texte:
        raise HTTPException(400, "La reformulation ne peut pas être vide")

    sess["comprehension"] = texte
    return {"message": "Merci. Je lance l'analyse prospective complète."}


@app.get("/api/analyze")
def analyze(session_id: str):
    sess = SESSIONS.get(session_id)
    if sess is None:
        raise HTTPException(404, "Session inconnue")

    def event_stream():
        try:
            for event in run_pipeline(sess):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            # Étape finale : scores ODD pour les diagrammes radar.
            final = {
                "step": "final",
                "odd": ODD,
                "odd_scores": sess.get("odd_scores", {}),
                "scenarios": sess.get("scenarios", []),
                "synthese": sess.get("synthese", ""),
            }
            yield f"data: {json.dumps(final, ensure_ascii=False)}\n\n"
        except Exception as exc:  # remonte l'erreur au front proprement
            err = {"step": "error", "message": str(exc)}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Fichiers statiques (JS/CSS). Monté après les routes /api.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
