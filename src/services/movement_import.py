# src/services/movement_import.py — il CSV riga per riga: ogni riga importata o spiegata
import csv

from pydantic import ValidationError

from src.exceptions import InvalidFileError
from src.services.problems import problema
from src.types.movements import ImportProblem, ImportResult, MovementRow

INTESTAZIONE = ["date", "description", "amount", "currency"]
CAMPI_ATTESI = f"{len(INTESTAZIONE)} campi: {','.join(INTESTAZIONE)}"


def motivo(numero: int, errore: ValidationError) -> ImportProblem:
    """Il primo campo che non va, cosa c'era e cosa serve: nella forma del 422, più la riga."""
    e = errore.errors()[0]
    campo = ".".join(str(p) for p in e["loc"]) or "riga"
    return ImportProblem(row=numero, **problema(e, campo, con_valore=True).model_dump())


def importa_csv(contenuto: bytes) -> ImportResult:
    if not contenuto.strip():
        raise InvalidFileError("Il file è vuoto")
    try:
        testo = contenuto.decode("utf-8-sig")  # -sig: toglie il BOM che Excel mette in testa
    except UnicodeDecodeError:
        raise InvalidFileError("Il file non è testo UTF-8: non è un CSV") from None

    # Un movimento per riga del file, e ogni riga si legge da sola: una virgoletta aperta e mai
    # chiusa, o un campo oltre il limite del modulo csv, rovinano la loro riga e non le successive
    righe = [r.rstrip("\r") for r in testo.split("\n")]
    if next(csv.reader(righe[:1]), []) != INTESTAZIONE:
        raise InvalidFileError(f"L'intestazione deve essere {','.join(INTESTAZIONE)}")

    importate, problemi = 0, []
    for numero, linea in enumerate(righe[1:], start=2):  # la riga nel file: la 1 è l'intestazione
        if not linea.strip():
            continue  # una riga vuota non è un movimento
        try:
            campi = next(csv.reader([linea], strict=True))
        except csv.Error:  # sollevato nel codice: se nessuno lo cattura, è un 500
            serve = "virgolette chiuse e campi più corti di 131072 caratteri"
            problemi.append(
                ImportProblem(
                    row=numero,
                    field="riga",
                    code="csv_unreadable",
                    reason=f"riga: illeggibile come CSV, servono {serve}",
                    expected=serve,
                )
            )
            continue
        if len(campi) != len(INTESTAZIONE):
            problemi.append(
                ImportProblem(
                    row=numero,
                    field="riga",
                    code="field_count",
                    reason=f"riga: trovati {len(campi)} campi, servono {CAMPI_ATTESI}",
                    found=f"{len(campi)} campi",
                    expected=CAMPI_ATTESI,
                )
            )
            continue
        try:
            MovementRow.model_validate(dict(zip(INTESTAZIONE, campi, strict=True)))
        except ValidationError as e:  # costruito nel codice: se nessuno lo cattura, è un 500
            problemi.append(motivo(numero, e))
            continue
        importate += 1
    return ImportResult(imported_count=importate, problems=problemi)
