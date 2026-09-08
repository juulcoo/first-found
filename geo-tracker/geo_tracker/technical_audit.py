"""
Technisch GEO-fundament
=========================
Voordat citaties er substantieel toe doen, moet het technische fundament
kloppen: kunnen AI-crawlers de site van de klant überhaupt bereiken en
lezen? Dit is een losstaande, statische check — geen API-kosten, en
verandert minder vaak dan citaties, dus periodiek (bv. elk kwartaal)
opnieuw draaien is genoeg.
"""

import json
from urllib.parse import urljoin

import requests

# Belangrijkste AI-crawlers om te checken. Controleer de actuele
# user-agent strings in de documentatie van elke provider vóór gebruik —
# deze kunnen wijzigen en providers voegen er soms nieuwe aan toe.
AI_CRAWLERS = {
    "OAI-SearchBot": "ChatGPT search (OpenAI) — de belangrijkste voor GEO",
    "GPTBot": "OpenAI training crawler (indirect relevant, geen search)",
    "PerplexityBot": "Perplexity",
    "ClaudeBot": "Anthropic/Claude",
    "Google-Extended": "Gemini / Google AI-features",
}


def _check_robots_txt(domain: str) -> dict:
    """
    Simpele parser die per user-agent blok checkt op 'Disallow: /'.
    Voor grootschalig gebruik: vervang dit door een echte robots.txt-
    parser (Python's ingebouwde urllib.robotparser, of het package
    `protego`) — deze aanpak dekt niet elke edge case (wildcards,
    meerdere user-agents per regel).
    """
    url = urljoin(domain, "/robots.txt")
    result = {"url": url, "found": False, "blocks": {}}
    try:
        resp = requests.get(url, timeout=10)
        result["found"] = resp.status_code == 200
        content = resp.text if result["found"] else ""
        blocks = {name: False for name in AI_CRAWLERS}
        current_agent = None
        for line in content.splitlines():
            line = line.strip()
            if line.lower().startswith("user-agent:"):
                current_agent = line.split(":", 1)[1].strip()
            elif line.lower().startswith("disallow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                for bot in AI_CRAWLERS:
                    if current_agent in (bot, "*") and path == "/":
                        blocks[bot] = True
        result["blocks"] = blocks
    except requests.RequestException as e:
        result["error"] = str(e)
    return result


def _check_server_rendering(domain: str) -> dict:
    """
    Ruwe heuristiek: weinig tekst in de body + veel <script>-tags wijst
    op client-side rendering, wat AI-crawlers (die geen JS uitvoeren)
    niets te lezen geeft. Voor een grondige check: render de pagina zelf
    met Playwright en vergelijk de zichtbare tekst met de ruwe HTML.
    """
    try:
        resp = requests.get(domain, timeout=10, headers={"User-Agent": "OAI-SearchBot"})
        html = resp.text
        script_tags = html.lower().count("<script")
        body_text_estimate = len(html.split("<body")[-1]) if "<body" in html.lower() else 0
        likely_csr = body_text_estimate < 500 and script_tags > 5
        return {"likely_client_side_rendered": likely_csr, "raw_html_length": len(html)}
    except requests.RequestException as e:
        return {"error": str(e), "likely_client_side_rendered": None}


def _check_sitemap(domain: str) -> dict:
    url = urljoin(domain, "/sitemap.xml")
    try:
        resp = requests.get(url, timeout=10)
        return {"url": url, "found": resp.status_code == 200}
    except requests.RequestException as e:
        return {"url": url, "found": False, "error": str(e)}


def _check_schema_markup(domain: str) -> dict:
    try:
        resp = requests.get(domain, timeout=10)
        return {"has_json_ld": "application/ld+json" in resp.text}
    except requests.RequestException as e:
        return {"error": str(e), "has_json_ld": None}


def run_audit(domain: str) -> dict:
    if not domain.startswith("http"):
        domain = f"https://{domain}"
    return {
        "domain": domain,
        "robots_txt": _check_robots_txt(domain),
        "rendering": _check_server_rendering(domain),
        "sitemap": _check_sitemap(domain),
        "schema": _check_schema_markup(domain),
    }


def save_audit_json(audit: dict, output_path) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
