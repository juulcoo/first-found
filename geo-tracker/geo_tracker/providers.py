"""
API-providers
==============
Elke query_* functie hierin bevraagt één AI-platform met web
search/grounding ingeschakeld, en geeft altijd hetzelfde soort resultaat
terug: (antwoordtekst, lijst met geciteerde domeinen). Dat maakt ze
onderling inwisselbaar (zie PROVIDERS onderaan) en makkelijk uit te
breiden met een nieuw platform — kopieer het patroon van één van deze
functies. Nu ingebouwd: ChatGPT, Perplexity, Gemini en Claude.

BELANGRIJKE KANTTEKENING
-------------------------
Dit bevraagt de officiële API's, niet de consumenten-apps. Dat is de
enige schaalbare, reproduceerbare manier om dit te scripten, maar het is
een betrouwbare proxy-meting — geen exacte kopie van wat een individuele
gebruiker in de ChatGPT- of Perplexity-app te zien krijgt (die kan
persoonlijke geschiedenis meewegen). Check ook de actuele documentatie
van elke provider vóór gebruik: model- en tool-namen veranderen
regelmatig.
"""

import os
from urllib.parse import urlparse

# Check de actuele modelnamen in de documentatie van elke provider vóór
# gebruik.
OPENAI_MODEL = "gpt-5.1"
GEMINI_MODEL = "gemini-2.5-pro"
CLAUDE_MODEL = "claude-sonnet-5"


class MissingAPIKey(RuntimeError):
    """
    Losse foutklasse (geen SystemExit!) zodat een ontbrekende key voor
    één provider alleen díe provider laat falen — de rest van de run
    (andere modellen, andere prompts) gaat gewoon door. cmd_run in cli.py
    vangt dit netjes op per (model, prompt)-combinatie.
    """


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url


def _require_env(var: str, provider: str) -> str:
    """Geeft een begrijpelijke foutmelding i.p.v. een cryptische KeyError."""
    value = os.environ.get(var)
    if not value:
        raise MissingAPIKey(
            f"Ontbrekende API key: {var} (nodig voor {provider}). "
            f"Zet 'm in je .env-bestand — zie .env.example."
        )
    return value


def query_openai(prompt: str) -> tuple[str, list[str]]:
    """ChatGPT-achtige, web-grounded query via OpenAI's Responses API."""
    _require_env("OPENAI_API_KEY", "OpenAI/ChatGPT")
    from openai import OpenAI

    client = OpenAI()
    response = client.responses.create(
        model=OPENAI_MODEL,
        tools=[{"type": "web_search"}],
        input=prompt,
    )
    text = response.output_text
    domains = []
    for item in response.output:
        if getattr(item, "type", "") == "message":
            for content in item.content:
                for ann in getattr(content, "annotations", []) or []:
                    if getattr(ann, "type", "") == "url_citation":
                        domains.append(_extract_domain(ann.url))
    return text, domains


def query_perplexity(prompt: str) -> tuple[str, list[str]]:
    """Perplexity Sonar geeft citaties standaard mee in de response."""
    api_key = _require_env("PERPLEXITY_API_KEY", "Perplexity")
    import requests

    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "sonar", "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    domains = [_extract_domain(u) for u in data.get("citations", [])]
    return text, domains


def query_gemini(prompt: str) -> tuple[str, list[str]]:
    """Gemini met Google Search grounding ingeschakeld."""
    api_key = _require_env("GEMINI_API_KEY", "Gemini")
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL, tools="google_search_retrieval")
    response = model.generate_content(prompt)
    text = response.text
    domains = []
    try:
        for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
            if chunk.web and chunk.web.uri:
                domains.append(_extract_domain(chunk.web.uri))
    except (AttributeError, IndexError):
        pass
    return text, domains


def query_claude(prompt: str) -> tuple[str, list[str]]:
    """
    Web-grounded query via Claude's eigen web search tool. Let op: je
    organisatie-beheerder moet web search eerst aanzetten in de Claude
    Console (Settings → Privacy) — zonder dat staat de tool wel in de
    request maar krijg je nooit citaties terug.
    """
    api_key = _require_env("ANTHROPIC_API_KEY", "Claude")
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    text_parts = []
    domains = []
    for block in response.content:
        if getattr(block, "type", "") == "text":
            text_parts.append(block.text)
            for citation in getattr(block, "citations", None) or []:
                if getattr(citation, "type", "") == "web_search_result_location":
                    domains.append(_extract_domain(citation.url))
    return "".join(text_parts), domains


# Centraal register: nieuw platform toevoegen = functie schrijven + hier
# één regel toevoegen. De rest van het systeem hoeft niets te weten van
# welke platforms er precies bestaan.
PROVIDERS = {
    "chatgpt": query_openai,
    "perplexity": query_perplexity,
    "gemini": query_gemini,
    "claude": query_claude,
}
