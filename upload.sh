#!/bin/bash
# Upload an HTML file to html-share on OpenHost
# Usage: ./upload.sh <file_path> <openhost_api_key> [host]
#
# Returns the public URL where the file can be viewed.

set -euo pipefail

FILE_PATH="${1:?Usage: ./upload.sh <file_path> <api_key> [host]}"
API_KEY="${2:?Usage: ./upload.sh <file_path> <api_key> [host]}"
HOST="${3:-https://html-share.zack.dev2-host.imbue.com}"

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH" >&2
    exit 1
fi

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -F "file=@$FILE_PATH" \
    "$HOST/upload")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
    URL=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" 2>/dev/null)
    if [ -n "$URL" ]; then
        echo "$URL"
    else
        echo "$BODY"
    fi
else
    echo "Error (HTTP $HTTP_CODE): $BODY" >&2
    exit 1
fi
