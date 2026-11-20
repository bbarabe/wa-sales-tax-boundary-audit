#!/usr/bin/env bash
# Build DOR's sample library (WaRateFileLookup 1.0.5, unmodified) with Mono and run it on test inputs.
# Requires: mono-mcs, mono-runtime (Ubuntu: apt-get install mono-mcs mono-runtime).
# Usage: scripts/wsrl/run_wsrl.sh DATA_DIR TESTS.tsv   (DATA_DIR holds State_26Q4.txt, Rates_26Q4.csv,
#        Zip4RatesQ42026-Short.txt; TESTS.tsv lines: id<TAB>street line<TAB>city<TAB>zip)
# Note: the library only loads rows for the current calendar quarter (Period.CurrentPeriod()).
set -euo pipefail
DATA=$(realpath "$1"); TESTS=$(realpath "$2"); HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(mktemp -d); cd "$WORK"
curl -fsSL -A "Mozilla/5.0" -O https://dor.wa.gov/sites/default/files/2022-06/WaRateFileLookup-1.0.5.zip
unzip -q WaRateFileLookup-1.0.5.zip -d src
SRC=src/WaRateFileLookup/WaRateFiles
FILES=$(find "$SRC" -name "*.cs" -not -path "*/UnitTest/*" -not -name FileMaintenance.cs)
mcs -nowarn:618,219,414,168 -target:library -out:WaRateFiles.dll -r:System.Configuration.dll $FILES
mcs -out:Driver.exe -r:WaRateFiles.dll "$HERE/Driver.cs"
mono Driver.exe "$DATA" "$TESTS"
