# GEO/AEO Citation Tracker

Meet of en hoe vaak een merk (en zijn concurrenten) organisch wordt
genoemd of geciteerd in antwoorden van ChatGPT, Perplexity, Gemini en
Claude — inclusief een technische fundament-check en een samengesteld
scorecijfer.

## Projectstructuur

```
geo-tracker/
├── main.py                    ← enige entry point, start hier
├── requirements.txt
├── .env.example
│
├── clients/                   ← klantdata, één bestand per klant
│   ├── _template.py           ← kopieer dit voor een nieuwe klant
│   └── groningen_zonnepanelen.py   ← ingevuld voorbeeld
│
├── geo_tracker/                ← de code, hoef je zelden aan te komen
│   ├── models.py               ← alle datastructuren (lees dit eerst)
│   ├── config.py                ← laadt clients/<slug>.py
│   ├── providers.py             ← API-aanroepen naar ChatGPT/Perplexity/Gemini
│   ├── analysis.py              ← bepaalt of een merk voorkomt in een antwoord
│   ├── storage.py                ← SQLite + JSON-export
│   ├── technical_audit.py        ← crawler-toegankelijkheid check
│   ├── scoring.py                 ← rekent het eindcijfer uit
│   └── cli.py                     ← bindt alles samen tot commando's
│
├── dashboard/
│   └── geo_dashboard.jsx      ← voorbeeldweergave voor een klant
│
└── data/                       ← alle gegenereerde output (gitignored)
    ├── <slug>.db
    ├── <slug>_dashboard.json
    ├── <slug>_technical_audit.json
    └── <slug>_score.json
```

**Waarom deze scheiding?** `clients/` is data — dingen die je per klant
invult en die vaak wijzigen. `geo_tracker/` is code — logica die voor
elke klant hetzelfde werkt en die je zelden hoeft aan te passen. Zo kun
je een nieuwe klant toevoegen zonder ook maar één regel code aan te
raken, en andersom de code verbeteren zonder klantdata te hoeven
doorspitten.

## 1. Installeren

```bash
cd geo-tracker
pip install -r requirements.txt
cp .env.example .env      # vul je eigen API keys in
```

Je hebt nodig: een **Anthropic/Claude API key** (console.anthropic.com —
let op: je organisatie-beheerder moet web search daar eerst aanzetten
onder Settings → Privacy), een **OpenAI API key** (platform.openai.com —
een los, betaald account, niet je ChatGPT Plus-abonnement), een
**Perplexity API key** (Sonar-modellen) en een **Gemini API key**
(Google AI Studio).

**Heb je nog niet alle vier keys?** Geen probleem — laat de ontbrekende
regels in `.env` gewoon leeg en beperk je tot de providers waar je wél
een key voor hebt met `--providers`:

```bash
python main.py run --client groningen_zonnepanelen --providers claude
```

Je kunt dit later, zodra je meer keys hebt, gewoon opnieuw draaien met
`--providers chatgpt,perplexity` erbij — de resultaten van eerdere runs
blijven gewoon in de database staan, dus je verliest niets.

## 2. Een nieuwe klant toevoegen

```bash
cp clients/_template.py clients/<nieuwe_klant>.py
```

Vul in `clients/<nieuwe_klant>.py`:
- `BRAND` — naam, domein, schrijfwijzen.
- `COMPETITORS` — 2-4 directe concurrenten.
- `PROMPTS` — 20-50 realistische koopvragen, verdeeld over de vijf
  categorieën (zie `geo_tracker/models.py` voor de uitleg per
  categorie, en `clients/groningen_zonnepanelen.py` voor een compleet
  ingevuld voorbeeld). Dit is het belangrijkste onderdeel — haal de
  vragen uit echte klantgesprekken, reviews en zoekwoordenonderzoek,
  nooit uit "noem [merk]"-achtige vragen. Zodra je begint te meten,
  laat je deze lijst ongewijzigd, anders zijn latere metingen niet
  vergelijkbaar met eerdere.

Bekijk op elk moment welke klanten er zijn:

```bash
python main.py list
```

## 3. Draaien

Los per stap:

```bash
python main.py run    --client groningen_zonnepanelen   # bevraagt alle AI's
python main.py report --client groningen_zonnepanelen   # → data/…_dashboard.json
python main.py audit  --client groningen_zonnepanelen   # technische check
python main.py score  --client groningen_zonnepanelen   # → eindcijfer
```

Of alles in één keer — dit is het commando dat je gebruikt om een
bestaande klant snel opnieuw te meten:

```bash
python main.py full --client groningen_zonnepanelen
```

## 4. Automatiseren (wekelijkse of dagelijkse meting)

GitHub Action met een schema, `.github/workflows/geo-tracker.yml`:

```yaml
name: geo-tracker
on:
  schedule:
    - cron: "0 8 * * 1"   # elke maandag 08:00 UTC
  workflow_dispatch: {}
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: python main.py full --client groningen_zonnepanelen
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      - run: git add data/ && git commit -m "weekly meting" && git push
```

Voor meerdere klanten: herhaal de `run`-stap met een andere `--client`
waarde, of loop in bash over `python main.py list`.

## 5. Aan de klant laten zien

`dashboard/geo_dashboard.jsx` toont nu voorbeelddata in exact de vorm
van `data/<slug>_dashboard.json`. Vervang de `MOCK_*`-constanten
bovenin door een fetch/import van dat bestand voor een werkend rapport
per klant.

## Kosten en verwachtingen

- Elke `run` kost echte API-tokens. Met 25 prompts × 3 modellen is dit
  meestal een paar euro per meting — reken dit door voordat je een
  vaste prijs afspreekt met een klant.
- De resultaten zijn een betrouwbare **proxy**, geen exacte kopie van
  wat een individuele consument in de ChatGPT- of Perplexity-app ziet
  (die kan persoonlijke geschiedenis meewegen). Wees hier transparant
  over.
- Citatiepatronen kunnen in dagen omslaan. Reken op minimaal
  maandelijkse herijking — en gebruik dat als argument voor een
  doorlopend contract in plaats van een eenmalig project.

## Uitbreiden

- **Nieuw AI-platform**: kopieer het patroon van een `query_*`-functie
  in `geo_tracker/providers.py` en voeg één regel toe aan `PROVIDERS`.
- **Alerting**: laat `cmd_run` in `geo_tracker/cli.py` een Slack-bericht
  sturen zodra `brand_mentioned` van `True` naar `False` verandert.
- **Robuustere technische check**: vervang de eenvoudige robots.txt-
  parser in `geo_tracker/technical_audit.py` door `urllib.robotparser`
  of `protego`, en de renderingscheck door een echte Playwright-render.
- **Andere scoregewichten**: pas `WEIGHTS` in `geo_tracker/scoring.py`
  aan zodra je ziet wat in de praktijk correleert met klantresultaten.
