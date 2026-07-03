#!/bin/bash
# Deploy script for AI Builders Digest site
# Run this when network access to GitHub is available

set -e

cd /root/.openclaw/workspace/obsidian-sync-local

echo "=== AI Builders Digest Site Deploy ==="
echo "Current branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline)"
echo ""

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Committing changes..."
    git add -A
    git commit -m "digest: $(date +%Y-%m-%d)"
fi

# Push to GitHub Pages
echo "Pushing to GitHub Pages..."
git push origin gh-pages

echo ""
echo "=== Deploy complete ==="
echo "Site should be live at: https://elena0x.github.io/obsidian-sync/"
