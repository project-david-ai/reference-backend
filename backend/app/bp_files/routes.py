# backend/app/bp_files/routes.py
# ------------------------------------------------------------
# POST /bp_files/api/files/upload
# Streams uploaded files into the user’s “file_search” vector-store.
# ------------------------------------------------------------
import os
import tempfile
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from projectdavid import Entity
from projectdavid_common.utils import LoggingUtility
from werkzeug.utils import secure_filename

from . import bp_files

LOG = LoggingUtility()
client = Entity(api_key=os.environ.get("ENTITIES_API_KEY"))


# ──────────────────────────────────────────────────────────────
@bp_files.route("/api/files/upload", methods=["POST"])
@jwt_required()
def upload_files_to_vector_store():
    """
    Accepts multipart/form-data with 1‒N <input type="file"> parts.
    • Saves each part to a temp file (preserving the extension)
    • Adds it to the earliest vector-store named “file_search”
    • Deletes the temp file
    • Returns [{id,name,size,mime}, …] → front-end maps to fileIds
    """
    user_id = get_jwt_identity()

    if not request.files:
        return jsonify(error="No files found in request"), 400

    # ── resolve target vector store ────────────────────────────
    stores = client.vectors.list_my_vector_stores()
    file_search_stores = [s for s in stores if s.name == "file_search"]

    if not file_search_stores:
        LOG.warning("No 'file_search' vector store found.")
        return jsonify(error="Vector store 'file_search' not found"), 500

    earliest_store = min(
        file_search_stores, key=lambda s: getattr(s, "created_at", datetime.utcnow())
    )
    vector_store_id = earliest_store.id
    LOG.info(f"Earliest vector store for 'file_search': {vector_store_id}")

    # ── handle each uploaded file ──────────────────────────────
    uploaded_meta = []

    for storage in request.files.values():  # werkzeug FileStorage
        filename = secure_filename(storage.filename)
        if not filename:
            continue

        # keep original suffix so FileProcessor recognises it
        ext = os.path.splitext(filename)[1]  # ".pdf", ".png", …
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            storage.save(tmp)  # stream to disk
            tmp_path = tmp.name

        try:
            resp = client.vectors.add_file_to_vector_store(
                vector_store_id=vector_store_id,
                file_path=tmp_path,
                user_metadata={
                    "uploaded_by": user_id,
                    "original_name": filename,
                    "uploaded_at": datetime.utcnow().isoformat() + "Z",
                },
            )
            # Expect {"file_id": "..."}
            uploaded_meta.append(
                {
                    "id": resp.id,
                    "name": filename,
                    "size": os.path.getsize(tmp_path),
                    "mime": storage.mimetype,
                }
            )
        finally:
            os.unlink(tmp_path)  # always clean up

    if not uploaded_meta:
        return jsonify(error="No valid files processed"), 400

    return jsonify(file_metadata=uploaded_meta), 200
