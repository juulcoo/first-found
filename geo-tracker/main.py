"""
Enige entry point van dit project.

    python main.py list
    python main.py run    --client groningen_zonnepanelen
    python main.py report --client groningen_zonnepanelen
    python main.py audit  --client groningen_zonnepanelen
    python main.py score  --client groningen_zonnepanelen
    python main.py full   --client groningen_zonnepanelen

Zie README.md voor de volledige uitleg.
"""

from geo_tracker.cli import main

if __name__ == "__main__":
    main()
