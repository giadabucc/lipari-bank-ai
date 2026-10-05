# LipariBank AI

L'assistente AI di LipariBank: un'applicazione FastAPI su Python 3.12, gestita con [uv](https://docs.astral.sh/uv/).
Questo README basta per installarla, avviarla e controllarla su una macchina che non l'ha mai vista.

## Cosa serve

Solo **uv** e **git**. Python 3.12 lo installa uv da solo, leggendo `.python-version`.

```bash
# Linux / Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Chiudi e riapri il terminale, poi `uv --version` deve stampare un numero di versione.

## Installare e avviare

```bash
git clone https://github.com/giadabucc/lipari-bank-ai.git
cd lipari-bank-ai
uv sync --locked                 # crea .venv con Python 3.12 e le versioni esatte di uv.lock
```

Poi la configurazione. `.env.example` elenca tutte le variabili; `.env` contiene i tuoi valori e non si versiona mai.

```bash
cp .env.example .env                    # Linux / Mac
Copy-Item .env.example .env             # Windows (PowerShell)
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Apri `.env` e incolla la stringa stampata dopo `JWT_SECRET=`. È l'unico valore che devi scrivere tu:
`DATABASE_URL` ha già un valore di sviluppo (il database arriva dal Giorno 3, oggi nessuno ci si collega),
e le chiavi `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` servono dal Giorno 4 — senza, il progetto parte lo stesso.

```bash
uv run uvicorn src.main:app --reload
```

Apri nel browser:

- http://localhost:8000/health — deve rispondere con `"status":"UP"`, l'ambiente e quali chiavi ci sono
- http://localhost:8000/docs — la documentazione interattiva (Swagger UI)

## Configurazione

| Variabile | Obbligatoria | Default | A cosa serve |
|---|---|---|---|
| `DATABASE_URL` | sì | — | connessione al database, `postgresql+asyncpg://utente:password@host:5432/nome` |
| `JWT_SECRET` | sì, ≥ 32 caratteri | — | firma dei token; generalo con il comando qui sopra |
| `ENVIRONMENT` | no | `development` | uno fra `development`, `test`, `production` |
| `DEBUG` | no | `false` | |
| `APP_NAME` | no | `LipariBank AI` | |
| `OPENAI_API_KEY` | no (serve dal Giorno 4) | vuota | |
| `ANTHROPIC_API_KEY` | no (serve dal Giorno 4) | vuota | |
| `DEFAULT_MODEL` | no | `gpt-4o-mini` | |
| `EMBEDDING_MODEL` | no | `text-embedding-3-small` | |
| `MAX_TOKENS_PER_REQUEST` | no | `2000` | un numero intero |

La configurazione si valida **all'avvio**. Se una variabile manca o ha un valore sbagliato, il processo non parte,
esce con codice 1 e dice quale variabile e cosa ci va, per esempio:

```
Configurazione non valida: il progetto non parte.
  - JWT_SECRET: manca. Ci va un segreto di almeno 32 caratteri: uv run python -c "import secrets; ...".
Si scrive nel file .env (l'elenco completo sta in .env.example) o nell'ambiente.
```

Con `--reload` il messaggio è lo stesso, ma il processo che sorveglia i file resta vivo: corretto il `.env`,
riavvia a mano (il reload guarda i `.py`, non il `.env`).

## Controllare il codice

Un comando solo, lo stesso che gira su GitHub Actions a ogni push (`.github/workflows/check.yml`):

```bash
uv run python scripts/check.py
```

Esegue, nell'ordine: `uv lock --check`, `ruff check`, `ruff format --check`, `mypy` in strict su `src` e `scripts`,
`pytest`. Li esegue tutti anche se uno fallisce, e alla fine dice quali sono falliti; il codice d'uscita è 1 se
almeno uno è fallito. Per correggere la formattazione: `uv run ruff format .`.

I test non hanno bisogno di un `.env`: `conftest.py` nella radice fornisce i due valori obbligatori.

## Struttura

```
src/config.py        la configurazione, validata all'avvio
src/main.py          l'app FastAPI e la sonda /health
scripts/check.py     il comando unico dei controlli
tests/               i test (pytest)
conftest.py          i valori minimi per importare l'app nei test
.env.example         l'elenco delle variabili, senza segreti
```

## Scelte di progetto

**Le dipendenze di sviluppo** (ruff, mypy, pytest) stanno in `[dependency-groups]`, non in `[project.optional-dependencies]`.
Il gruppo è lo standard più recente (PEP 735): `uv sync` lo installa senza flag, e `uv sync --no-dev` lo lascia fuori
dall'immagine di produzione. Un extra invece finirebbe nei metadati del pacchetto come se fosse una funzione per gli utenti, e andrebbe chiesto a ogni installazione con `--extra dev`.

**Estensione del pomeriggio: il comando che controlla tutto** (`scripts/check.py` più la CI).
Scelto: uno script Python, che gira uguale su Windows, Mac e Linux, e `uv sync --locked` in CI. Scartato: un Makefile,
che su Windows non c'è, e `uv sync` senza `--locked`. Il numero: 5 controlli invece di 5 comandi da ricordare, in 6,4 s in locale.
Con un `uv.lock` non aggiornato, `uv sync --locked` esce con codice 1. Senza `--locked` risolve 41 pacchetti invece di 38,
installa `requests 2.34.2` (che nel lock non c'è) e passa.
Il test `tests/test_check.py` dimostra che un solo passo fallito fa fallire il comando, e che i passi successivi girano comunque.

## La prova della ricostruzione

<!-- DA COMPILARE: cancella .venv, segui questo README riga per riga e cronometra -->
- Tempo: **___ minuti**, dalla cartella vuota alla sonda che risponde.
- Primo punto di blocco: ___
