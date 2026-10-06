# src/types/problem.py — un campo che non va, nella stessa forma ovunque arrivi
from pydantic import BaseModel, Field


class Problem(BaseModel):
    """La stessa forma per il 422 di una richiesta e per una riga scartata del CSV: per chi la
    riceve è lo stesso problema, e si legge allo stesso modo."""

    field: str = Field(description="Il campo, come lo ha scritto il chiamante: amount, date, corpo")
    code: str = Field(description="Il codice stabile, per un programma: missing, greater_than…")
    reason: str = Field(description="La frase, per una persona: il campo, cosa c'era, cosa serve")
    found: str | None = Field(
        default=None,
        description="Il valore trovato, al massimo 40 caratteri. Solo per le righe di un file: "
        "il corpo di una richiesta non torna indietro",
    )
    expected: str | None = Field(default=None, description="Cosa serve, detto in italiano")
