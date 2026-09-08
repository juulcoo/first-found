"""
Command-line interface
========================
Dit bestand bevat geen "echte" logica — het roept alleen functies aan uit
de andere modules in de juiste volgorde. Als je wilt begrijpen wat een
commando doet, lees de aangeroepen functie in het betreffende module
(config.py, providers.py, storage.py, technical_audit.py, scoring.py).

Gebruik (vanuit de hoofdmap van het project):

    python main.py list
    python main.py run     --client <slug>
    python main.py report  --client <slug>
    python main.py audit   --client <slug>
    python main.py score   --client <slug>
    python main.py full    --client <slug>     # alle vier hierboven, achter elkaar
"""

import argparse
from datetime import datetime, timezone

from dotenv import load_dotenv

from . import scoring, storage, technical_audit
from .analysis import analyze
from .config import list_clients, load_client
from .models import ClientConfig, QueryResult
from .providers import PROVIDERS, MissingAPIKey


def cmd_list(_args) -> None:
    slugs = list_clients()
    if not slugs:
        print("Nog geen klanten. Kopieer clients/_template.py om te beginnen.")
        return
    print("Beschikbare klanten:")
    for slug in slugs:
        print(f"  - {slug}")


def cmd_run(args) -> None:
    client = load_client(args.client)
    conn = storage.init_db(client.slug)
    timestamp = datetime.now(timezone.utc).isoformat()

    active_providers = _select_providers(args.providers)
    done = 0
    for model_name, query_fn in active_providers.items():
        for prompt in client.prompts:
            try:
                text, domains = query_fn(prompt.text)
            except MissingAPIKey as e:
                print(f"[{model_name}] overgeslagen: {e}")
                break  # geen zin om dezelfde fout voor elke prompt te herhalen
            except Exception as e:
                print(f"[{model_name}] fout bij '{prompt.text[:40]}...': {e}")
                continue

            done += 1
            info = analyze(text, domains, client.brand, client.competitors)
            result = QueryResult(
                model=model_name, prompt=prompt.text, category=prompt.category.value,
                timestamp=timestamp, raw_text=text, **info,
            )
            storage.save_result(conn, result)
            status = "GEVONDEN" if result.brand_mentioned else "niet gevonden"
            print(f"[{done}] {model_name}: {status} — {prompt.text[:50]}")
    conn.close()
    print(f"\nKlaar. {done} metingen opgeslagen in {storage.db_path(client.slug)}")


def _select_providers(providers_arg: str | None) -> dict:
    """Filtert PROVIDERS op basis van --providers, met een duidelijke foutmelding bij een tikfout."""
    if not providers_arg:
        return PROVIDERS
    requested = [p.strip() for p in providers_arg.split(",") if p.strip()]
    unknown = [p for p in requested if p not in PROVIDERS]
    if unknown:
        raise SystemExit(
            f"Onbekende provider(s): {', '.join(unknown)}. "
            f"Beschikbaar: {', '.join(PROVIDERS)}"
        )
    return {name: PROVIDERS[name] for name in requested}


def cmd_report(args) -> None:
    client = load_client(args.client)
    path = storage.export_dashboard_json(
        client.slug, client.brand.name, [c.name for c in client.competitors]
    )
    print(f"Geëxporteerd naar {path}")


def cmd_audit(args) -> None:
    client = load_client(args.client)
    print(f"Technische check voor {client.brand.domain}...")
    audit = technical_audit.run_audit(client.brand.domain)
    path = storage.audit_json_path(client.slug)
    technical_audit.save_audit_json(audit, path)
    blocked = [b for b, v in audit["robots_txt"].get("blocks", {}).items() if v]
    if blocked:
        print(f"  Let op: geblokkeerd voor {', '.join(blocked)}")
    else:
        print("  Geen geblokkeerde AI-crawlers gevonden.")
    print(f"Opgeslagen in {path}")


def cmd_score(args) -> None:
    client = load_client(args.client)
    records = storage.load_results(client.slug)
    if not records:
        raise SystemExit(
            f"Nog geen metingen voor '{client.slug}'. Draai eerst: "
            f"python main.py run --client {client.slug}"
        )

    audit_path = storage.audit_json_path(client.slug)
    if not audit_path.exists():
        raise SystemExit(
            f"Nog geen technische audit voor '{client.slug}'. Draai eerst: "
            f"python main.py audit --client {client.slug}"
        )

    import json
    with open(audit_path, encoding="utf-8") as f:
        audit = json.load(f)

    report = scoring.build_report(client.brand.name, records, audit)
    scoring.save_score_json(report, storage.score_json_path(client.slug))

    print(f"\n{report['brand']} — {report['composite_score']}/100 ({report['grade']})")
    print(f"  technisch fundament : {report['technical_score']}/100")
    print(f"  genoemd (mention)   : {report['mention_rate']}%")
    print(f"  geciteerd met link  : {report['citation_rate']}%")
    print(f"  aandeel van stem    : {report['share_of_voice']}%")
    if report["category_breakdown"]:
        print("  per categorie:")
        for cat, rate in report["category_breakdown"].items():
            print(f"    - {cat}: {rate}%")


def cmd_full(args) -> None:
    """De 'draai alles opnieuw voor deze klant'-knop."""
    print(f"=== Volledige pijplijn voor '{args.client}' ===\n")
    print("1/4 Meten...")
    cmd_run(args)
    print("\n2/4 Exporteren...")
    cmd_report(args)
    print("\n3/4 Technische audit...")
    cmd_audit(args)
    print("\n4/4 Score berekenen...")
    cmd_score(args)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="main.py", description="GEO/AEO citation tracker"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="toon beschikbare klanten").set_defaults(func=cmd_list)

    for name, help_text, func in [
        ("run", "bevraag alle AI-platforms en sla resultaten op", cmd_run),
        ("report", "exporteer resultaten naar dashboard-JSON", cmd_report),
        ("audit", "technische crawler-toegankelijkheid check", cmd_audit),
        ("score", "bereken het samengestelde scorecijfer", cmd_score),
        ("full", "run + report + audit + score, achter elkaar", cmd_full),
    ]:
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("--client", required=True, help="slug uit clients/, bv. groningen_zonnepanelen")
        if name in ("run", "full"):
            sub.add_argument(
                "--providers", default=None,
                help=f"komma-gescheiden subset, bv. 'claude' of 'claude,chatgpt'. "
                     f"Standaard: alle ({', '.join(PROVIDERS)})",
            )
        sub.set_defaults(func=func)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
