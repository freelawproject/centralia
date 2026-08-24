#!/bin/sh
# Rebuild the centralia wheel into docs/wheels/ and record its filename.
# The wheel is committed on purpose: GitHub Pages is static, so the browser
# fetches it straight off the site. Re-run after any change to centralia/.
set -e
cd "$(dirname "$0")/.."
rm -f docs/wheels/*.whl
uv build --wheel -o docs/wheels
WHEEL=$(basename docs/wheels/*.whl)
printf '{"wheel": "%s"}\n' "$WHEEL" > docs/wheels/manifest.json
echo "built $WHEEL ($(du -h "docs/wheels/$WHEEL" | cut -f1))"
