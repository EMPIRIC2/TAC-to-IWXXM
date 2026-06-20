import pathlib
import sys

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.utilities.conversion import ConversionError, convert_metar_tac

sample = "METAR CWFD 290000Z AUTO 20022KT ////SM // BKN003 BKN008 ///// A////"
print("Sample TAC:", sample)
try:
    xml = convert_metar_tac(sample)
    print("Converted IWXXM (truncated):\n", xml[:400])
except ConversionError as e:
    print("ConversionError:", e)
except Exception as e:
    print("Unexpected error:", e)
