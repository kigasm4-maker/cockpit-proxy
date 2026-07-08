#!/bin/sh
# Pipeline de publication : quality gate + fingerprint check.
# Usage : ./publish.sh mon_texte.md
# Ne publie rien si l'un des deux gates échoue (exit 1).
set -e
FICHIER="$1"
[ -f "$FICHIER" ] || { echo "Usage : ./publish.sh <fichier>"; exit 1; }
DIR="$(dirname "$0")"
echo "── Gate 1/2 : quality_gate ──"
python3 "$DIR/quality_gate.py" "$FICHIER"
echo ""
echo "── Gate 2/2 : fingerprint_check ──"
python3 "$DIR/fingerprint_check.py" "$FICHIER"
echo ""
echo "🚀 Les deux gates sont passés : $FICHIER est prêt à publier."
