"""
Klantconfiguratie-sjabloon
===========================
Kopieer dit bestand naar clients/<slug>.py — gebruik een korte, duidelijke
slug in kleine letters met underscores (bv. "groningen_zonnepanelen").
Deze slug wordt ook gebruikt in alle bestandsnamen in data/, dus kies 'm
zorgvuldig en verander 'm later niet meer (anders lijkt het net alsof je
met een nieuwe klant begint).

Bestandsnamen die niet met een underscore beginnen, tellen mee als
klant — dit bestand (met _ ervoor) en __init__.py worden dus genegeerd
door `python main.py list`.
"""

from geo_tracker.models import Brand, Category, Competitor, Prompt

BRAND = Brand(
    name="Voorbeeldbedrijf B.V.",
    domain="voorbeeldbedrijf.nl",
    aliases=["Voorbeeldbedrijf", "Voorbeeldbedrijf.nl"],
)

COMPETITORS = [
    Competitor(name="Concurrent A", domain="concurrenta.nl"),
    Competitor(name="Concurrent B", domain="concurrentb.nl"),
]

# Bouw de promptset op uit de vijf categorieën (zie geo_tracker/models.py
# voor de uitleg per categorie). Vuistregel: 20-50 prompts, gehaald uit
# echte klantgesprekken/reviews/zoekwoorden, nooit de merknaam zelf erin.
PROMPTS = [
    Prompt("Wat is de beste [categorie] voor [doelgroep] in Nederland?", Category.GENERIEK),
    Prompt("Vergelijk de bekendste aanbieders van [categorie].", Category.VERGELIJKEND),
    Prompt("Wat zijn goede alternatieven voor [Concurrent A]?", Category.CONCURRENT),
    Prompt("Ik ben [persona/situatie] en zoek [behoefte], wat raad je aan?", Category.PERSONA),
    Prompt("Ik loop tegen [probleem] aan, wat kan ik hieraan doen?", Category.PROBLEEM),
]
