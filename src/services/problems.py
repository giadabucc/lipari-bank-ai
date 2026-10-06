# src/services/problems.py — dall'errore di Pydantic al Problem: cosa c'era, cosa serve
from collections.abc import Mapping
from typing import Any

from src.types.problem import Problem

MAX_TROVATO = 40  # abbastanza per riconoscere la cella, non abbastanza per rimandare un file
FORME = {r"^[A-Z]{3}$": "tre lettere maiuscole, per esempio EUR"}
NUMERO = "un numero col punto decimale, per esempio 12.50"
DATA = "una data che esiste, nella forma AAAA-MM-GG"


def atteso(tipo: str, ctx: Mapping[str, Any]) -> str | None:
    """Cosa serve, detto a chi ha preparato il dato. None per un tipo che non conosciamo."""
    if tipo == "missing":
        return "un valore"
    if tipo == "string_too_short":
        n = ctx.get("min_length", 1)
        return "un testo non vuoto" if n == 1 else f"almeno {n} caratteri"
    if tipo == "string_too_long":
        return f"al massimo {ctx['max_length']} caratteri"
    if tipo == "greater_than":
        return f"un numero maggiore di {ctx['gt']}"
    if tipo in ("decimal_parsing", "decimal_type", "float_parsing", "float_type"):
        return NUMERO
    if tipo == "string_pattern_mismatch":
        forma = str(ctx.get("pattern"))
        return FORME.get(forma, f"un testo nella forma {forma}")
    if tipo.startswith("date"):  # date_format (il nostro), date_parsing, date_from_datetime_…
        return DATA
    if tipo == "json_invalid":
        return "un corpo JSON valido"
    return None


def problema(errore: Mapping[str, Any], campo: str, con_valore: bool) -> Problem:
    """Un errore di Pydantic come Problem. con_valore: il valore trovato torna indietro solo
    quando chi lo legge deve ritrovarlo in un file suo."""
    tipo = str(errore["type"])
    serve = atteso(tipo, errore.get("ctx") or {})
    trovato = None
    if con_valore and tipo != "missing":
        v = str(errore["input"])
        trovato = v if len(v) <= MAX_TROVATO else v[:MAX_TROVATO] + "…"

    if tipo == "missing":
        frase = "manca"
    elif serve is None:
        frase = str(errore["msg"])  # un tipo nuovo: meglio la frase di Pydantic che niente
    elif trovato is None:
        frase = f"serve {serve}"
    else:
        visto = "un campo vuoto" if not trovato.strip() else f"«{trovato}»"  # anche solo spazi
        frase = f"trovato {visto}, serve {serve}"
    return Problem(
        field=campo, code=tipo, reason=f"{campo}: {frase}", found=trovato, expected=serve
    )
