#!/usr/bin/env bash
#
# Create a new project from the gambit-template
# and keep a link to the original repo as "upstream"
#
# Usage:
#   ./scripts/new_project.sh <new_project_name> [<new_repo_url>]
#

set -e

TEMPLATE_REPO="https://github.com/ajber/gambit-template.git"
PROJECT_NAME="$1"
NEW_REPO_URL="$2"

if [ -z "$PROJECT_NAME" ]; then
  echo "❌ Error: You must specify a new project name."
  echo "Usage: $0 <new_project_name> [<new_repo_url>]"
  exit 1
fi

echo "🚀 Creating new project '$PROJECT_NAME' from template..."

# Clone the template into a new directory
git clone "$TEMPLATE_REPO" "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Rename the origin remote to 'upstream'
git remote rename origin upstream

# Optionally add your new repo as the new origin
if [ -n "$NEW_REPO_URL" ]; then
  git remote add origin "$NEW_REPO_URL"
  echo "🔗 Added new origin: $NEW_REPO_URL"
fi

# Clean Bazel and build artifacts
rm -rf bazel-* build dist .bazel-cache .cache 2>/dev/null || true

# -------------------------------
# 🔤 Rename all instances of gambit_template → new name
# -------------------------------
OLD_NAME="gambit_template"

echo "🧩 Renaming '$OLD_NAME' → '$PROJECT_NAME' in code and paths..."

# 1. Rename folders/files that contain the old name
find . -depth -name "*${OLD_NAME}*" | while read path; do
  new_path=$(echo "$path" | sed "s/${OLD_NAME}/${PROJECT_NAME}/g")
  mv "$path" "$new_path"
done

# 2. Replace text inside files
grep -rl "$OLD_NAME" . \
  --exclude-dir=.git \
  --exclude-dir=bazel-* \
  --exclude-dir=build \
  --exclude-dir=dist \
  --exclude-dir=.cache \
  --exclude-dir=.venv \
  | xargs sed -i "s/${OLD_NAME}/${PROJECT_NAME}/g"

echo "✅ Renaming complete."

# Make an initial commit marker
git commit --allow-empty -m "Start project from gambit-template"

echo
echo "✅ Done!"
echo
echo "Next steps:"
echo "  cd $PROJECT_NAME"
if [ -n "$NEW_REPO_URL" ]; then
  echo "  git push -u origin main"
fi
echo
echo "To pull future template updates:"
echo "  git pull upstream main --rebase"
