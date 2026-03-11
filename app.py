#!/usr/bin/env -S venv/bin/python3
"""
Website Compliance Crawler - Web Interface

Lokales Web-Interface für den Compliance Crawler.
Startet einen Flask-Server und öffnet den Browser.
"""

import io
import json
import sys
import threading
import time
import uuid
import webbrowser
from contextlib import redirect_stdout
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, Response, jsonify, render_template, request, send_file

from crawler import (
    crawl_urls_only,
    crawl_with_content,
    normalize_domain,
)

app = Flask(__name__)

# Store für laufende Jobs: job_id -> {"messages": [...], "done": bool, "result": dict}
jobs = {}


class StreamCapture(io.StringIO):
    """Captured stdout und speichert Zeilen in einer Job-Message-Queue."""

    def __init__(self, job_id):
        super().__init__()
        self.job_id = job_id

    def write(self, text):
        if text.strip():
            jobs[self.job_id]["messages"].append(("log", text.strip()))
        return super().write(text)


def run_crawl(job_id, domain, shop_type, extract_content,
              categories, exclude, max_urls):
    """Führt den Crawl in einem Background-Thread aus."""
    output_dir = Path("output")
    capture = StreamCapture(job_id)

    try:
        with redirect_stdout(capture):
            if extract_content:
                urls_data, content_data = crawl_with_content(
                    domain, output_dir, max_urls, categories, exclude, shop_type
                )
                # Ergebnis zusammenstellen
                result = {
                    "total_urls": content_data["total_urls"],
                    "successful": content_data["successful"],
                    "failed": content_data["failed"],
                    "categories": {
                        cat: len(urls) for cat, urls in urls_data["urls"].items()
                    },
                    "urls_file": None,
                    "content_file": None,
                }
                # Finde die zuletzt geschriebenen Dateien
                urls_files = sorted(output_dir.glob("*_urls.json"))
                if urls_files:
                    result["urls_file"] = urls_files[-1].name
                content_files = sorted(output_dir.glob("*_content.json"))
                if content_files:
                    result["content_file"] = content_files[-1].name
            else:
                urls_data = crawl_urls_only(domain, output_dir, shop_type)
                result = {
                    "total_urls": urls_data["total_urls"],
                    "successful": urls_data["total_urls"],
                    "failed": len(urls_data["errors"]),
                    "categories": {
                        cat: len(urls) for cat, urls in urls_data["urls"].items()
                    },
                    "urls_file": None,
                    "content_file": None,
                }
                urls_files = sorted(output_dir.glob("*_urls.json"))
                if urls_files:
                    result["urls_file"] = urls_files[-1].name

        # Progress-Update mit finalen Stats
        jobs[job_id]["messages"].append(("progress", json.dumps({
            "urls": result["total_urls"],
            "extracted": result.get("successful", 0),
            "policies": result["categories"].get("policies", 0),
            "errors": result["failed"],
        })))

        jobs[job_id]["messages"].append(("done", json.dumps(result)))

    except Exception as e:
        jobs[job_id]["messages"].append(("error", str(e)))

    finally:
        jobs[job_id]["done"] = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/crawl", methods=["POST"])
def start_crawl():
    data = request.get_json()

    # Validierung
    try:
        domain = normalize_domain(data.get("domain", ""))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    shop_type = data.get("shop_type") or None
    extract_content = data.get("extract_content", False)
    categories = data.get("categories") or None
    exclude = data.get("exclude") or None
    max_urls = data.get("max_urls") or None

    if categories and exclude:
        return jsonify({"error": "categories und exclude nicht gleichzeitig möglich"}), 400

    # Job erstellen
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"messages": [], "done": False, "result": None}

    # Crawl im Background starten
    thread = threading.Thread(
        target=run_crawl,
        args=(job_id, domain, shop_type, extract_content,
              categories, exclude, max_urls),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/stream/<job_id>")
def stream(job_id):
    if job_id not in jobs:
        return jsonify({"error": "Job nicht gefunden"}), 404

    def generate():
        idx = 0
        while True:
            job = jobs[job_id]
            messages = job["messages"]

            while idx < len(messages):
                event_type, data = messages[idx]
                yield f"event: {event_type}\ndata: {data}\n\n"
                idx += 1

                if event_type in ("done", "error"):
                    return

            if job["done"] and idx >= len(messages):
                return

            time.sleep(0.1)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/download/<filename>")
def download(filename):
    # Sicherheitscheck: nur Dateien aus output/
    if ".." in filename or "/" in filename:
        return jsonify({"error": "Ungültiger Dateiname"}), 400
    filepath = Path("output") / filename
    if not filepath.exists() or not filepath.is_file():
        return jsonify({"error": "Datei nicht gefunden"}), 404
    return send_file(filepath, as_attachment=True)


@app.route("/content/<filename>")
def content(filename):
    """Gibt den JSON-Inhalt als Text zurück (für Clipboard-Copy)."""
    if ".." in filename or "/" in filename:
        return jsonify({"error": "Ungültiger Dateiname"}), 400
    filepath = Path("output") / filename
    if not filepath.exists() or not filepath.is_file():
        return jsonify({"error": "Datei nicht gefunden"}), 404
    return Response(filepath.read_text(encoding="utf-8"), mimetype="text/plain")


@app.route("/open-output", methods=["POST"])
def open_output():
    """Öffnet den Output-Ordner im Finder (macOS)."""
    import subprocess
    output_dir = Path("output").resolve()
    if output_dir.exists():
        subprocess.Popen(["open", str(output_dir)])
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = 8080
    print("\n  Compliance Crawler Web-Interface")
    print(f"  http://localhost:{port}\n")

    # Browser nach kurzer Verzögerung öffnen
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    app.run(host="127.0.0.1", port=port, debug=False)
