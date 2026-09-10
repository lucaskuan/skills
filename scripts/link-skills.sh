#!/usr/bin/env bash
set -euo pipefail

# Links every non-deprecated skill in this repo into ~/.claude/skills as a
# symlink, so a `git pull` keeps installed skills current.
# Re-run after adding, renaming, or removing a skill.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/skills"

if [ -L "$DEST" ]; then
  resolved="$(readlink "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      echo "Remove it and re-run; the script will use a real directory." >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$DEST"

linked=0
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  name="$(basename "$src")"
  target="$DEST/$name"

  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "skip $name: $target exists and is not a symlink (refusing to delete)" >&2
    continue
  fi

  ln -sfn "$src" "$target"
  echo "linked $name -> $src"
  linked=$((linked + 1))
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/deprecated/*' -print0)

echo "linked $linked skill(s) into $DEST"
