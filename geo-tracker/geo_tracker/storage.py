"""
Opslag
=======
Alle output — databases, exports, auditresultaten, scores — komt in de
centrale data/ map terecht, met de klant-slug in de bestandsnaam. Zo
overschrijven klanten elkaars data nooit, en weet je bij het zien van
een bestandsnaam meteen van welke klant en welk type data het is.

    data/
      groningen_zonnepanelen.db                 ← ruwe metingen (SQLite)
      groningen_zonnepanelen_dashboard.json      ← export voor het dashboard
      groningen_zonnepanelen_technical_audit.json
      groningen_zonnepanelen_score.json
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import QueryResult

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _path(slug: str, suffix: str) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR / f"{slug}{suffix}"


def db_path(slug: str) -> Path:
    return _path(slug, ".db")


def dashboard_json_path(slug: str) -> Path:
    return _path(slug, "_dashboard.json")


def audit_json_path(slug: str) -> Path:
    return _path(slug, "_technical_audit.json")


def score_json_path(slug: str) -> Path:
    return _path(slug, "_score.json")


def init_db(slug: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(slug))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, model TEXT, prompt TEXT, category TEXT,
            brand_mentioned INTEGER, brand_cited_with_link INTEGER,
            competitors_mentioned TEXT, cited_domains TEXT, raw_text TEXT
        )
    """)
    conn.commit()
    return conn


def save_result(conn: sqlite3.Connection, r: QueryResult) -> None:
    conn.execute(
        "INSERT INTO results (timestamp, model, prompt, category, brand_mentioned, "
        "brand_cited_with_link, competitors_mentioned, cited_domains, raw_text) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            r.timestamp, r.model, r.prompt, r.category,
            int(r.brand_mentioned), int(r.brand_cited_with_link),
            json.dumps(r.competitors_mentioned), json.dumps(r.cited_domains),
            r.raw_text,
        ),
    )
    conn.commit()


def load_results(slug: str) -> list[dict]:
    conn = sqlite3.connect(db_path(slug))
    rows = conn.execute(
        "SELECT timestamp, model, prompt, category, brand_mentioned, "
        "brand_cited_with_link, competitors_mentioned, cited_domains "
        "FROM results ORDER BY timestamp"
    ).fetchall()
    conn.close()
    return [
        {
            "timestamp": r[0], "model": r[1], "prompt": r[2], "category": r[3],
            "brand_mentioned": bool(r[4]), "brand_cited_with_link": bool(r[5]),
            "competitors_mentioned": json.loads(r[6]),
            "cited_domains": json.loads(r[7]),
        }
        for r in rows
    ]


def export_dashboard_json(slug: str, brand_name: str, competitor_names: list[str]) -> Path:
    records = load_results(slug)
    output_path = dashboard_json_path(slug)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "brand": brand_name,
            "competitors": competitor_names,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "records": records,
        }, f, ensure_ascii=False, indent=2)
    return output_path
