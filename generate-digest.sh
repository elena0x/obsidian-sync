#!/bin/bash

# AI Builders Digest 生成并同步脚本
# 在 isolated session 中运行，生成 digest、发送给用户、并推送到 GitHub

REPO_DIR="/root/.openclaw/workspace/obsidian-sync-local"
DATE=$(date +%Y-%m-%d)

# 配置
MODEL="minimax-portal/MiniMax-M2.1"

echo "开始生成 AI Builders Digest..."

# 生成 digest 内容
DIGEST=$(openclaw --model "$MODEL" --prompt "Run the follow-builders skill: execute prepare-digest.js, remix the content into a digest following the prompts. Language should be bilingual (English + Chinese side by side). Output ONLY the digest content, no additional text." 2>&1)

# 保存到文件
cd "$REPO_DIR"
echo "$DIGEST" > "digest-$DATE.md"
echo "$DIGEST" > "latest.md"

# Git 操作
git add .
git commit -m "AI Builders Digest - $DATE" || echo "No changes to commit"
git push origin main

echo "Digest 已同步到 GitHub: $DATE"
