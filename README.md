# html-share

An OpenHost app that lets you upload HTML files and serve them at secret public URLs.

## How it works

- **Upload** (`POST /upload`) — Authenticated endpoint. Upload an HTML file and get back a public URL with a random secret token.
- **View** (`GET /shared/<token>/<filename>`) — Public. Anyone with the URL can view the file.
- **Index** (`GET /`) — Authenticated. Lists all uploaded files with public URLs and delete buttons.

## Deploying

```bash
oh app deploy https://github.com/imbue-ai/openhost-html-sharing
```

## Usage

### Claude skill

Set environment variables:

```bash
export OPENHOST_API_KEY=<your-token>
export OPENHOST_DOMAIN=https://your-space.dev2-host.imbue.com
```

Then use `/share-html path/to/file.html` in Claude Code.

### curl

```bash
curl -X POST \
  -H "Authorization: Bearer $OPENHOST_API_KEY" \
  -F "file=@path/to/file.html" \
  https://html-share.your-space.dev2-host.imbue.com/upload
```

Returns JSON:

```json
{
  "url": "https://html-share.your-space.dev2-host.imbue.com/shared/<token>/file.html",
  "token": "<token>",
  "filename": "file.html"
}
```
