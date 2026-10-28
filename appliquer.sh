#!/usr/bin/env bash
# Usage : ./appliquer.sh squelette      (point de depart de la seance)
#         ./appliquer.sh solution       (correction, a n'ouvrir qu'en dernier recours)
#         ./appliquer.sh squelette --force   (ecrase votre travail !)
set -e
VARIANTE="${1:-squelette}"
DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR/variantes/$VARIANTE"
MARQUEUR="$DIR/.variante_appliquee"

if [ ! -d "$SRC" ]; then
  echo "Variante inconnue : $VARIANTE (choix : squelette ou solution)"; exit 1
fi
if [ -f "$MARQUEUR" ] && [ "$2" != "--force" ]; then
  echo "Une variante a deja ete appliquee ($(cat "$MARQUEUR"))."
  echo "Pour ne pas ecraser votre travail, rien n'a ete fait."
  echo "Si vous etes sur, relancez avec : ./appliquer.sh $VARIANTE --force"; exit 1
fi
cp "$SRC/views.py" "$SRC/serializers.py" "$SRC/services.py" "$DIR/api/"
echo "$VARIANTE" > "$MARQUEUR"
echo "Variante '$VARIANTE' appliquee dans api/ (views.py, serializers.py, services.py)."
