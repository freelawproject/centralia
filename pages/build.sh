#!/bin/sh
# Rebuild the centralia wheel into pages/wheels/ and record its filename.
# The wheel is committed on purpose: GitHub Pages is static, so the browser
# fetches it straight off the site. Re-run after any change to centralia/.
set -e
cd "$(dirname "$0")/.."
rm -f pages/wheels/*.whl
uv build --wheel -o pages/wheels
WHEEL=$(basename pages/wheels/*.whl)
printf '{"wheel": "%s"}\n' "$WHEEL" > pages/wheels/manifest.json
echo "built $WHEEL ($(du -h "pages/wheels/$WHEEL" | cut -f1))"
