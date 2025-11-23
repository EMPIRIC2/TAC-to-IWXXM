# METAR to IWXXM Converter

FastAPI-based single-page GUI and utility functions to decode METAR/SPECI TAC and serialize IWXXM XML using the GIFTs submodule.

## Features

- Drag & drop multiple `.tac` / `.txt` METAR files
- Manual METAR text input
- Batch conversion to IWXXM XML (returned as text for convenience)
- Copy / download each result
- Planned: ZIP batch download endpoint

## Quick Start

### 1. Create a virtual environment (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

Editable install currently fails (pyproject expects a `src/` layout). For now install runtime deps directly:

```powershell
python -m pip install fastapi uvicorn tpg python-multipart
```

Optional extra functionality:

```powershell
python -m pip install lxml skyfield
```

### 3. Run GUI

```powershell
python -m uvicorn gui.app:app --host 0.0.0.0 --port 8000
```

Open <http://localhost:8000/> in a browser.

### 4. Convert METAR

- Drag files or paste TAC into Manual Input.
- Click Convert.
- Use Download / Copy buttons for each IWXXM output.

### 5. Programmatic Use

```python
from backend.conversion import convert_metar_tac
xml = convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 SCT120 BKN250 15/07 A3005")
print(xml[:200])
```

## Roadmap

- `/api/convert-zip` endpoint to bundle outputs as ZIP
- Editable packaging (`src/metar_to_IWXXM/`) for `pip install -e .`
- Optional IWXXM schema validation step if `lxml` and schemas present

## Notes

- Add `python-multipart` to `pyproject.toml` dependencies for form uploads.
- Current XML output uses basic encoder; additional data enrichment may require more GIFTs modules.

## License

MIT
