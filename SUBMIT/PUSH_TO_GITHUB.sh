#!/bin/bash
# =============================================================================
#  Puts this whole folder on GitHub so the team can access it.
#
#  RUN THIS:
#      bash ~/Desktop/Wapor_2026_hackathon/SUBMIT/PUSH_TO_GITHUB.sh
#
#  First run: it will ask you to sign in to GitHub in your browser. That is
#  normal and only happens once.
# =============================================================================
set -e
cd "$(dirname "$0")"

REPO_NAME="same-budget-more-water"
VISIBILITY="public"          # change to private if you would rather

echo ""
echo "  Publishing to GitHub"
echo "  ===================="

# ---------- git ----------
if ! command -v git >/dev/null 2>&1; then
  echo "  ✗ git is not installed."
  echo "    Run:  xcode-select --install     then try again."
  exit 1
fi

# ---------- GitHub CLI: does the sign in and makes the repo for you ----------
if ! command -v gh >/dev/null 2>&1; then
  echo "  · installing the GitHub command line tool"
  if command -v brew >/dev/null 2>&1; then
    brew install gh
  else
    echo "  ✗ Homebrew is not installed, so I cannot install gh automatically."
    echo ""
    echo "    EASIEST ALTERNATIVE, no terminal needed:"
    echo "      1. Download GitHub Desktop:  https://desktop.github.com"
    echo "      2. File > Add Local Repository, choose this SUBMIT folder"
    echo "      3. Click 'Publish repository'"
    exit 1
  fi
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "  · signing you in to GitHub, follow the prompts in the browser"
  gh auth login
fi

# ---------- ignore the heavy and the pointless ----------
cat > .gitignore <<'EOF'
.DS_Store
__pycache__/
*.pyc
data/raw/
data/interim/seasonal/
media/
.vo/
EOF

# ---------- commit ----------
if [ ! -d .git ]; then
  git init -q
  git branch -M main
fi
git add -A
if git diff --cached --quiet; then
  echo "  · nothing new to commit"
else
  git commit -q -m "Same Budget, More Water: WaPOR based allocation of Egypt's on-farm modernisation budget"
  echo "  ✓ committed"
fi

# ---------- create the repo and push ----------
if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
else
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
fi

URL=$(gh repo view --json url -q .url 2>/dev/null || echo "")
echo ""
echo "  ✓ DONE"
[ -n "$URL" ] && echo "    $URL"
echo ""
echo "  Share that link with the team, and put it on the Miro board."
echo "  To publish updates later, just run this script again."
echo ""
