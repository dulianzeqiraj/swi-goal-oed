# word_tools

Shared helpers for the Word builders of the notes and reviews in `experiments/*`:

| File | Content |
|---|---|
| `build_sota.py` | runs, links, paragraphs, headings, rich text, shaded cells and tables (python-docx) |
| `build_methodology.py` | the equation register `Eqs`, text with inline math, displayed and numbered equations |
| `build_annex.py` | page-number fields and two-column sections |
| `omml_render.py` | renders the OMML equations of a .docx for LibreOffice and writes a PDF (`python omml_render.py IN.docx OUT.docx --pdf DIR`) |

The equations are converted with `../ml_paradigms/word/omml.py` (needs pandoc).
