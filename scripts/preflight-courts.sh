#!/bin/sh
# Run BEFORE every commit that stages centralia/courts/__init__.py.
# Fails loudly if the INDEX would import a module the index does not carry.
cd /Users/Palin/Code/rewrite || exit 2
git diff --cached --name-only | grep -q 'centralia/courts/__init__.py' || {
  echo "preflight: __init__.py not staged, nothing to check"; exit 0; }
tree=$(git write-tree) || exit 2
git ls-tree -r --name-only "$tree" centralia/courts/ | sed 's#.*/##; s#\.py$##' \
  | grep -v __init__ | sort > /tmp/pf_tracked.txt
git show "$tree:centralia/courts/__init__.py" \
  | grep -oE '^from \. import [a-z0-9_]+' | awk '{print $4}' | sort > /tmp/pf_imports.txt
missing=$(comm -23 /tmp/pf_imports.txt /tmp/pf_tracked.txt)
if [ -n "$missing" ]; then
  echo "PREFLIGHT FAIL — staged __init__.py imports modules the index lacks:"
  echo "$missing" | sed 's/^/    /'
  echo "  Either stage those modules too, or unstage centralia/courts/__init__.py."
  exit 1
fi
echo "preflight OK — every staged import has a module in the index"
