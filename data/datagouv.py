"""Client léger de l'API publique data.gouv.fr.

On interroge l'API de recherche (aucune clé requise) et on ne récupère que
les métadonnées utiles : titre, organisation, description, URL. Un cache
mémoire évite de refaire deux fois la même requête pendant une session.

Doc API : https://doc.data.gouv.fr/api/reference/
"""
from __future__ import annotations

import httpx

_SEARCH_URL = "https://www.data.gouv.fr/api/1/datasets/"
_CACHE: dict[str, list[dict]] = {}

# Jeux de données de repli si l'API est indisponible pendant la démo.
_FALLBACK = [
    {
        "title": "Transition(s) 2050 — quatre scénarios pour la neutralité carbone",
        "organization": "ADEME",
        "description": "Scénarios prospectifs de l'ADEME pour atteindre la "
        "neutralité carbone en France à l'horizon 2050.",
        "url": "https://www.data.gouv.fr/datasets/transition-s-2050-quatre-"
        "scenarios-pour-atteindre-la-neutralite-carbone",
    },
]


def search_datasets(query: str, page_size: int = 5) -> list[dict]:
    """Recherche des jeux de données pertinents pour `query`.

    Retourne une liste de dictionnaires normalisés. En cas d'erreur réseau,
    retourne les jeux de repli pour que le pipeline ne s'interrompe pas.
    """
    key = f"{query}::{page_size}"
    if key in _CACHE:
        return _CACHE[key]

    params = {"q": query, "page_size": page_size}
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return _FALLBACK

    results: list[dict] = []
    for item in data.get("data", []):
        org = item.get("organization") or {}
        results.append(
            {
                "title": item.get("title", "(sans titre)"),
                "organization": org.get("name", "—"),
                "description": (item.get("description") or "")[:400],
                "url": item.get("page") or item.get("uri", ""),
            }
        )

    results = results or _FALLBACK
    _CACHE[key] = results
    return results
