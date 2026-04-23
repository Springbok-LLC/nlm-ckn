#!/usr/bin/env python3
"""Generate release config files and a data zip for a cell-kn release.

Inputs
------
--run-name      Release name used in all output filenames, e.g. "2026-04".

--include PATH  Results directory to include, relative to data/.
                Repeat for each dataset directory.
                Omit to auto-discover every directory under data/prod/ that
                contains a *_results.csv file.

--dry-run       Print the generated JSON to stdout without writing any files.

Files generated
---------------
data/prod/release/run-<run-name>.json
    Top-level run config consumed by the ETL pipeline. Contains the path to
    results-sources-<run-name>.json and the HuBMAP URLs read from
    scripts/release/hubmap_urls.txt.

data/prod/release/results-sources-<run-name>.json
    Array of per-dataset entries, each with a results_dir and the file-pattern
    fields (nsforest_pattern, harvester_pattern, mapping_substrs, etc.) used
    by the downstream harvester to locate specific output files.

data/prod/release/release-<run-name>.zip
    Flat archive of the ETL-facing data files collected from every included
    results directory (see ZIP_PATTERNS), plus hubmap_urls.txt (one URL per
    line). Files are stored at the top level of the zip; if two datasets
    produce a file with the same name the results-directory name is prepended
    to disambiguate.

Usage
-----
    python scripts/release/generate_release.py \\
        --run-name 2026-04 \\
        --include prod/bone_marrow/sc-nsforest-qc-nf/69b43b8be91505a60aa45010/results/bone_marrow-Dominguez_Conde-2022 \\
        --include prod/kidney/sc-nsforest-qc-nf/a3f91c2d.../results/kidney-Author-2023
"""

import argparse
import json
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).parents[2] / "data"
RELEASE_DIR = DATA_DIR / "prod" / "release"
HUBMAP_URLS_FILE = Path(__file__).parent / "hubmap_urls.txt"

# Files the ETL repo expects to find in each results directory.
# *_mapping.csv is currently absent from cell-kn/data/prod but included for completeness.
ZIP_PATTERNS = [
    "*_harvester_final.csv",
    "*_results.csv",
    "*_mapping.csv",
    "*_silhouette_fscore_summary.csv",
    "*_master_dataset_summary.csv",
]

# File patterns consumed by the ETL (nlm-ckn-etl/data/results-sources-full.json).
DEFAULT_PATTERNS = {
    "harvester_pattern": "*_harvester_final.csv",
    "nsforest_pattern": "*_results.csv",
    "mapping_substrs": ["_results.csv", "_mapping.csv"],
    "scores_substrs": ["_results.csv", "_silhouette_fscore_summary.csv"],
    "summary_substrs": ["_results.csv", "_*_master_dataset_summary.csv"],
}


def discover_results_dirs(data_dir: Path) -> list[str]:
    """Find all results directories under data/prod/ that contain
    NSForest results files (*_results.csv). Returns paths relative to data/."""
    found = []
    for csv in sorted(data_dir.rglob("*_results.csv")):
        rel = csv.parent.relative_to(data_dir)
        if str(rel) not in found:
            found.append(str(rel))
    return found


def _collect_manifest_files(results_sources: list[dict]) -> list[Path]:
    """Return files matching ZIP_PATTERNS from each results_dir."""
    collected: list[Path] = []
    for entry in results_sources:
        results_dir = DATA_DIR / entry["results_dir"]
        for pattern in ZIP_PATTERNS:
            collected.extend(sorted(results_dir.glob(pattern)))
    return collected


def build_release_zip(
    run_name: str,
    results_sources: list[dict],
    hubmap_urls: list[str],
) -> Path:
    """Create a zip of manifest files in a flat structure plus hubmap_urls.txt."""
    zip_path = RELEASE_DIR / f"release-{run_name}.zip"
    seen_names: dict[str, Path] = {}

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src in _collect_manifest_files(results_sources):
            name = src.name
            if name in seen_names and seen_names[name] != src:
                # Prefix with the immediate results-dir basename to resolve collision
                name = f"{src.parent.name}__{name}"
            seen_names[name] = src
            zf.write(src, arcname=name)

        zf.writestr(
            "hubmap_urls.txt", "\n".join(hubmap_urls) + ("\n" if hubmap_urls else "")
        )

    return zip_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-name", required=True, help="Release name, e.g. 2026-04")
    parser.add_argument(
        "--include",
        action="append",
        dest="results_dirs",
        metavar="PATH",
        help="results_dir to include (relative to data/). "
        "Repeat for each directory. "
        "Omit to auto-discover all NSForest results dirs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated JSON without writing files.",
    )
    args = parser.parse_args()

    hubmap_urls = [
        line for line in HUBMAP_URLS_FILE.read_text().splitlines() if line.strip()
    ]

    results_dirs = args.results_dirs or discover_results_dirs(DATA_DIR)

    if not results_dirs:
        raise SystemExit("No NSForest results directories found or specified.")

    # Validate each path exists
    missing = [d for d in results_dirs if not (DATA_DIR / d).is_dir()]
    if missing:
        raise SystemExit(
            "Results directories not found:\n"
            + "\n".join(f"  data/{d}" for d in missing)
        )

    results_sources_filename = f"prod/release/results-sources-{args.run_name}.json"

    run_config = {
        "results_sources": results_sources_filename,
        "hubmap_urls": hubmap_urls,
    }

    results_sources = [{"results_dir": d, **DEFAULT_PATTERNS} for d in results_dirs]

    if args.dry_run:
        print("=== run config ===")
        print(json.dumps(run_config, indent=2))
        print("\n=== results sources ===")
        print(json.dumps(results_sources, indent=2))
        return

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    run_config_path = RELEASE_DIR / f"run-{args.run_name}.json"
    run_config_path.write_text(json.dumps(run_config, indent=2) + "\n")
    print(f"Written: {run_config_path.relative_to(DATA_DIR.parent)}")

    sources_path = RELEASE_DIR / f"results-sources-{args.run_name}.json"
    sources_path.write_text(json.dumps(results_sources, indent=2) + "\n")
    print(f"Written: {sources_path.relative_to(DATA_DIR.parent)}")

    zip_path = build_release_zip(args.run_name, results_sources, hubmap_urls)
    print(f"Written: {zip_path.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
