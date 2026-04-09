import os
import shutil
import secrets
from pathlib import Path

from quart import Quart, request, jsonify, send_from_directory, abort, redirect, url_for

app = Quart(__name__)

DATA_DIR = Path(os.environ.get("OPENHOST_APP_DATA_DIR", "./data"))
FILES_DIR = DATA_DIR / "files"


@app.before_serving
async def setup():
    FILES_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
async def index():
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host", "")
    base_url = f"https://{host}"
    files = []
    if FILES_DIR.exists():
        for token_dir in sorted(FILES_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if token_dir.is_dir():
                for f in token_dir.iterdir():
                    if f.is_file():
                        files.append({
                            "token": token_dir.name,
                            "filename": f.name,
                            "url": f"{base_url}/shared/{token_dir.name}/{f.name}",
                            "size": f.stat().st_size,
                        })

    rows = ""
    for f in files:
        rows += f"""
        <tr>
            <td><a href="{f['url']}" target="_blank">{f['filename']}</a></td>
            <td>{f['size']:,} B</td>
            <td><a href="{f['url']}" target="_blank">{f['url']}</a></td>
            <td>
                <form method="POST" action="/delete/{f['token']}/{f['filename']}"
                      onsubmit="return confirm('Delete {f['filename']}?')">
                    <button type="submit">Delete</button>
                </form>
            </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><title>html-share</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #ddd; }}
button {{ cursor: pointer; }}
</style>
</head><body>
<h1>html-share</h1>
<div style="margin: 1rem 0; display: flex; gap: 0.5rem; align-items: center;">
    <input type="file" id="fileInput">
    <button onclick="uploadFile()">Upload</button>
    <span id="uploadStatus"></span>
</div>
<script>
async function uploadFile() {{
    const input = document.getElementById('fileInput');
    const status = document.getElementById('uploadStatus');
    if (!input.files.length) return;
    status.textContent = 'Uploading...';
    const form = new FormData();
    form.append('file', input.files[0]);
    try {{
        const res = await fetch('/upload', {{ method: 'POST', body: form }});
        if (!res.ok) throw new Error(await res.text());
        status.textContent = '';
        location.reload();
    }} catch (e) {{
        status.textContent = 'Error: ' + e.message;
    }}
}}
</script>
<p>{len(files)} file(s) uploaded</p>
<table>
<tr><th>File</th><th>Size</th><th>Public URL</th><th></th></tr>
{rows}
</table>
</body></html>"""


@app.route("/delete/<token>/<filename>", methods=["POST"])
async def delete_file(token, filename):
    file_dir = FILES_DIR / token
    filepath = file_dir / filename
    if filepath.exists():
        filepath.unlink()
    if file_dir.exists() and not any(file_dir.iterdir()):
        shutil.rmtree(file_dir)
    return redirect(url_for("index"))


@app.route("/upload", methods=["POST"])
async def upload():
    files = await request.files
    if "file" not in files:
        return jsonify({"error": "No file provided"}), 400

    file = files["file"]
    if not file.filename:
        return jsonify({"error": "No filename"}), 400

    token = secrets.token_urlsafe(24)

    upload_dir = FILES_DIR / token
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename
    filepath = upload_dir / filename
    await file.save(str(filepath))

    # Use forwarded host from the OpenHost reverse proxy; always https
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host", "")
    base_url = f"https://{host}"
    public_url = f"{base_url}/shared/{token}/{filename}"

    return jsonify({"url": public_url, "token": token, "filename": filename})


@app.route("/shared/<token>/<path:filename>")
async def serve_file(token, filename):
    file_dir = FILES_DIR / token
    filepath = file_dir / filename

    if not filepath.exists():
        abort(404)

    return await send_from_directory(str(file_dir), filename)


@app.route("/health")
async def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
