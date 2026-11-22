#!/usr/bin/env bash
# Download the public USGS report SIR 2004-5067 (Land et al., 2004) and extract Appendix A and Table 2.
# The data are public domain (U.S. Geological Survey); they are written to ./data, which is not committed.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data/raw
curl -s -L -o data/raw/sir2004-5067.pdf "https://pubs.usgs.gov/sir/2004/5067/sir2004-5067.pdf"
pdftotext -f 54 -l 61 -bbox data/raw/sir2004-5067.pdf data/raw/appA_bbox.html     # Appendix A (PDF pages 54-61)
pdftotext -f 22 -l 24 -layout data/raw/sir2004-5067.pdf data/raw/table2.txt       # Table 2 (PDF pages 22-24)
python3 -I parse_appA.py data/raw/appA_bbox.html data/appA.csv
python3 -I parse_table2.py data/raw/table2.txt data/table2.csv
