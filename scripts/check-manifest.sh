#!/usr/bin/env bash
set -euo pipefail

# Verifies that every skill in a promoted bucket is listed in
# .claude-plugin/plugin.json, and that nothing else is.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

PROMOTED="fleet workflow review"
fail=0

on_disk="$(for b in $PROMOTED; do
  find "skills/$b" -name SKILL.md 2>/dev/null | sed 's|/SKILL.md$||' | sed 's|^|./|'
done | sort)"

in_manifest="$(grep -o '"\./skills/[^"]*"' .claude-plugin/plugin.json | tr -d '"' | sort)"

missing="$(comm -23 <(echo "$on_disk") <(echo "$in_manifest"))"
extra="$(comm -13 <(echo "$on_disk") <(echo "$in_manifest"))"

if [ -n "$missing" ]; then
  echo "MISSING from plugin.json:"; echo "$missing" | sed 's|^|  |'; fail=1
fi
if [ -n "$extra" ]; then
  echo "IN plugin.json but not a promoted skill on disk:"; echo "$extra" | sed 's|^|  |'; fail=1
fi

for b in $PROMOTED; do
  while IFS= read -r s; do
    [ -z "$s" ] && continue
    name="$(basename "$s")"
    [ -f "docs/$b/$name.md" ] || { echo "MISSING docs page: docs/$b/$name.md"; fail=1; }
  done < <(find "skills/$b" -name SKILL.md 2>/dev/null | sed 's|/SKILL.md$||')
done

[ "$fail" -eq 0 ] && echo "manifest OK"
exit $fail
