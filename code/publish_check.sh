#!/usr/bin/env bash
# Run the mechanical publish gate. Templates, the gate itself and the scripts that
# write/remove DRAFT stamps legitimately contain the marker words.
cd "$(dirname "$0")/.."
python3 scripts/publish_gate.py . --allow-draft-in templates scripts code/08_figures.py code/10_docs.py docs/GLOSSARY.md code/publish_check.sh
