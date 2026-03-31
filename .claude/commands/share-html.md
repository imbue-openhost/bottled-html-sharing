Upload an HTML file to OpenHost html-share and return a public URL.

Usage: /share-html <file_path>

Steps:
1. The file to upload is: $ARGUMENTS
2. Verify the file exists. If it doesn't, tell the user and stop.
3. Read the environment variable `OPENHOST_API_KEY`. If it's not set, tell the user to set it (e.g. `export OPENHOST_API_KEY=<token>`) and stop.
4. Upload the file using:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $OPENHOST_API_KEY" \
  -F "file=@<file_path>" \
  https://html-share.zack.dev2-host.imbue.com/upload
```

5. Parse the JSON response and extract the `url` field.
6. Display the public URL to the user. This URL is publicly accessible to anyone with the link — no login required.
