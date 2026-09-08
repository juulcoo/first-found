"""
Analyse
========
Zet een ruwe AI-antwoordtekst + geciteerde domeinen om in een concreet
oordeel: wordt het merk genoemd, wordt het geciteerd met een link, welke
concurrenten komen voor. Puur tekstverwerking, geen API-aanroepen — apart
gehouden van providers.py zodat je dit onafhankelijk kunt testen en
verbeteren (bv. met betere tekstherkenning) zonder de API-code te raken.
"""

from .models import Brand, Competitor


def analyze(
    text: str,
    domains: list[str],
    brand: Brand,
    competitors: list[Competitor],
) -> dict:
    text_lower = text.lower()

    brand_mentioned = brand.name.lower() in text_lower or any(
        alias.lower() in text_lower for alias in brand.aliases
    )
    brand_cited_with_link = brand.domain in domains

    competitors_mentioned = [
        c.name for c in competitors
        if c.name.lower() in text_lower or c.domain in domains
    ]

    return {
        "brand_mentioned": brand_mentioned,
        "brand_cited_with_link": brand_cited_with_link,
        "competitors_mentioned": competitors_mentioned,
        "cited_domains": domains,
    }
