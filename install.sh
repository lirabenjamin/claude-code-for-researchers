#!/usr/bin/env bash
# Installer for claude-code-for-researchers skills.
#
# Usage (one-liner):
#   curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/install.sh | bash
#
# Install specific skills only:
#   curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/install.sh | bash -s -- pipeline-audit data-analysis
#
# Overwrite existing skills of the same name:
#   curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/install.sh | bash -s -- --force

set -euo pipefail

REPO_URL="https://github.com/lirabenjamin/claude-code-for-researchers.git"
BRANCH="main"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

FORCE=0
SELECTED=()
for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=1 ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) SELECTED+=("$arg") ;;
  esac
done

bold()  { printf '\033[1m%s\033[0m\n' "$*"; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
yellow(){ printf '\033[33m%s\033[0m\n' "$*"; }
red()   { printf '\033[31m%s\033[0m\n' "$*"; }

command -v git >/dev/null 2>&1 || { red "git is required but not installed."; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

bold "Fetching skills from $REPO_URL..."
git clone --depth 1 --branch "$BRANCH" --quiet "$REPO_URL" "$TMP/repo"

SRC="$TMP/repo/skills"
[ -d "$SRC" ] || { red "No skills/ directory in repo."; exit 1; }

mkdir -p "$DEST"

# Pick skill set (portable — no mapfile, macOS ships bash 3.2)
TO_INSTALL=()
if [ ${#SELECTED[@]} -eq 0 ]; then
  while IFS= read -r line; do
    TO_INSTALL+=("$line")
  done < <(find "$SRC" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
else
  TO_INSTALL=("${SELECTED[@]}")
fi

bold ""
bold "Installing to $DEST"
installed=()
skipped=()
missing=()

for name in "${TO_INSTALL[@]}"; do
  src_path="$SRC/$name"
  dest_path="$DEST/$name"
  if [ ! -d "$src_path" ]; then
    missing+=("$name")
    red "  ✗ $name (not found in repo)"
    continue
  fi
  if [ -d "$dest_path" ] && [ "$FORCE" -ne 1 ]; then
    skipped+=("$name")
    yellow "  ⊘ $name (already installed — use --force to overwrite)"
    continue
  fi
  rm -rf "$dest_path"
  cp -R "$src_path" "$dest_path"
  installed+=("$name")
  green "  ✓ $name"
done

echo
bold "Summary"
echo "  Installed: ${#installed[@]}"
echo "  Skipped:   ${#skipped[@]}"
[ ${#missing[@]} -gt 0 ] && echo "  Not found: ${#missing[@]}"

# Warn about skills that need configuration (bash 3.2 compatible — no assoc arrays)
config_note_for() {
  case "$1" in
    archive-raw-data)    echo ".env needs ZENODO_TOKEN + MONGODB_URI; mongoexport installed" ;;
    plate-check)         echo "{{WORKSPACE}} and {{PHONE}} placeholders in SKILL.md" ;;
    log-off)             echo "{{WORKSPACE}} and {{PHONE}} placeholders in SKILL.md" ;;
    opportunity-hunter)  echo "{{REPORTS_DIR}} placeholder in SKILL.md" ;;
    wbl-form-filler)     echo "Known Defaults block (Wharton-specific — adapt for your lab)" ;;
    qualtrics-survey)    echo ".env needs QUALTRICS_API_TOKEN + QUALTRICS_DATA_CENTER" ;;
    render-survey)       echo "Render + MongoDB Atlas accounts; OPENAI_API_KEY for AI tasks" ;;
    notify-me)           echo "macOS Messages + your phone number" ;;
    gws)                 echo "gws CLI must be installed" ;;
    *) echo "" ;;
  esac
}

config_lines=()
if [ ${#installed[@]} -gt 0 ]; then
  for name in "${installed[@]}"; do
    note=$(config_note_for "$name")
    if [ -n "$note" ]; then
      config_lines+=("$name — $note")
    fi
  done
fi

if [ ${#config_lines[@]} -gt 0 ]; then
  echo
  bold "These skills need configuration before first use:"
  for line in "${config_lines[@]}"; do
    yellow "  • $line"
  done
  echo
  echo "Open each SKILL.md and grep for {{ to find placeholders:"
  echo "  grep -l '{{' $DEST/*/SKILL.md"
fi

echo
bold "Next steps"
echo "  1. Restart Claude Code (or start a fresh session)"
echo "  2. Skills appear as slash commands, e.g. /pipeline-audit"
echo "  3. Optional: set up a global CLAUDE.md with your profile"
echo "     curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/TEMPLATE_CLAUDE.md -o ~/.claude/CLAUDE.md"
echo
green "Done."
