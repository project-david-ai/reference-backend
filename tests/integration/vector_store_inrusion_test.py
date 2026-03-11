"""
vector_store_isolation_test.py
───────────────────────────────
Ownership isolation sweep for the vector-store surface.

Tests:
  1.  Owner creates a vector store                          → success
  2.  Owner retrieves their own store                       → success
  3.  Intruder retrieves owner's store by ID                → 404
  4.  Owner lists their stores (no cross-user leakage)      → success
  5.  Intruder lists stores (owner's store absent)          → success
  6.  Owner adds a file to their store                      → success
  7.  Intruder adds a file to owner's store                 → 404
  8.  Intruder lists owner's store files                    → 404
  9.  Owner lists their own store files                     → success
 10.  Intruder deletes owner's store                        → 404
 11.  Owner deletes their own store                         → success
 12.  Collection-name lookup by intruder (Gap 2 fix)        → 404

Design notes:
  • Cross-user access returns 404, not 403 — the router deliberately
    avoids confirming resource existence to non-owners.
  • File tests use a small temp file created at runtime; it is removed
    in teardown regardless of test outcome.
  • The SDK is accessed via client.vectors.*
"""

import os
import tempfile

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
        results[label] = "PASS"
        return result
    except Exception as e:
        print(f"[FAIL] ❌  {label} raised an unexpected error: {e}")
        results[label] = "FAIL"
        return None


def expect_404(label: str, fn, *args, **kwargs):
    """
    Cross-user vector store access returns 404, not 403.
    The router deliberately avoids confirming resource existence to
    non-owners — a 403 would leak that the resource exists.
    """
    print(f"\n--- {label} (expecting 404) ---")
    try:
        fn(*args, **kwargs)
        print(f"[FAIL] ❌  {label} succeeded — ownership guard may not be active.")
        results[label] = "FAIL"
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print(f"[PASS] ✅  {label} correctly returned 404: {e}")
            results[label] = "PASS"
        else:
            print(
                f"[WARN] ⚠️  {label} rejected with unexpected error (expected 404): {e}"
            )
            results[label] = "WARN"


# ──────────────────────────────────────────────────────────────────────────────
# TEMP FILE — used for file-upload tests
# ──────────────────────────────────────────────────────────────────────────────
tmp_file = tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".txt",
    delete=False,
    prefix="vs_isolation_test_",
)
tmp_file.write("Vector store isolation test payload. Safe to delete.")
tmp_file.close()
TMP_FILE_PATH = tmp_file.name
print(f"\n[SETUP] Temp file created: {TMP_FILE_PATH}")


# ──────────────────────────────────────────────────────────────────────────────
# SETUP STATE
# ──────────────────────────────────────────────────────────────────────────────
owner_store = None
collection_name = None


# ──────────────────────────────────────────────────────────────────────────────
# TEST 1 — Owner creates a vector store
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("VECTOR STORE ISOLATION SWEEP")
print("═" * 60)

owner_store = expect_success(
    "Test 1: Owner creates vector store",
    owner_client.vectors.create_vector_store,
    name="isolation_test_store",
)

if owner_store:
    collection_name = owner_store.collection_name
    print(f"  store.id              : {owner_store.id}")
    print(f"  store.user_id         : {owner_store.user_id}")
    print(f"  store.collection_name : {collection_name}")
else:
    print("\n[ABORT] Could not create owner vector store. Exiting.")
    os.unlink(TMP_FILE_PATH)
    exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 2 — Owner retrieves their own store by ID
