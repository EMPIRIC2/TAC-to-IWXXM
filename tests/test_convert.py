from backend.conversion import convert_metar_tac, ConversionError
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


sample = "METAR CWFD 290000Z AUTO 20022KT ////SM // BKN003 BKN008 ///// A////"
print("Sample TAC:", sample)
try:
    xml = convert_metar_tac(sample)
    print("Converted IWXXM (truncated):\n", xml[:400])
except ConversionError as e:
    print("ConversionError:", e)
except Exception as e:
    print("Unexpected error:", e)
