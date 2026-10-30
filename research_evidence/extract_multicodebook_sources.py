"""Extract audited R2.7/R2.3 evidence without network access.
The large experiment sources and result files are stored as byte-exact gzip
files so their Git-object hashes can be independently verified.
"""
from pathlib import Path
import gzip
FOLDER=Path(__file__).resolve().parent
ITEMS={
  "run_multicodebook_20261031.py.gz":"run_multicodebook.py",
  "r27_algorithm2_direct_v1.py.gz":"r27_algorithm2_direct_v1.py",
  "audit_multicodebook_20261031.py.gz":"audit_multicodebook.py",
  "multicodebook_results_20261031.json.gz":"multicodebook_results.json",
  "multicodebook_detectors_20261031.csv.gz":"multicodebook_detectors.csv",
  "multicodebook_decode_20261031.csv.gz":"multicodebook_decode.csv"
}
for compressed, output in ITEMS.items():
    src=FOLDER/compressed
    if not src.exists():
        raise FileNotFoundError(src)
    dst=FOLDER/output
    dst.write_bytes(gzip.decompress(src.read_bytes()))
    print(f"Extracted {dst.name} ({dst.stat().st_size} bytes)")
