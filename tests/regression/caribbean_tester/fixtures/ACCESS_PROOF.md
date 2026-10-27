# Access proof — Downloads testing packet

Root: `/Users/bigme/Downloads/TAC-IWXXM TRANSLATOR TESTING RESULTS (2)`

## Services / subfolders (8) and file counts

| Service folder | Files |
|----------------|------:|
| BELIZE-TAC TO IWXXM COMPLETED TESTING RESULTS | 23 |
| BRITISH VIRGIN ISLANDS | 2 |
| GUYANA-TAC-IWXXM-TEST-EVALUATION | 73 |
| JAMAICA IWXXM TESTING RESULTS | 17 |
| SAINT LUCIA - TAC-IWXXM TESTING RESULT | 2 |
| ST KITTS and NEVIS-TAC-IWXXM-TEST-EVALUATIONS | 2 |
| St Maarten IWXXM TESTING RESULTS | 3 |
| TRINIDAD AND TOBAGO -TAC-TO-IWXXM TESTING RESULTS | 2 |

Totals under root: **24 DOCX**, **6 XLSX**, **65 PNG/JPEG** (15 Jamaica PNG + 50 Guyana JPEG). All image files were opened with the vision Read tool (see `IMAGE_REVIEW.md`).

## DOCX (python-docx) — ≥2 opened

1. **St Maarten** `TAC to IWXXM Test-Error Report.docx`  
   - Finding: “SYSTEM NOT DECODING ‘VCSH’ NOR REMARKS WITH DIRECTION OF CB, SHRA”  
   - Finding: “GTS HEADERS HAD TO BE REMOVED … MESSAGE SHOULD START WITH METAR TNCM…”

2. **Trinidad and Tobago** `NMHS TAC-IWXXM User Evaluation Questionnaire_TTPPFeedback.docx`  
   - Finding: METAR reliability score 3 — “VCSH and … lowest Vis and direction were left out.”  
   - Finding: “interface was way too busy and overwhelming for first time users”

3. **Guyana** `TAC_to_IWXXM_Test-Error_Report.docx` (extra)  
   - Finding: “Generated IWXXM repeatedly failed validation with AIRPORT_ICAO and TAC_SYNTAX”

## XLSX (openpyxl) — ≥5 national logs

| Log | Sheets | TAC-like rows |
|-----|--------|--------------:|
| Jamaica `2-WeekTest-Log…xlsx` | Instructions, Test Log, Summary, Weekly Summary | 1074 |
| TT `…TTMS.xlsx` | same four | 71 |
| St Kitts `IWXXMTestFiles.xlsx` | Sheet1 | 56 |
| Guyana `2-WeekTest-Log…xlsx` | same four | 53 |
| Belize `2-WeekTest-Log…xlsx` | same four | 179 |

All listed paths were readable; no blocker.
