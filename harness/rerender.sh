#!/bin/zsh
# One continuous-render ROUND: if any engine source changed since the last
# round, re-render every court and refresh the quality grades. The caller
# relaunches this script when it exits, making the loop.
cd "$(dirname "$0")/.." || exit 1
STAMP=output/notes/.render_stamp

if [ -f "$STAMP" ] && [ -z "$(find centralia -name '*.py' -newer "$STAMP" | head -1)" ]; then
  echo "NO_CHANGE"
  exit 0
fi

touch "$STAMP"   # before the pass: changes landing mid-render trigger another round
for c in $(ls output | grep -v -e '^notes$' -e '^\.pageimg$'); do
  uv run python harness/cli.py render "$c" 2>&1 | tail -1
done
uv run python harness/cli.py quality 2>/dev/null | head -3
echo "ROUND_DONE"
