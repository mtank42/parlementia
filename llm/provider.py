"""Couche d'abstraction LLM.

Objectif : pouvoir changer de modèle en modifiant UNE seule variable
d'environnement (`LLM_PROVIDER`), sans toucher au code des agents.

Chaque provider expose la même méthode :

    complete(system: str, user: str, temperature: float = 0.4) -> str

Providers disponibles :
    - mistral : API Mistral (La Plateforme), nécessite MISTRAL_API_KEY
    - ollama  : modèle Mistral local (aucune clé, souverain, hors-ligne)
    - mock    : réponses simulées, aucune dépendance réseau (démo de secours)
"""
from __future__ import annotations

import json

import httpx

from config import (
    LLM_PROVIDER,
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
    OLLAMA_HOST,
    OLLAMA_MODEL,
)


class LLMProvider:
    """Interface commune à tous les fournisseurs de modèle."""

    name = "base"

    def complete(self, system: str, user: str, temperature: float = 0.4) -> str:
        raise NotImplementedError


class MistralProvider(LLMProvider):
    name = "mistral"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.url = "https://api.mistral.ai/v1/chat/completions"

    def complete(self, system: str, user: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=120) as client:
            resp = client.post(self.url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, host: str, model: str) -> None:
        self.host = host.rstrip("/")
        self.model = model

    def complete(self, system: str, user: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        with httpx.Client(timeout=300) as client:
            resp = client.post(f"{self.host}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["message"]["content"].strip()


class MockProvider(LLMProvider):
    """Réponses simulées pour faire tourner l'app sans réseau ni clé.

    Rend un texte plausible et, si l'agent demande du JSON (scores ODD),
    renvoie un JSON valide pour que le radar s'affiche quand même.
    """

    name = "mock"

    def complete(self, system: str, user: str, temperature: float = 0.4) -> str:
        if "JSON" in system or "json" in user.lower():
            odd = {str(i): 50 + (i * 7) % 45 for i in range(1, 18)}
            return json.dumps({"scores": odd, "commentaire": "(données simulées)"})
        return (
            "[Réponse simulée — provider 'mock' actif, aucun LLM appelé]\n\n"
            "Ceci est un texte de démonstration généré localement pour illustrer "
            "le pipeline Parlementia. Configurez MISTRAL_API_KEY ou lancez Ollama "
            "pour obtenir une analyse réelle."
        )


_CACHED: LLMProvider | None = None


def _build() -> LLMProvider:
    choice = LLM_PROVIDER

    if choice == "auto":
        if MISTRAL_API_KEY:
            choice = "mistral"
        else:
            choice = "ollama"

    if choice == "mistral":
        if not MISTRAL_API_KEY:
            raise RuntimeError(
                "LLM_PROVIDER=mistral mais MISTRAL_API_KEY est vide (voir .env)."
            )
        return MistralProvider(MISTRAL_API_KEY, MISTRAL_MODEL)

    if choice == "ollama":
        return OllamaProvider(OLLAMA_HOST, OLLAMA_MODEL)

    if choice == "mock":
        return MockProvider()

    raise RuntimeError(f"LLM_PROVIDER inconnu : {choice!r}")


def get_provider() -> LLMProvider:
    """Retourne l'instance de provider (singleton)."""
    global _CACHED
    if _CACHED is None:
        _CACHED = _build()
    return _CACHED
