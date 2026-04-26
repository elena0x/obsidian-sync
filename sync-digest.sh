#!/bin/bash

# AI Builders Digest 自动同步脚本
# 每天定时运行，生成 digest 并推送到 GitHub

REPO_DIR="/root/.openclaw/workspace/obsidian-sync-local"
DATE=$(date +%Y-%m-%d)

cd "$REPO_DIR"

# 拉取最新
git pull origin main

# 保存 digest（从环境变量或文件读取）
if [ -n "$DIGEST_CONTENT" ]; then
    echo "$DIGEST_CONTENT" > "digest.md"
fi

# 添加文件
git add .

# 检查是否有更改
if git diff --staged --quiet; then
    echo "No changes to commit"
    exit 0
fi

# 提交
git commit -m "AI Builders Digest - $DATE"

# 推送
git push origin main

echo "Digest synced to GitHub - $DATE"
