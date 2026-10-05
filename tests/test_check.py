# tests/test_check.py — il comando unico non nasconde un fallimento
import sys

from scripts.check import esegui

PASSA = [sys.executable, "-c", "raise SystemExit(0)"]
FALLISCE = [sys.executable, "-c", "raise SystemExit(3)"]


def test_un_solo_passo_fallito_fa_fallire_il_comando_e_viene_nominato(capsys):
    codice = esegui([("primo", PASSA), ("rotto", FALLISCE), ("ultimo", PASSA)])
    uscita = capsys.readouterr().out
    assert codice == 1
    assert "FALLITI 1 su 3: rotto" in uscita
    assert "==> ultimo" in uscita  # i passi dopo il fallimento girano comunque
