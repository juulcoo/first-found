"""
Score-berekening
==================
Combineert de technische fundament-check en de citatiemetingen tot één
vergelijkbaar cijfer 0-100 — de "uitslag" van de meettest die je in een
auditrapport aan een klant laat zien.

De gewichten hieronder zijn een startpunt, geen wetenschappelijke
waarheid — niemand publiceert een officiële formule hiervoor. Stel ze
gerust bij op basis van wat je in de praktijk ziet correleren met
daadwerkelijke klantresultaten (leads, omzet).
"""

import json

WEIGHTS = {
    "technical": 0.20,       # fundament: zonder dit werkt de rest niet
    "mention_rate": 0.30,    # wordt het merk ooit genoemd
    "citation_rate": 0.30,   # wordt het merk met een link geciteerd (sterker signaal)
    "share_of_voice": 0.20,  # hoe verhoudt dit zich tot de concurrentie
}


def technical_score(audit: dict) -> float:
    """0-100. Elke geblokkeerde crawler of ontbrekend basiselement kost punten."""
    score = 100.0
    blocks = audit.get("robots_txt", {}).get("blocks", {})
    blocked_count = sum(1 for v in blocks.values() if v)
    score -= blocked_count * 25  # een geblokkeerde AI-crawler is een harde showstopper
    if audit.get("rendering", {}).get("likely_client_side_rendered"):
        score -= 20
    if not audit.get("sitemap", {}).get("found"):
        score -= 5
    if not audit.get("schema", {}).get("has_json_ld"):
        score -= 5
    return max(0.0, min(100.0, score))


def citation_scores(records: list[dict]) -> dict:
    total = len(records)
    if total == 0:
        return {"mention_rate": 0.0, "citation_rate": 0.0, "share_of_voice": 0.0}

    mentioned = sum(1 for r in records if r["brand_mentioned"])
    cited = sum(1 for r in records if r["brand_cited_with_link"])

    brand_appearances = mentioned
    competitor_appearances = sum(len(r["competitors_mentioned"]) for r in records)
    total_appearances = brand_appearances + competitor_appearances
    sov = (brand_appearances / total_appearances * 100) if total_appearances else 0.0

    return {
        "mention_rate": mentioned / total * 100,
        "citation_rate": cited / total * 100,
        "share_of_voice": sov,
    }


def category_breakdown(records: list[dict]) -> dict[str, float]:
    """
    Mention rate per prompt-categorie (generiek, vergelijkend, etc.) —
    laat zien waar een merk sterk/zwak scoort, niet alleen hoe vaak in
    totaal. Handig om in een rapport te laten zien: "je scoort goed op
    generieke vragen maar wordt nooit genoemd als alternatief voor
    concurrent X".
    """
    by_category: dict[str, list[bool]] = {}
    for r in records:
        by_category.setdefault(r.get("category", "onbekend"), []).append(r["brand_mentioned"])
    return {
        cat: round(sum(hits) / len(hits) * 100, 1)
        for cat, hits in by_category.items()
    }


def composite_score(technical: float, citations: dict) -> float:
    return round(
        technical * WEIGHTS["technical"]
        + citations["mention_rate"] * WEIGHTS["mention_rate"]
        + citations["citation_rate"] * WEIGHTS["citation_rate"]
        + citations["share_of_voice"] * WEIGHTS["share_of_voice"],
        1,
    )


def grade(score: float) -> str:
    if score >= 80: return "A — sterk zichtbaar"
    if score >= 60: return "B — redelijk zichtbaar, ruimte voor groei"
    if score >= 40: return "C — beperkt zichtbaar"
    if score >= 20: return "D — nauwelijks zichtbaar"
    return "E — technisch fundament of citaties ontbreken vrijwel volledig"


def build_report(brand_name: str, records: list[dict], audit: dict) -> dict:
    tech = technical_score(audit)
    cites = citation_scores(records)
    total = composite_score(tech, cites)
    return {
        "brand": brand_name,
        "technical_score": round(tech, 1),
        "mention_rate": round(cites["mention_rate"], 1),
        "citation_rate": round(cites["citation_rate"], 1),
        "share_of_voice": round(cites["share_of_voice"], 1),
        "composite_score": total,
        "grade": grade(total),
        "category_breakdown": category_breakdown(records),
    }


def save_score_json(report: dict, output_path) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
