#!/bin/bash

# AI Builders Digest 自动同步脚本 (使用 GitHub API)
# 每天定时运行，生成 digest 并推送到 GitHub

TOKEN="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"
REPO="elennnnasweet-del/obsidian-sync"
DATE=$(date +%Y-%m-%d)
DIGEST_FILE="/root/.openclaw/workspace/obsidian-sync-local/digest-$DATE.md"
LATEST_FILE="/root/.openclaw/workspace/obsidian-sync-local/latest.md"

echo "Starting AI Builders Digest sync - $DATE"

# 检查文件是否存在
if [ ! -f "$DIGEST_FILE" ]; then
    echo "Digest file not found: $DIGEST_FILE"
    exit 1
fi

# 上传 digest 文件
CONTENT=$(base64 -w0 < "$DIGEST_FILE")
RESPONSE=$(curl -s -X PUT "https://api.github.com/repos/$REPO/contents/digest-$DATE.md" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"AI Builders Digest - $DATE\",
    \"content\": \"$CONTENT\"
  }")

if echo "$RESPONSE" | grep -q "content"; then
    echo "Digest uploaded: digest-$DATE.md"
else
    echo "Error uploading digest: $RESPONSE"
fi

# 上传 latest 文件
CONTENT=$(base64 -w0 < "$LATEST_FILE")
RESPONSE=$(curl -s -X PUT "https://api.github.com/repos/$REPO/contents/latest.md" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"AI Builders Digest - Latest\",
    \"content\": \"$CONTENT\"
  }")

if echo "$RESPONSE" | grep -q "content"; then
    echo "Latest digest uploaded: latest.md"
else
    echo "Error uploading latest: $RESPONSE"
fi

echo "Sync complete!"