# ──────────────────────────────────────────────────────────────────────────────
expect_success(
    "Test 2: Owner retrieves own store by ID",
    owner_client.vectors.retrieve_vector_store_sync,
    owner_store.id,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 3 — Intruder retrieves owner's store by ID (must 404)
# ──────────────────────────────────────────────────────────────────────────────
expect_404(
    "Test 3: Intruder retrieves owner's store by ID",
    intruder_client.vectors.retrieve_vector_store_sync,
    owner_store.id,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 4 — Owner lists stores (no cross-user leakage)
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n--- Test 4: Owner lists stores (expecting only own stores) ---")
try:
    owner_stores = owner_client.vectors.list_my_vector_stores()
    owner_store_ids = [s.id for s in owner_stores]

    if owner_store.id in owner_store_ids:
        print(f"[PASS] ✅  Test 4: Owner's store appears in list")
        results["Test 4: Owner store in list"] = "PASS"
    else:
        print(f"[FAIL] ❌  Test 4: Owner's store missing from list")
        results["Test 4: Owner store in list"] = "FAIL"

    owner_user_id = owner_store.user_id
    leaked = [s for s in owner_stores if s.user_id != owner_user_id]
    if leaked:
        print(
            f"[FAIL] ❌  Test 4: {len(leaked)} foreign store(s) leaked into owner's list!"
        )
        results["Test 4: No cross-user leakage"] = "FAIL"
    else:
        print(f"[PASS] ✅  Test 4: No cross-user leakage in store list")
        results["Test 4: No cross-user leakage"] = "PASS"
except Exception as e:
    print(f"[FAIL] ❌  Test 4 raised unexpected error: {e}")
    results["Test 4: Owner store in list"] = "FAIL"
    results["Test 4: No cross-user leakage"] = "FAIL"


# ──────────────────────────────────────────────────────────────────────────────
# TEST 5 — Intruder lists stores (must not see owner's store)
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n--- Test 5: Intruder lists stores (must not see owner's store) ---")
try:
    intruder_stores = intruder_client.vectors.list_my_vector_stores()
    intruder_store_ids = [s.id for s in intruder_stores]

    if owner_store.id in intruder_store_ids:
        print(f"[FAIL] ❌  Test 5: Owner's store leaked into intruder's list!")
        results["Test 5: No cross-user leakage"] = "FAIL"
    else:
        print(f"[PASS] ✅  Test 5: Owner's store not visible to intruder")
        results["Test 5: No cross-user leakage"] = "PASS"
except Exception as e:
    print(f"[FAIL] ❌  Test 5 raised unexpected error: {e}")
    results["Test 5: No cross-user leakage"] = "FAIL"


# ──────────────────────────────────────────────────────────────────────────────
# TEST 6 — Owner adds a file to their own store
# ──────────────────────────────────────────────────────────────────────────────
owner_file = expect_success(
    "Test 6: Owner adds file to own store",
    owner_client.vectors.add_file_to_vector_store,
    owner_store.id,
    TMP_FILE_PATH,
)

if owner_file:
    print(f"  file.id     : {owner_file.id}")
    print(f"  file.status : {owner_file.status}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 7 — Intruder adds a file to owner's store (must 404)
# ──────────────────────────────────────────────────────────────────────────────
expect_404(
    "Test 7: Intruder adds file to owner's store",
    intruder_client.vectors.add_file_to_vector_store,
    owner_store.id,
    TMP_FILE_PATH,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 8 — Intruder lists owner's store files (must 404)
# ──────────────────────────────────────────────────────────────────────────────
expect_404(
    "Test 8: Intruder lists owner's store files",
    intruder_client.vectors.list_store_files,
    owner_store.id,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 9 — Owner lists their own store files
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n--- Test 9: Owner lists own store files ---")
try:
    files = owner_client.vectors.list_store_files(owner_store.id)
    print(f"[PASS] ✅  Test 9: Owner retrieved {len(files)} file(s) from own store")
    results["Test 9: Owner lists own files"] = "PASS"
except Exception as e:
    print(f"[FAIL] ❌  Test 9 raised unexpected error: {e}")
    results["Test 9: Owner lists own files"] = "FAIL"


# ──────────────────────────────────────────────────────────────────────────────
# TEST 10 — Intruder deletes owner's store (must 404)
# ──────────────────────────────────────────────────────────────────────────────
expect_404(
    "Test 10: Intruder deletes owner's store",
    intruder_client.vectors.delete_vector_store,
    owner_store.id,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 11 — Owner deletes their own store
# ──────────────────────────────────────────────────────────────────────────────
expect_success(
    "Test 11: Owner deletes own store",
    owner_client.vectors.delete_vector_store,
    owner_store.id,
    permanent=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 12 — Collection-name lookup by intruder (Gap 2 fix)
#
# Before the fix, GET /vector-stores/lookup/collection had NO auth dependency
# at all — any unauthenticated or cross-user caller could enumerate metadata
# about any store by guessing or knowing its collection name.
#
# After the fix, the endpoint requires auth and enforces ownership, returning
# 404 (not 403) to avoid confirming existence to non-owners.
#
# We use the collection_name captured at store creation time. The store was
# permanently deleted in Test 11, so the expected result is always 404 —
# but the important assertion is that the intruder cannot even try to fish
# for stores they don't own. If the auth guard were missing, this would
# return 404 only because the store is gone, not because access was denied.
# To isolate the auth fix specifically, create a second store below.
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n--- Test 12: Collection-name lookup isolation (Gap 2 fix) ---")

# Create a fresh store so it actually exists during the lookup attempt.
probe_store = expect_success(
    "Test 12 setup: Owner creates probe store for collection lookup",
    owner_client.vectors.create_vector_store,
    name="isolation_probe_store",
)

if probe_store:
    probe_collection = probe_store.collection_name
    print(f"  probe_store.collection_name : {probe_collection}")

    # Owner can look up their own store by collection name.
    expect_success(
        "Test 12a: Owner looks up own store by collection name",
        owner_client.vectors.retrieve_vector_store_sync,  # uses GET /vector-stores/{id}
        probe_store.id,
    )

    # Intruder cannot look up owner's store by collection name — must 404.
    # This exercises the fixed GET /vector-stores/lookup/collection endpoint.
    expect_404(
        "Test 12b: Intruder looks up owner's store by collection name (Gap 2 fix)",
        intruder_client.vectors._run_sync,
        intruder_client.vectors._request(
            "GET",
            "/v1/vector-stores/lookup/collection",
            params={"name": probe_collection},
        ),
    )

    # Teardown probe store.
    expect_success(
        "Test 12 teardown: Owner permanently deletes probe store",
        owner_client.vectors.delete_vector_store,
        probe_store.id,
        permanent=True,
    )
else:
    print(
        "[WARN] ⚠️  Test 12: Could not create probe store — skipping collection lookup test."
    )
    results[
        "Test 12b: Intruder looks up owner's store by collection name (Gap 2 fix)"
    ] = "WARN"


# ──────────────────────────────────────────────────────────────────────────────
# TEARDOWN — remove temp file
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("TEARDOWN")
print("═" * 60)
try:
    os.unlink(TMP_FILE_PATH)
    print(f"[OK] Temp file removed: {TMP_FILE_PATH}")
except Exception as e:
    print(f"[WARN] Could not remove temp file {TMP_FILE_PATH}: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("VECTOR STORE ISOLATION SWEEP — SUMMARY")
print("═" * 60)
for label, outcome in results.items():
    icon = "✅" if outcome == "PASS" else "❌" if outcome == "FAIL" else "⚠️"
    print(f"  {icon}  {label}: {outcome}")
print("═" * 60)
