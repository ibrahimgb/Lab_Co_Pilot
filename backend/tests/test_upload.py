"""
Upload endpoint test — drop your ZIP / CSV / Excel files into:

    backend/tests/test_data/

Then run:
    cd backend
    .venv/bin/python tests/test_upload.py

It will upload every file in that folder to the running backend
(http://localhost:8000) and print the results.
"""

from __future__ import annotations

import os
import sys
import json
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
UPLOAD_ENDPOINT = f"{API_URL}/api/data/upload"
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
SUPPORTED_EXTENSIONS = {".csv", ".xls", ".xlsx", ".zip"}

SEPARATOR = "=" * 70


def upload_file(filepath: str) -> dict | None:
    """Upload a single file and return the JSON response."""
    filename = os.path.basename(filepath)
    print(f"\n{SEPARATOR}")
    print(f"📤  Uploading: {filename}  ({os.path.getsize(filepath)} bytes)")
    print(SEPARATOR)

    try:
        with open(filepath, "rb") as f:
            resp = requests.post(
                UPLOAD_ENDPOINT,
                files={"file": (filename, f)},
                timeout=30,
            )
    except requests.ConnectionError:
        print("❌  Cannot connect to the backend. Is the server running?")
        print(f"    Expected at: {API_URL}")
        return None

    print(f"Status: {resp.status_code}")

    if resp.status_code != 200:
        print(f"❌  Error: {resp.text}")
        return None

    data = resp.json()
    return data


def print_result(data: dict) -> None:
    """Pretty-print the upload response."""
    total = data.get("total_files", 0)
    ftype = data.get("file_type", "?")
    print(f"✅  Success — {total} file(s) loaded  [type: {ftype}]")

    for i, f in enumerate(data.get("files", []), 1):
        print(f"\n  ── File {i}: {f['filename']} ──")
        print(f"     ID:      {f['file_id']}")
        print(f"     Rows:    {f['row_count']}")
        print(f"     Columns: {len(f['columns'])}")

        # Column details
        for col in f.get("column_info", []):
            line = f"       • {col['name']:20s}  dtype={col['dtype']:10s}  "
            line += f"unique={col['unique_count']}  nulls={col['null_count']}"
            mn, mx, avg = col.get("min"), col.get("max"), col.get("mean")
            if mn is not None or mx is not None or avg is not None:
                mn_s = f"{mn}" if mn is not None else "N/A"
                mx_s = f"{mx}" if mx is not None else "N/A"
                avg_s = f"{avg:.4f}" if avg is not None else "N/A"
                line += f"  min={mn_s}  max={mx_s}  mean={avg_s}"
            print(line)

        # Preview
        preview = f.get("preview", [])
        if preview:
            print(f"\n     Preview (first {len(preview)} rows):")
            cols = f["columns"]
            # Header
            header = "     | " + " | ".join(f"{c:>15s}" for c in cols) + " |"
            print(header)
            print("     |" + "-" * (len(header) - 6) + "|")
            for row in preview:
                vals = " | ".join(f"{str(row.get(c, '')):>15s}" for c in cols)
                print(f"     | {vals} |")


def generate_sample_zip() -> str:
    """Create a small sample ZIP with 2 CSVs for quick testing."""
    import csv
    import zipfile
    import io

    out_path = os.path.join(TEST_DATA_DIR, "_sample_generated.zip")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # CSV 1
        csv1 = io.StringIO()
        w = csv.writer(csv1)
        w.writerow(["Gene", "Expression", "P_Value", "Significant"])
        w.writerow(["BRCA1", 2.45, 0.001, "yes"])
        w.writerow(["TP53", 1.10, 0.05, "no"])
        w.writerow(["MYC", 3.67, 0.0001, "yes"])
        w.writerow(["EGFR", "", 0.8, "no"])
        zf.writestr("gene_expression.csv", csv1.getvalue())

        # CSV 2
        csv2 = io.StringIO()
        w = csv.writer(csv2)
        w.writerow(["SampleID", "Concentration", "Temperature", "Replicate"])
        w.writerow(["S001", 0.5, 37.0, 1])
        w.writerow(["S002", 1.2, 37.0, 2])
        w.writerow(["S003", 0.8, 25.0, 1])
        zf.writestr("measurements.csv", csv2.getvalue())

    with open(out_path, "wb") as f:
        f.write(buf.getvalue())

    return out_path


def main() -> None:
    print("\n🔬  Lab Co-Pilot — Upload Test Runner")
    print(f"    Backend: {API_URL}")
    print(f"    Test data folder: {os.path.abspath(TEST_DATA_DIR)}\n")

    # Check connectivity first
    try:
        r = requests.get(API_URL, timeout=5)
        print(f"    Server status: {'🟢 Online' if r.ok else '🔴 Error'}")
    except requests.ConnectionError:
        print("    Server status: 🔴 Offline — start the backend first:")
        print("        cd backend && .venv/bin/uvicorn main:app --reload --port 8000")
        sys.exit(1)

    # Collect test files
    files = []
    if os.path.isdir(TEST_DATA_DIR):
        for name in sorted(os.listdir(TEST_DATA_DIR)):
            ext = os.path.splitext(name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                files.append(os.path.join(TEST_DATA_DIR, name))

    if not files:
        print("\n⚠️  No test files found. Generating a sample ZIP…")
        sample = generate_sample_zip()
        files.append(sample)
        print(f"    Created: {sample}")

    print(f"\n    Found {len(files)} test file(s):")
    for f in files:
        print(f"      - {os.path.basename(f)}")

    # Upload each file
    passed = 0
    failed = 0
    for filepath in files:
        data = upload_file(filepath)
        if data:
            print_result(data)
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{SEPARATOR}")
    print(f"📊  Results: {passed} passed, {failed} failed, {len(files)} total")
    print(SEPARATOR)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
