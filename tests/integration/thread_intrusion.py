import os
import time

from dotenv import load_dotenv
from projectdavid import Entity

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:9000")

OWNER_KEY = "ea_Y4OIjjbHMluwjT0lcjGSRT-SsFjNt1oxi4YHcNp8vE4"
INTRUDER_KEY = "ea_T1CphyVjo2ahhnWrVsGyYh03tbguKac7gPc4Dz8C66k"

owner_client = Entity(base_url=BASE_URL, api_key=OWNER_KEY)
intruder_client = Entity(base_url=BASE_URL, api_key=INTRUDER_KEY)

results: dict = {}


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────


def expect_success(label: str, fn, *args, **kwargs):
    print(f"\n--- {label} (expecting success) ---")
    try:
        result = fn(*args, **kwargs)
        print(f"[PASS] ✅  {label}")
        return result
    except Exception as e:
        print(f"[FAIL] ❌  {label} raised an unexpected error: {e}")
        return None


def expect_403(label: str, fn, *args, **kwargs):
    print(f"\n--- {label} (expecting 403) ---")
    try:
        fn(*args, **kwargs)
        print(f"[FAIL] ❌  {label} succeeded — ownership guard may not be active.")
        results[label] = "FAIL"
    except Exception as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 403 or "403" in str(e) or "permission" in str(e).lower():
            print(f"[PASS] ✅  {label} correctly rejected with 403: {e}")
            results[label] = "PASS"
        else:
            print(f"[WARN] ⚠️  {label} was rejected, but with an unexpected error: {e}")
            results[label] = "WARN"


# ──────────────────────────────────────────────────────────────────────────────
# TEST 1 — Owner creates a thread (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
owner_thread = expect_success(
    "Test 1: Owner creates thread",
    owner_client.threads.create_thread,
)

if owner_thread:
    print(f"  thread.id       : {owner_thread.id}")
    print(f"  thread.owner_id : {getattr(owner_thread, 'owner_id', 'N/A')}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 2 — Owner retrieves their own thread (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
if owner_thread:
    retrieved = expect_success(
        "Test 2: Owner retrieves own thread",
        owner_client.threads.retrieve_thread,
        owner_thread.id,
    )
    if retrieved:
        print(f"  retrieved.id : {retrieved.id}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 3 — Owner updates their own thread metadata (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
if owner_thread:
    expect_success(
        "Test 3: Owner updates own thread metadata",
        owner_client.threads.update_thread_metadata,
        owner_thread.id,
        {"compliance_sweep": "threads", "test": True},
    )


# ──────────────────────────────────────────────────────────────────────────────
# TEST 4 — Intruder attempts to update owner's thread metadata (must 403)
# ──────────────────────────────────────────────────────────────────────────────
if owner_thread:
    expect_403(
        "Test 4: Intruder updates owner's thread metadata",
        intruder_client.threads.update_thread_metadata,
        owner_thread.id,
        {"injected": "malicious_value"},
    )


# ──────────────────────────────────────────────────────────────────────────────
# TEST 5 — Intruder attempts to delete owner's thread (must 403)
# ──────────────────────────────────────────────────────────────────────────────
if owner_thread:
    expect_403(
        "Test 5: Intruder deletes owner's thread",
        intruder_client.threads.delete_thread,
        owner_thread.id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# TEST 6 — Owner deletes their own thread (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
if owner_thread:
    deleted = expect_success(
        "Test 6: Owner deletes own thread",
        owner_client.threads.delete_thread,
        owner_thread.id,
    )
    if deleted:
        print(f"  deleted.id      : {deleted.id}")
        print(f"  deleted.deleted : {deleted.deleted}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 7 — Retrieve deleted thread (must 404)
# ──────────────────────────────────────────────────────────────────────────────
if owner_thread:
    print(f"\n--- Test 7: Retrieve deleted thread (expecting 404) ---")
    try:
        owner_client.threads.retrieve_thread(owner_thread.id)
        print("[FAIL] ❌  Test 7 succeeded — deleted thread still accessible.")
    except Exception as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 404 or "404" in str(e) or "not found" in str(e).lower():
            print(f"[PASS] ✅  Test 7 correctly returned 404: {e}")
        else:
            print(f"[WARN] ⚠️  Test 7 returned an unexpected error: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("THREAD ISOLATION SWEEP — SUMMARY")
print("═" * 60)
for label, outcome in results.items():
    icon = "✅" if outcome == "PASS" else "❌" if outcome == "FAIL" else "⚠️"
    print(f"  {icon}  {label}: {outcome}")
print("═" * 60)
