"""
Datamodellen
=============
Alle kernbegrippen van het systeem op één plek, als dataclasses in plaats
van losse dicts. Voordeel: je editor geeft autocomplete en waarschuwt bij
typefouten (bv. `brand.naam` i.p.v. `brand.name`), en dit bestand is in
z'n geheel de "woordenlijst" van het project — lees dit eerst als je wilt
begrijpen hoe alles in elkaar steekt.
"""

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    """
    De vijf soorten vragen uit de meetmethodiek. Gebruik deze bij het
    samenstellen van een promptset per klant (zie clients/_template.py).
    """
    GENERIEK = "generiek"                  # "Wat is de beste X voor Y?"
    VERGELIJKEND = "vergelijkend"          # "Vergelijk de bekendste aanbieders van X"
    CONCURRENT = "concurrent-alternatief"  # "Alternatieven voor [concurrent]?"
    PERSONA = "persona-specifiek"          # uitgebreide, situatie-beschrijvende vraag
    PROBLEEM = "probleem-eerst"            # pijnpunt, zonder productcategorie te noemen


@dataclass
class Brand:
    """Het merk dat je meet."""
    name: str
    domain: str
    aliases: list[str] = field(default_factory=list)


@dataclass
class Competitor:
    """Een concurrent om tegen af te zetten (aandeel van stem)."""
    name: str
    domain: str


@dataclass
class Prompt:
    """Eén vaste meetvraag, met het type vraag erbij voor latere analyse."""
    text: str
    category: Category = Category.GENERIEK


@dataclass
class ClientConfig:
    """De volledige configuratie van één klant, geladen uit clients/<slug>.py."""
    slug: str
    brand: Brand
    competitors: list[Competitor]
    prompts: list[Prompt]


@dataclass
class QueryResult:
    """Het resultaat van één (model, prompt)-combinatie uit een meetrun."""
    model: str
    prompt: str
    category: str
    timestamp: str
    brand_mentioned: bool
    brand_cited_with_link: bool
    competitors_mentioned: list[str]
    cited_domains: list[str]
    raw_text: str


@dataclass
class TechnicalAudit:
    """Resultaat van de technische fundament-check (technical_audit.py)."""
    domain: str
    robots_txt_found: bool
    blocked_crawlers: list[str]
    likely_client_side_rendered: bool | None
    sitemap_found: bool
    has_json_ld: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class ScoreReport:
    """De uiteindelijke "uitslag" van de meettest — dit toon je aan een klant."""
    brand: str
    technical_score: float
    mention_rate: float
    citation_rate: float
    share_of_voice: float
    composite_score: float
    grade: str
    category_breakdown: dict[str, float] = field(default_factory=dict)
