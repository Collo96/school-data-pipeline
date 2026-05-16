"""
run_pipeline.py
===============
Master runner – executes all pipeline phases in sequence:
  Phase 0 → Generate synthetic data (skip if you have real data)
  Phase 1 → Extract
  Phase 2 → Transform
  Phase 3 → Load

Usage:
    python run_pipeline.py           # runs all phases
    python run_pipeline.py --skip-generate   # skip data generation
"""

import argparse
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)


def run_phase(name: str, module_func) -> float:
    log.info(f"\n{'='*55}")
    log.info(f"  STARTING: {name}")
    log.info(f"{'='*55}")
    t0 = time.time()
    try:
        module_func()
    except Exception as e:
        log.error(f"Phase '{name}' FAILED: {e}")
        sys.exit(1)
    elapsed = time.time() - t0
    log.info(f"  DONE: {name} ({elapsed:.1f}s)")
    return elapsed


def main():
    parser = argparse.ArgumentParser(description="KCSE Data Pipeline")
    parser.add_argument("--skip-generate", action="store_true",
                        help="Skip synthetic data generation (use if you have real data)")
    args = parser.parse_args()

    times = {}

    if not args.skip_generate:
        import importlib.util, sys as _sys
        # Dynamically import and run each module
        from importlib import import_module

    # Run phases
    if not args.skip_generate:
        import generate_data_runner
        times["Generate"] = run_phase("Generate Data",  _run_generate)

    times["Extract"]   = run_phase("Extract",          _run_extract)
    times["Transform"] = run_phase("Transform",         _run_transform)
    times["Load"]      = run_phase("Load",              _run_load)

    # Summary
    total = sum(times.values())
    log.info(f"\n{'='*55}")
    log.info("  PIPELINE COMPLETE ✓")
    log.info(f"{'='*55}")
    for phase, t in times.items():
        log.info(f"  {phase:<12}: {t:.1f}s")
    log.info(f"  {'TOTAL':<12}: {total:.1f}s")
    log.info("\nNext step: streamlit run 04_dashboard.py")


def _run_generate():
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("gen", "00_generate_data.py")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

def _run_extract():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ext", "01_extract.py")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()

def _run_transform():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tfm", "02_transform.py")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()

def _run_load():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ld", "03_load.py")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()


if __name__ == "__main__":
    main()
