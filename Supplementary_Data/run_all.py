"""
Master script to run all simulations for the revised paper.
Usage: python run_all.py [--s1] [--s2] [--s2-ext] [--s2-adaptive] [--s3] [--s4] [--all]

Default: runs all simulations in sequence.
"""

import argparse, sys, os, time, subprocess

# Parse arguments
parser = argparse.ArgumentParser(description="Run all steganography simulations")
parser.add_argument("--s1", action="store_true", help="Run S1: Geodesics")
parser.add_argument("--s2", action="store_true", help="Run S2: NG vs Euclidean (diagonal)")
parser.add_argument("--s2-ext", action="store_true", help="Run S2-EXT: NG on non-diagonal FIM")
parser.add_argument("--s2-adaptive", action="store_true", help="Run S2-ADAPTIVE: vs Adam/RMSprop")
parser.add_argument("--s3", action="store_true", help="Run S3: Curvature map (revised)")
parser.add_argument("--s4", action="store_true", help="Run S4: Path comparison (revised)")
parser.add_argument("--all", action="store_true", help="Run all simulations")
args = parser.parse_args()

# If no flags given, run all
if not any([args.s1, args.s2, args.s2_ext, args.s2_adaptive, args.s3, args.s4, args.all]):
    args.all = True

run_all = args.all
scripts = []

if run_all or args.s1:
    scripts.append(("S1: Geodesics", "sim_s1_geodesics.py"))
if run_all or args.s2:
    scripts.append(("S2: NG vs Euclidean (diagonal)", "sim_s2_gradient.py"))
if run_all or args.s2_ext:
    scripts.append(("S2-EXT: NG on non-diagonal FIM", "sim_s2_nondiagonal.py"))
if run_all or args.s2_adaptive:
    scripts.append(("S2-ADAPTIVE: vs Adam/RMSprop", "sim_s2_adaptive_comparison.py"))
if run_all or args.s3:
    scripts.append(("S3: Curvature map (revised)", "sim_s3_curvature.py"))
if run_all or args.s4:
    scripts.append(("S4: Path comparison (revised)", "sim_s4_path_comparison.py"))

code_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("Running simulations for: Information Geometry for Steganographic Embedding")
print("Revised version (post-audit)")
print("=" * 70)
print(f"Code directory: {code_dir}")
print(f"Simulations to run: {len(scripts)}")
print()

total_start = time.time()

for name, script in scripts:
    script_path = os.path.join(code_dir, script)
    if not os.path.exists(script_path):
        print(f"  WARNING: {script} not found, skipping.")
        continue

    print(f"\n{'='*70}")
    print(f"  Starting: {name}")
    print(f"  Script:   {script}")
    print(f"{'='*70}")

    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=code_dir,
            capture_output=False,
            text=True,
            timeout=1800  # 30 min timeout per simulation
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            print(f"  COMPLETED in {elapsed:.1f}s")
        else:
            print(f"  FAILED (exit code {result.returncode}) after {elapsed:.1f}s")
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after 30 minutes")
    except Exception as e:
        print(f"  ERROR: {e}")

total_elapsed = time.time() - total_start
print(f"\n{'='*70}")
print(f"All simulations completed in {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
print(f"Output files:")
print(f"  Data:    {os.path.join(code_dir, '..', 'data')}")
print(f"  Figures: {os.path.join(code_dir, '..', 'figures')}")
print(f"{'='*70}")
