"""
tests/integration/files_intrusion.py

File ownership isolation sweep for Project David.
Tests that row-level access control is correctly enforced on all file endpoints.

Fixtures:
  owner   — user_BG5JyzwSLb4dVfDqzJoH8u  (OWNER_API_KEY)
  intruder — user_v1LoJ7wFyLhIrPiaqlpyJS (INTRUDER_API_KEY)

Run:
    python -m tests.integration.files_intrusion
"""

import os
import tempfile
import traceback
from typing import Optional

from dotenv import load_dotenv
from projectdavid import Entity

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
BASE_URL = os.getenv("ENTITIES_BASE_URL", "http://localhost:9000")
OWNER_KEY = os.getenv("OWNER_API_KEY")
INTRUDER_KEY = os.getenv("INTRUDER_API_KEY")

if not OWNER_KEY or not INTRUDER_KEY:
    raise RuntimeError(
        "Set OWNER_API_KEY and INTRUDER_API_KEY in your environment or .env file."
    )

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
results: dict = {}


def record(label: str, passed: bool, note: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    tag = "✅" if passed else "❌"
    print(f"[{status}] {tag}  {label}" + (f": {note}" if note else ""))
    results[label] = status


def expect_success(label: str, fn, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        record(label, True)
        return result
    except Exception as exc:
        record(label, False, str(exc))
        return None


def expect_error(label: str, expected_codes: tuple, fn, *args, **kwargs):
    """
    Calls fn(*args, **kwargs) and expects an HTTP error whose status code is in
    expected_codes.  Any other outcome (success or wrong status) is a FAIL.
    """
    try:
        fn(*args, **kwargs)
        record(label, False, "Expected error but call succeeded")
        return None
    except Exception as exc:
        msg = str(exc)
        matched = any(str(code) in msg for code in expected_codes)
        record(label, matched, msg)
        return exc


# ──────────────────────────────────────────────────────────────────────────────
# Clients
# ──────────────────────────────────────────────────────────────────────────────
owner_client = Entity(base_url=BASE_URL, api_key=OWNER_KEY)
intruder_client = Entity(base_url=BASE_URL, api_key=INTRUDER_KEY)

# ──────────────────────────────────────────────────────────────────────────────
# Temp file fixture
# ──────────────────────────────────────────────────────────────────────────────
tmp = tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".txt",
    prefix="files_isolation_",
    delete=False,
)
tmp.write("Project David — file isolation test fixture\n")
tmp.close()
TMP_PATH = tmp.name
print(f"\n[SETUP] Temp file created: {TMP_PATH}")

# ──────────────────────────────────────────────────────────────────────────────
# State
# ──────────────────────────────────────────────────────────────────────────────
owner_file_id: Optional[str] = None

# ──────────────────────────────────────────────────────────────────────────────
# SWEEP
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("FILE ISOLATION SWEEP")
print("═" * 60)

# ── Test 1: Owner uploads file ────────────────────────────────────────────────
print("\n--- Test 1: Owner uploads file (expecting success) ---")
owner_file = expect_success(
    "Test 1: Owner uploads file",
    owner_client.files.upload_file,
    TMP_PATH,
    "assistants",
)
if owner_file:
    owner_file_id = owner_file.id
    print(f"  file.id      : {owner_file.id}")
    print(f"  file.filename: {owner_file.filename}")
    print(f"  file.purpose : {owner_file.purpose}")

# ── Test 2: Owner retrieves own file metadata ─────────────────────────────────
print("\n--- Test 2: Owner retrieves own file metadata (expecting success) ---")
if owner_file_id:
    retrieved = expect_success(
        "Test 2: Owner retrieves own file metadata",
        owner_client.files.retrieve_file,
        owner_file_id,
    )
    if retrieved:
        print(f"  retrieved.id       : {retrieved.id}")
        print(f"  retrieved.filename : {retrieved.filename}")

# ── Test 3: Intruder retrieves owner's file metadata ─────────────────────────
print("\n--- Test 3: Intruder retrieves owner's file metadata (expecting 403/404) ---")
if owner_file_id:
    expect_error(
        "Test 3: Intruder retrieves owner's file metadata",
        (403, 404),
        intruder_client.files.retrieve_file,
        owner_file_id,
    )

# ── Test 4: Intruder requests Base64 of owner's file ─────────────────────────
print("\n--- Test 4: Intruder requests Base64 of owner's file (expecting 403/404) ---")
if owner_file_id:
    expect_error(
        "Test 4: Intruder requests Base64 of owner's file",
        (403, 404),
        intruder_client.files.get_file_as_base64,
        owner_file_id,
    )

# ── Test 5: Owner gets Base64 of own file ────────────────────────────────────
print("\n--- Test 5: Owner gets Base64 of own file (expecting success) ---")
if owner_file_id:
    b64 = expect_success(
        "Test 5: Owner gets Base64 of own file",
        owner_client.files.get_file_as_base64,
        owner_file_id,
    )
    if b64:
        print(f"  base64 length: {len(b64)} chars")

# ── Test 6: Intruder requests signed URL for owner's file ────────────────────
print(
    "\n--- Test 6: Intruder requests signed URL for owner's file (expecting 403/404) ---"
)
if owner_file_id:
    expect_error(
        "Test 6: Intruder requests signed URL for owner's file",
        (403, 404),
        intruder_client.files.get_signed_url,
        owner_file_id,
    )

# ── Test 7: Owner gets signed URL for own file ───────────────────────────────
print("\n--- Test 7: Owner gets signed URL for own file (expecting success) ---")
if owner_file_id:
    signed_url = expect_success(
        "Test 7: Owner gets signed URL for own file",
        owner_client.files.get_signed_url,
        owner_file_id,
    )
    if signed_url:
        print(f"  signed_url: {signed_url[:80]}...")

# ── Test 8: Intruder deletes owner's file ────────────────────────────────────
print("\n--- Test 8: Intruder deletes owner's file (expecting 403/404) ---")
if owner_file_id:
    # FileClient.delete_file returns False on 404 rather than raising — check
    # the file still exists after the intruder call to confirm no deletion.
    try:
        result = intruder_client.files.delete_file(owner_file_id)
        # If it returned False that's a 404 response — acceptable isolation
        # If it returned True that's a leak
        if result is True:
            record(
                "Test 8: Intruder deletes owner's file",
                False,
                "Intruder call returned True — file may have been deleted!",
            )
        else:
            # Verify file still exists for owner
            still_there = owner_client.files.retrieve_file(owner_file_id)
            if still_there:
                record(
                    "Test 8: Intruder deletes owner's file",
                    True,
                    "Returned False and file still exists for owner",
                )
            else:
                record(
                    "Test 8: Intruder deletes owner's file",
                    False,
                    "File is gone after intruder call",
                )
    except Exception as exc:
        msg = str(exc)
        matched = any(str(code) in msg for code in (403, 404))
        record("Test 8: Intruder deletes owner's file", matched, msg)

# ── Test 9: Owner deletes own file ───────────────────────────────────────────
print("\n--- Test 9: Owner deletes own file (expecting success) ---")
if owner_file_id:
    deleted = expect_success(
        "Test 9: Owner deletes own file",
        owner_client.files.delete_file,
        owner_file_id,
    )
    if deleted:
        print(f"  deleted: {deleted}")

# ── Test 10: Deleted file returns 404 for owner ──────────────────────────────
print("\n--- Test 10: Deleted file returns 404 for owner (expecting 404) ---")
if owner_file_id:
    expect_error(
        "Test 10: Deleted file returns 404 for owner",
        (404,),
        owner_client.files.retrieve_file,
        owner_file_id,
    )

# ──────────────────────────────────────────────────────────────────────────────
# TEARDOWN
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("TEARDOWN")
print("═" * 60)

try:
    os.unlink(TMP_PATH)
    print(f"[OK] Temp file removed: {TMP_PATH}")
except Exception:
    print(f"[WARN] Could not remove temp file: {TMP_PATH}")

# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("FILE ISOLATION SWEEP — SUMMARY")
print("═" * 60)
for label, outcome in results.items():
    tag = "✅" if outcome == "PASS" else "❌"
    print(f"  {tag}  {label}: {outcome}")
print("═" * 60)
