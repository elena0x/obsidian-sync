#!/bin/bash
# Deploy AI Builders Digest site to gh-pages
set -e

cd /root/.openclaw/workspace/obsidian-sync-local

# Generate site
python3 generate-site.py

# Commit to main
git add site/
git commit -m "Update site - $(date +%Y-%m-%d)" || true
git push origin main

# Deploy to gh-pages
git checkout gh-pages
git rm -rf . > /dev/null 2>&1 || true
git checkout main -- site/
mv site/* .
rm -rf site
git add .
git commit -m "Deploy site - $(date +%Y-%m-%d)" || true
git push origin gh-pages --force
git checkout main

echo "Site deployed successfully!"
