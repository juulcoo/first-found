"""
Klantconfiguratie: Reitdiep Zonnepanelen (Groningen)
======================================================
Volledig ingevuld voorbeeld om de hele stack mee uit te proberen.

- BRAND is fictief (Reitdiep Zonnepanelen), zodat je dit veilig als demo
  kunt draaien zonder een bestaande klant te impliceren.
- COMPETITORS zijn echte, publiek adverterende regionale spelers
  (gevonden via een korte zoekopdracht naar "zonnepanelen installateur
  Groningen") — vervang deze door de daadwerkelijke concurrenten zodra
  je dit voor een echte prospect inzet.
- PROMPTS zijn opgebouwd volgens de vijf categorieën, inclusief een paar
  plaatsnaam-varianten om lokale relevantie te testen.
"""

from geo_tracker.models import Brand, Category, Competitor, Prompt

BRAND = Brand(
    name="Reitdiep Zonnepanelen",
    domain="reitdiepzonnepanelen.nl",
    aliases=["Reitdiep Zonnepanelen", "Reitdiep Zonne-energie", "Reitdiep Zonnepanelen Groningen"],
)

COMPETITORS = [
    Competitor(name="ZPN Installaties", domain="zpn-installaties.nl"),
    Competitor(name="SUN-TAG Nederland", domain="sun-tag.nl"),
    Competitor(name="Jansen Elektrotechniek", domain="jansenelektrotechniek.nl"),
]

G = Category.GENERIEK
V = Category.VERGELIJKEND
C = Category.CONCURRENT
P = Category.PERSONA
X = Category.PROBLEEM

PROMPTS = [
    # --- Generiek / categorie -------------------------------------------
    Prompt("Wat is de beste zonnepanelen installateur in Groningen?", G),
    Prompt("Welk bedrijf kan ik het beste inschakelen voor zonnepanelen in de provincie Groningen?", G),
    Prompt("Wat kost het laten plaatsen van zonnepanelen door een lokale installateur in Groningen?", G),
    Prompt("Welke zonnepaneleninstallateurs zijn actief in en rond de stad Groningen?", G),
    Prompt("Hoe vind ik een gecertificeerde zonnepaneleninstallateur in Groningen?", G),
    Prompt("Welke zonnepanelenbedrijven in Noord-Nederland hebben de beste reputatie?", G),

    # --- Vergelijkend -----------------------------------------------------
    Prompt("Vergelijk de bekendste zonnepanelenbedrijven in Groningen met elkaar.", V),
    Prompt("Wat zijn de voor- en nadelen van een lokale installateur versus een landelijke keten voor zonnepanelen in Groningen?", V),
    Prompt("Welke zonnepaneleninstallateur in Groningen heeft de beste klantbeoordelingen?", V),

    # --- Concurrent-alternatief --------------------------------------------
    Prompt("Wat zijn goede alternatieven voor ZPN Installaties in de regio Groningen?", C),
    Prompt("Ik heb een offerte van SUN-TAG Nederland, welke andere installateurs in Groningen kan ik ter vergelijking benaderen?", C),
    Prompt("Welke lokale zonnepanelenbedrijven in Groningen zijn een goed alternatief voor de grote landelijke ketens?", C),

    # --- Persona / use-case-specifiek --------------------------------------
    Prompt("Ik woon in een jaren '30-woning in de stad Groningen en overweeg zonnepanelen, welke installateur kan me hierbij het beste adviseren?", P),
    Prompt("Ik heb een boerderij bij Winschoten met een groot dak, welk bedrijf in de omgeving kan grootschalige zonnepaneleninstallaties aan?", P),
    Prompt("Ik run een klein bedrijf in Hoogezand en wil zonnepanelen op ons bedrijfspand, wie kan ik het beste benaderen in de regio?", P),
    Prompt("Ik huur mijn woning in Groningen, kan ik toch zonnepanelen laten plaatsen en welk bedrijf helpt daarbij?", P),
    Prompt("We willen als VvE in Groningen gezamenlijk zonnepanelen aanschaffen, welk bedrijf heeft hier ervaring mee?", P),

    # --- Probleem-eerst (zonder productcategorie te noemen) ----------------
    Prompt("Mijn energierekening is de laatste tijd enorm gestegen, wat kan ik hieraan doen als huiseigenaar in Groningen?", X),
    Prompt("Ik wil minder afhankelijk zijn van het gasnet, wat zijn mijn opties in de provincie Groningen?", X),
    Prompt("Mijn dak in Groningen is oud en ik twijfel of het zonnepanelen kan dragen, wie kan dit beoordelen?", X),
    Prompt("Hoe zorg ik dat mijn woning in Groningen energieneutraal wordt?", X),

    # --- Lokale varianten (test regionale relevantie) -----------------------
    Prompt("Beste zonnepanelen installateur in Haren, Groningen.", G),
    Prompt("Zonnepanelen laten plaatsen in Delfzijl, welk bedrijf raad je aan?", G),
    Prompt("Zonnepanelen installateur Stadskanaal, wie heeft goede aanbevelingen?", G),
]
