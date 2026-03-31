Upload an HTML file to OpenHost html-share and return a public URL.

Usage: /share-html <file_path>

Steps:
1. The file to upload is: $ARGUMENTS
2. Verify the file exists. If it doesn't, tell the user and stop.
3. Read the environment variables `OPENHOST_API_KEY` and `OPENHOST_DOMAIN`. If either is not set, tell the user to set them (e.g. `export OPENHOST_API_KEY=<token>` and `export OPENHOST_DOMAIN=https://your-space.host.imbue.com`) and stop.
4. Strip the protocol from `OPENHOST_DOMAIN` to get just the domain (e.g. `https://your-space.host.imbue.com` → `your-space.host.imbue.com`), then upload the file using:

```bash
DOMAIN=$(echo "$OPENHOST_DOMAIN" | sed 's|^https://||')
curl -s -X POST \
  -H "Authorization: Bearer $OPENHOST_API_KEY" \
  -F "file=@<file_path>" \
  "https://html-share.$DOMAIN/upload"
```

5. Parse the JSON response and extract the `url` field.
6. Display the public URL to the user. This URL is publicly accessible to anyone with the link — no login required.
