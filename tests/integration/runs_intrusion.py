import os

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
            print(f"[WARN] ⚠️  {label} rejected with unexpected error: {e}")
            results[label] = "WARN"


def expect_404(label: str, fn, *args, **kwargs):
    print(f"\n--- {label} (expecting 404) ---")
    try:
        fn(*args, **kwargs)
        print(f"[FAIL] ❌  {label} succeeded — resource should not exist.")
        results[label] = "FAIL"
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print(f"[PASS] ✅  {label} correctly returned 404: {e}")
            results[label] = "PASS"
        else:
            print(f"[WARN] ⚠️  {label} rejected with unexpected error: {e}")
            results[label] = "WARN"


# ──────────────────────────────────────────────────────────────────────────────
# SETUP — owner creates the shared fixtures
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("SETUP — creating owner fixtures")
print("═" * 60)

owner_assistant = expect_success(
    "Setup: Owner creates assistant",
    owner_client.assistants.create_assistant,
    name="Run Isolation Test Assistant",
    model="gpt-4",
    instructions="You are a test assistant.",
)

owner_thread = expect_success(
    "Setup: Owner creates thread",
    owner_client.threads.create_thread,
)

if not owner_assistant or not owner_thread:
    print("\n[ABORT] Fixtures could not be created. Exiting.")
    exit(1)

print(f"  assistant.id : {owner_assistant.id}")
print(f"  thread.id    : {owner_thread.id}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 1 — Owner creates a run (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
owner_run = expect_success(
    "Test 1: Owner creates run",
    owner_client.runs.create_run,
    thread_id=owner_thread.id,
    assistant_id=owner_assistant.id,
)

if owner_run:
    print(f"  run.id      : {owner_run.id}")
    print(f"  run.user_id : {owner_run.user_id}")
    print(f"  run.status  : {owner_run.status}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 2 — Intruder attempts to create a run against owner's assistant (must 403)
# ──────────────────────────────────────────────────────────────────────────────
expect_403(
    "Test 2: Intruder creates run against owner's assistant",
    intruder_client.runs.create_run,
    thread_id=owner_thread.id,
    assistant_id=owner_assistant.id,
)


# ──────────────────────────────────────────────────────────────────────────────
# TEST 3 — Owner retrieves their own run (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
if owner_run:
    retrieved = expect_success(
        "Test 3: Owner retrieves own run",
        owner_client.runs.retrieve_run,
        owner_run.id,
    )
    if retrieved:
        print(f"  retrieved.id      : {retrieved.id}")
        print(f"  retrieved.user_id : {retrieved.user_id}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 4 — Intruder attempts to retrieve owner's run (must 403)
# ──────────────────────────────────────────────────────────────────────────────
if owner_run:
    expect_403(
        "Test 4: Intruder retrieves owner's run",
        intruder_client.runs.retrieve_run,
        owner_run.id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# TEST 5 — Intruder attempts to cancel owner's run (must 403)
# ──────────────────────────────────────────────────────────────────────────────
if owner_run:
    expect_403(
        "Test 5: Intruder cancels owner's run",
        intruder_client.runs.cancel_run,
        owner_run.id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# TEST 6 — Owner cancels their own run (must succeed)
# ──────────────────────────────────────────────────────────────────────────────
if owner_run:
    cancelled = expect_success(
        "Test 6: Owner cancels own run",
        owner_client.runs.cancel_run,
        owner_run.id,
    )
    if cancelled:
        # SDK may return a dict or a Pydantic model depending on version
        cancelled_id = (
            cancelled.get("id") if isinstance(cancelled, dict) else cancelled.id
        )
        cancelled_status = (
            cancelled.get("status") if isinstance(cancelled, dict) else cancelled.status
        )
        print(f"  cancelled.id     : {cancelled_id}")
        print(f"  cancelled.status : {cancelled_status}")


# ──────────────────────────────────────────────────────────────────────────────
# TEST 7 — Owner lists runs (must succeed, intruder's runs must not appear)
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n--- Test 7: Owner lists runs (expecting only own runs) ---")
try:
    run_list = owner_client.runs.list_all_runs()  # ← was list_runs()
    run_ids = [r.id for r in run_list.data]
    if owner_run and owner_run.id in run_ids:
        print(f"[PASS] ✅  Test 7: Owner's run appears in list")
        results["Test 7: Owner run in list"] = "PASS"
    else:
        print(
            f"[WARN] ⚠️  Test 7: Owner's run not found in list (may have been cancelled)"
        )
        results["Test 7: Owner run in list"] = "WARN"

    owner_user_id = owner_run.user_id if owner_run else None
    if owner_user_id:
        leaked = [r for r in run_list.data if r.user_id != owner_user_id]
        if leaked:
            print(f"[FAIL] ❌  Test 7: {len(leaked)} foreign run(s) leaked into list!")
            results["Test 7: No cross-user leakage"] = "FAIL"
        else:
            print(f"[PASS] ✅  Test 7: No cross-user leakage in run list")
            results["Test 7: No cross-user leakage"] = "PASS"
except Exception as e:
    print(f"[FAIL] ❌  Test 7 raised unexpected error: {e}")
    results["Test 7: Owner run in list"] = "FAIL"


# ──────────────────────────────────────────────────────────────────────────────
# TEST 8 — Intruder lists runs (must not see owner's run)
# ──────────────────────────────────────────────────────────────────────────────
print(f"\n--- Test 8: Intruder lists runs (must not see owner's run) ---")
try:
    intruder_list = intruder_client.runs.list_all_runs()  # ← was list_runs()
    intruder_run_ids = [r.id for r in intruder_list.data]
    if owner_run and owner_run.id in intruder_run_ids:
        print(f"[FAIL] ❌  Test 8: Owner's run leaked into intruder's list!")
        results["Test 8: No cross-user leakage"] = "FAIL"
    else:
        print(f"[PASS] ✅  Test 8: Owner's run not visible to intruder")
        results["Test 8: No cross-user leakage"] = "PASS"
except Exception as e:
    print(f"[FAIL] ❌  Test 8 raised unexpected error: {e}")
    results["Test 8: No cross-user leakage"] = "FAIL"


# ──────────────────────────────────────────────────────────────────────────────
# TEARDOWN — clean up fixtures
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("TEARDOWN")
print("═" * 60)

if owner_thread:
    expect_success(
        "Teardown: Delete owner thread",
        owner_client.threads.delete_thread,
        owner_thread.id,
    )

if owner_assistant:
    expect_success(
        "Teardown: Delete owner assistant",
        owner_client.assistants.delete_assistant,
        owner_assistant.id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "═" * 60)
print("RUN ISOLATION SWEEP — SUMMARY")
print("═" * 60)
for label, outcome in results.items():
    icon = "✅" if outcome == "PASS" else "❌" if outcome == "FAIL" else "⚠️"
    print(f"  {icon}  {label}: {outcome}")
print("═" * 60)
