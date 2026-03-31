import os
import secrets
from pathlib import Path

from quart import Quart, request, jsonify, send_from_directory, abort

app = Quart(__name__)

DATA_DIR = Path(os.environ.get("OPENHOST_APP_DATA_DIR", "./data"))
FILES_DIR = DATA_DIR / "files"


@app.before_serving
async def setup():
    FILES_DIR.mkdir(parents=True, exist_ok=True)


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

    base_url = request.host_url.rstrip("/")
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
