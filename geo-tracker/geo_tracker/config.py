"""
Klantconfiguratie laden
=========================
Elke klant heeft één bestand in clients/<slug>.py met daarin BRAND,
COMPETITORS en PROMPTS. Dit module laadt en valideert dat bestand, zodat
je bij een tikfout of ontbrekend veld direct een duidelijke foutmelding
krijgt in plaats van een cryptische crash verderop in het script.
"""

import importlib

from .models import ClientConfig

REQUIRED_ATTRS = ("BRAND", "COMPETITORS", "PROMPTS")


def load_client(slug: str) -> ClientConfig:
    """
    Laadt clients/<slug>.py. `slug` is de bestandsnaam zonder .py, bv.
    "groningen_zonnepanelen" voor clients/groningen_zonnepanelen.py.
    """
    try:
        module = importlib.import_module(f"clients.{slug}")
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"Geen configuratie gevonden voor client '{slug}'.\n"
            f"Verwacht bestand: clients/{slug}.py\n"
            f"Kopieer clients/_template.py als startpunt voor een nieuwe klant."
        ) from e

    missing = [attr for attr in REQUIRED_ATTRS if not hasattr(module, attr)]
    if missing:
        raise SystemExit(
            f"clients/{slug}.py mist verplichte velden: {', '.join(missing)}"
        )

    if not module.PROMPTS:
        raise SystemExit(f"clients/{slug}.py heeft een lege PROMPTS-lijst.")

    return ClientConfig(
        slug=slug,
        brand=module.BRAND,
        competitors=module.COMPETITORS,
        prompts=module.PROMPTS,
    )


def list_clients() -> list[str]:
    """Geeft alle beschikbare client-slugs terug (voor een overzichtscommando)."""
    import pathlib
    clients_dir = pathlib.Path(__file__).resolve().parent.parent / "clients"
    return sorted(
        p.stem for p in clients_dir.glob("*.py")
        if not p.stem.startswith("_")
    )
