from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from xlfConvater import translate_xlf_to_english
from xlf_utils import XLFParseError, parse_xlf_document

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "converted"
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)


def validate_xlf_file(file_path: Path):
    """Return (is_valid, payload). Payload contains either stats or error text."""
    try:
        parsed = parse_xlf_document(file_path)
    except XLFParseError as exc:
        return False, {"error": f"Invalid XLF XML: {exc}"}

    tree = parsed.tree
    root = tree.getroot()
    namespaces = [
        {"xliff": "urn:oasis:names:tc:xliff:document:1.2"},
        {},
    ]
    trans_units = []
    for ns in namespaces:
        xpath = ".//xliff:trans-unit" if ns else ".//trans-unit"
        trans_units = root.findall(xpath, ns)
        if trans_units:
            break

    if not trans_units:
        return False, {"error": "No <trans-unit> nodes found in the XLF payload."}

    total_units = len(trans_units)
    missing_sources = 0
    for unit in trans_units:
        source = unit.find("xliff:source", {"xliff": "urn:oasis:names:tc:xliff:document:1.2"})
        if source is None:
            source = unit.find("source")
        if source is None or not (source.text or "").strip():
            missing_sources += 1

    payload = {"total_units": total_units, "missing_sources": missing_sources}
    if parsed.recovered:
        payload["warnings"] = [
            "Input XML contained structural issues that were auto-corrected before translation."
        ]

    return True, payload


@app.get("/")
def index():
    """Serve the converter UI."""
    return render_template("index.html")


@app.post("/api/convert")
def api_convert():
    """Translate XLF content (uploaded file or pasted text) from Bangla to English."""
    uploaded_file = request.files.get("xlfFile")
    request_data = request.get_json(silent=True) or {}
    if not isinstance(request_data, dict):
        request_data = {}
    pasted_text = (request_data.get("xlfText") or "").strip()

    if uploaded_file and uploaded_file.filename.strip():
        safe_input_name = secure_filename(uploaded_file.filename) or "input.xlf"
        suffix = Path(safe_input_name).suffix or ".xlf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            uploaded_file.save(tmp.name)
            temp_input_path = Path(tmp.name)
    elif pasted_text:
        safe_input_name = "pasted_input.xlf"
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".xlf", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(pasted_text)
            temp_input_path = Path(tmp.name)
    else:
        return jsonify({"error": "Provide an XLF file or paste the XML text."}), 400

    is_valid, validation_payload = validate_xlf_file(temp_input_path)
    if not is_valid:
        temp_input_path.unlink(missing_ok=True)
        return jsonify(validation_payload), 400

    output_name = f"{Path(safe_input_name).stem or 'converted'}_{uuid.uuid4().hex[:8]}_English.xlf"
    output_path = OUTPUT_DIR / output_name

    try:
        translate_xlf_to_english(str(temp_input_path), str(output_path))
        output_text = output_path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - surface errors to UI
        return jsonify({"error": f"Conversion failed: {exc}"}), 500
    finally:
        temp_input_path.unlink(missing_ok=True)

    return jsonify(
        {
            "message": "Translation complete!",
            "downloadUrl": f"/download/{output_name}",
            "outputPath": str(output_path.resolve()),
            "outputText": output_text,
            "fileName": output_name,
            "stats": validation_payload,
        }
    )


@app.get("/download/<path:filename>")
def download_file(filename: str):
    """Allow the user to download a converted XLF file."""
    safe_name = secure_filename(filename)
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists():
        return jsonify({"error": "Requested file not found."}), 404
    return send_from_directory(OUTPUT_DIR, safe_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8001)
