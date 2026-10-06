# src/types/movements.py — una riga dell'estratto, e l'esito dell'importazione
import datetime as dt
import re
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError

from src.types.problem import Problem


class MovementRow(BaseModel):
    """Una riga del CSV: le stesse regole del singolo movimento, più la data."""

    model_config = ConfigDict(str_strip_whitespace=True)

    date: dt.date
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")

    @field_validator("date", mode="before")
    @classmethod
    def solo_aaaa_mm_gg(cls, v: object) -> object:
        # Da solo Pydantic accetterebbe anche "1756684800" (un timestamp: il 2025-09-01) e
        # "2026-09-01T00:00:00": il contratto ne ammette una. Che la data esista lo controlla
        # poi il tipo: il 2026-02-30 non passa.
        if not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v.strip()):
            # un codice nostro, date_format, invece del generico value_error: il client lo distingue
            raise PydanticCustomError("date_format", "la data va scritta AAAA-MM-GG")
        return v.strip()  # quella che si è controllata: lo spazio davanti non arriva al tipo


class ImportProblem(Problem):
    """Il Problem del 422, più il numero di riga: chi legge l'uno sa leggere l'altro."""

    row: int = Field(description="Il numero di riga nel file: la 1 è l'intestazione")


class ImportResult(BaseModel):
    imported_count: int
    problems: list[ImportProblem]
