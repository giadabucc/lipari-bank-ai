# scripts/check.py — un comando solo per tutti i controlli, lo stesso in locale e in CI
import subprocess
import sys
import time

Passo = tuple[str, list[str]]

# python -m invece del nome dell'eseguibile: usa i tool del .venv del progetto, su ogni sistema.
# ruff format --check e non ruff format: un controllo dice cosa non va, non lo corregge di nascosto
PASSI: list[Passo] = [
    ("lock aggiornato", ["uv", "lock", "--check"]),
    ("ruff check", [sys.executable, "-m", "ruff", "check", "."]),
    ("ruff format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    ("mypy strict", [sys.executable, "-m", "mypy", "src", "scripts"]),
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
]


def esegui(passi: list[Passo]) -> int:
    """Esegue tutti i passi, anche dopo un fallimento, e restituisce 1 se almeno uno è fallito."""
    falliti: list[str] = []
    inizio = time.perf_counter()
    for nome, comando in passi:
        print(f"==> {nome}", flush=True)
        if subprocess.run(comando).returncode != 0:
            falliti.append(nome)
    durata = time.perf_counter() - inizio
    if falliti:
        print(f"\nFALLITI {len(falliti)} su {len(passi)}: {', '.join(falliti)} ({durata:.1f}s)")
        return 1
    print(f"\nOK: {len(passi)} controlli passati in {durata:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(esegui(PASSI))
