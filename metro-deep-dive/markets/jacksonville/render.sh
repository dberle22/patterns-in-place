#!/bin/bash
# Render all sections for this market to outputs/<market_name>/
# Run from the market folder: bash render.sh

MARKET=$(basename "$(pwd)")
OUTPUT_DIR="../../outputs/$MARKET"
mkdir -p "$OUTPUT_DIR"

quarto render act1_identity/s01_fingerprint.qmd --output-dir "$OUTPUT_DIR"
quarto render act1_identity/s02_history.qmd     --output-dir "$OUTPUT_DIR"
quarto render act1_identity/s03_peers.qmd       --output-dir "$OUTPUT_DIR"
quarto render act2_engine_fabric/s04_industry.qmd  --output-dir "$OUTPUT_DIR"
quarto render act2_engine_fabric/s05_built_env.qmd --output-dir "$OUTPUT_DIR"
quarto render act3_dynamics/s06_trends.qmd      --output-dir "$OUTPUT_DIR"
quarto render act3_dynamics/s07_data_take.qmd   --output-dir "$OUTPUT_DIR"
quarto render act4_funnel/s08_zones.qmd         --output-dir "$OUTPUT_DIR"
quarto render act4_funnel/s09_corridors.qmd     --output-dir "$OUTPUT_DIR"
quarto render act4_funnel/s10_parcels.qmd       --output-dir "$OUTPUT_DIR"

echo "Done — outputs in $OUTPUT_DIR"
