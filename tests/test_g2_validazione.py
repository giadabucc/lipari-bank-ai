# tests/test_g2_validazione.py — l'estensione: lo stesso errore si legge allo stesso modo
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_la_valuta_sbagliata_ha_la_stessa_forma_nella_richiesta_e_nel_file():
    richiesta = client.post(
        "/api/ai/categorize", json={"description": "Coop", "amount": 5, "currency": "euro"}
    )
    [nella_richiesta] = richiesta.json()["details"]
    file = b"date,description,amount,currency\n2026-09-01,Coop,5.00,euro\n"
    importato = client.post("/api/ai/movements/import", files={"file": ("e.csv", file)})
    [nel_file] = importato.json()["problems"]

    # la stessa forma, più il numero di riga: un client li legge con lo stesso codice
    assert set(nel_file) - set(nella_richiesta) == {"row"}
    for chiave in ("field", "code", "expected"):
        assert nel_file[chiave] == nella_richiesta[chiave]
    # cosa c'era torna solo dal file, che è di chi lo ha caricato; il corpo della richiesta no
    assert nella_richiesta["found"] is None and "euro" not in richiesta.text
    assert (
        nel_file["reason"]
        == "currency: trovato «euro», serve tre lettere maiuscole, per esempio EUR"
    )
