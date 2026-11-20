#!/usr/bin/env bash
# Download the Q4 2026 Washington data used in this repo into ./data (about 640 MiB unzipped).
# These filenames identify the archived Q4 2026 release.
set -euo pipefail
mkdir -p data && cd data
get() { curl -fsSL -A "Mozilla/5.0" -O "$1"; }

# Washington DOR downloads (https://dor.wa.gov/taxes-rates/sales-use-tax-rates/downloadable-database)
get https://dor.wa.gov/sites/default/files/2026-08/State_26Q4.zip      # address file (State_26Q4.txt)
get https://dor.wa.gov/sites/default/files/2026-08/Zip4Q426C.zip       # ZIP+4 file, short
get https://dor.wa.gov/sites/default/files/2026-08/Zip4Q426E.zip       # ZIP+4 file, long
get https://dor.wa.gov/sites/default/files/2026-08/Rates_26Q4.zip      # location codes and rates
get https://dor.wa.gov/sites/default/files/2026-08/StateWRLS_26Q4.zip  # wireless (MTSA) file

# Washington's Streamlined Sales Tax boundary file (https://streamlinedsalestax.org/ratesandboundry/Boundary/)
get https://streamlinedsalestax.org/ratesandboundry/Boundary/WAB2026Q4AUG27.zip
get https://www.streamlinedsalestax.org/ratesandboundry/Rates/WAR2026Q4AUG27.zip

for z in *.zip; do unzip -oq "$z"; done
ls -la
