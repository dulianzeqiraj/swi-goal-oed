#!/bin/bash
# Word version of the karst diagram: large type and editable equations (OMML), six A4 landscape pages
# (the section, the section enlarged in two halves, the innovation, the eight panels four to a page).
# Run first: python3 karst_diagram.py && node render.js 1.5 (makes karst_diagram.png).
# Uses the Word builder of ../ml_paradigms/word (docx from npm, pandoc 3, Python with lxml).
set -e
cd "$(dirname "$0")"
python3 word_content.py
cd word_karst
node ../../ml_paradigms/word/paradigms_word.js 1 draft.docx eq.json content.json hero.png
python3 ../../ml_paradigms/word/omml.py draft.docx eq.json Karst_Aquifer_What_Changes_In_The_Model.docx
