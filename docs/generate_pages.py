#!/usr/bin/env python3
"""
Generate Sphinx RST pages from cell-kn master_dataset_summary.csv files.

This script:
1. Finds all master_dataset_summary.csv files under data/prod/
2. Groups datasets by tissue/organ
3. Generates per-tissue RST pages with summary tables and reference forms
4. Generates the index.rst landing page
5. Copies silhouette_fscore_summary.html reports to _static/reports/

Usage:
    python docs/generate_pages.py
"""

import csv
import glob
import os
from pathlib import Path

# Paths relative to repo root
GITHUB_RAW = "https://raw.githubusercontent.com/NIH-NLM/cell-kn/main"
GITHUB_PREVIEW = "https://htmlpreview.github.io/?https://github.com/NIH-NLM/cell-kn/blob/main"

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data" / "prod"
DOCS_DIR = REPO_ROOT / "docs"
TISSUES_DIR = DOCS_DIR / "tissues"

# Columns to extract from CSV
COLUMNS = [
    "collection_name",
    "collection_url",
    "dataset_title",
    "explorer_url",
    "first_author",
    "year",
    "n_clusters",
    "n_cells",
    "median_silhouette",
    "mean_silhouette",
    "median_fscore",
    "mean_fscore",
    "organ",
    "dataset",
]


def find_master_csvs():
    """Find all master_dataset_summary.csv files."""
    pattern = str(DATA_DIR / "**" / "*master_dataset_summary.csv")
    return sorted(glob.glob(pattern, recursive=True))

def find_all_viz_files(csv_path):
    """Find all HTML and SVG files in the same directory as the CSV."""
    csv_dir = os.path.dirname(csv_path)
    htmls = glob.glob(os.path.join(csv_dir, "*.html"))
    svgs = glob.glob(os.path.join(csv_dir, "*.svg"))
    return sorted(htmls + svgs)

def github_url(filepath):
    """Build a GitHub URL for a file in the repo."""
    rel = os.path.relpath(filepath, REPO_ROOT)
    if filepath.endswith('.html'):
        return f"{GITHUB_PREVIEW}/{rel}"
    return f"{GITHUB_RAW}/{rel}"


def read_csv_row(csv_path):
    """Read the first data row from a master_dataset_summary.csv."""
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return row
    return None


def format_number(val):
    """Format a number string nicely."""
    try:
        num = float(val)
        if num == int(num) and num > 1:
            return f"{int(num):,}"
        return f"{num:.4f}"
    except (ValueError, TypeError):
        return str(val)


def get_tissue_label(tissue_name):
    """Convert tissue directory name to a display label."""
    return tissue_name.replace("_", " ").title()


def generate_tissue_rst(tissue, datasets):
    """Generate RST content for a single tissue page."""
    label = get_tissue_label(tissue)
    lines = []

    # Title
    lines.append("=" * len(label))
    lines.append(label)
    lines.append("=" * len(label))
    lines.append("")
    lines.append(f"Datasets analyzed for **{label}**: {len(datasets)} total.")
    lines.append("")

    # --- Dataset Summary Table ---
    lines.append("Dataset Summary")
    lines.append("-" * len("Dataset Summary"))
    lines.append("")
    lines.append(".. raw:: html")
    lines.append("")
    lines.append("   <div class=\"table-wrapper\">")
    lines.append("   <table class=\"dataset-summary\">")
    lines.append("   <thead>")
    lines.append("   <tr>")
    lines.append("     <th>Dataset</th>")
    lines.append("     <th>Collection</th>")
    lines.append("     <th>Dataset Title</th>")
    lines.append("     <th>Explorer</th>")
    lines.append("     <th>Cells</th>")
    lines.append("     <th>Clusters</th>")
    lines.append("     <th>Med. Silhouette</th>")
    lines.append("     <th>Mean Silhouette</th>")
    lines.append("     <th>Med. F-score</th>")
    lines.append("     <th>Mean F-score</th>")
    lines.append("     <th>Report</th>")
    lines.append("   </tr>")
    lines.append("   </thead>")
    lines.append("   <tbody>")

    for ds in datasets:
        author = ds.get("first_author", "Unknown")
        year = ds.get("year", "")
        journal = ds.get("journal", "")
        dataset_label = f"{author} ({journal}) {year}" if journal else f"{author} {year}"
        collection_url = ds.get("collection_url", "#")
        dataset_title = ds.get("dataset_title", "")
        dt_display = dataset_title[:50] + "..." if len(dataset_title) > 50 else dataset_title
        explorer_url = ds.get("explorer_url", "#")
        collection_name = ds.get("collection_name", "")
        n_cells = format_number(ds.get("n_cells", ""))
        n_clusters = format_number(ds.get("n_clusters", ""))
        med_sil = format_number(ds.get("median_silhouette", ""))
        mean_sil = format_number(ds.get("mean_silhouette", ""))
        med_f = format_number(ds.get("median_fscore", ""))
        mean_f = format_number(ds.get("mean_fscore", ""))

        # Report link
        report_link = ""
        if ds.get("_report_url"):
            report_link = f'<a href="{ds["_report_url"]}" target="_blank">View Report</a>'

        # Truncate collection name for display
        coll_display = collection_name[:50] + "..." if len(collection_name) > 50 else collection_name

        lines.append("   <tr>")
        lines.append(f'     <td><strong>{dataset_label}</strong></td>')
        lines.append(f'     <td><a href="{collection_url}" target="_blank" title="{collection_name}">{coll_display}</a></td>')
        lines.append(f'     <td title="{dataset_title}">{dt_display}</td>')
        lines.append(f'     <td><a href="{explorer_url}" target="_blank">Explore</a></td>')
        lines.append(f"     <td>{n_cells}</td>")
        lines.append(f"     <td>{n_clusters}</td>")
        lines.append(f"     <td>{med_sil}</td>")
        lines.append(f"     <td>{mean_sil}</td>")
        lines.append(f"     <td>{med_f}</td>")
        lines.append(f"     <td>{mean_f}</td>")
        lines.append(f"     <td>{report_link}</td>")
        lines.append("   </tr>")

    lines.append("   </tbody>")
    lines.append("   </table>")
    lines.append("   </div>")
    lines.append("")

    # --- Per Dataset Visualizations ---
    lines.append("Visualizations")
    lines.append("-" * len("Visualizations"))
    lines.append("")
    lines.append(".. raw:: html")
    lines.append("")
    for ds in datasets:
        author = ds.get("first_author", "Unknown")
        journal = ds.get("journal", "")
        year = ds.get("year", "")
        dt = ds.get("dataset_title", "")
        label = f"{author} ({journal}) {year} - {dt}" if journal else f"{author} {year} - {dt}"

        viz_files = ds.get("_viz_files", {})
        if not viz_files:
            continue

        lines.append(f'   <details><summary><strong>{label}</strong></summary>')
        lines.append('   <div class="viz-links">')

        # Group by category
        categories = {
            "Quality Boxplots": [f for f in viz_files if "boxplot_" in os.path.basename(f)],
            "Scatter Plots": [f for f in viz_files if "scatter_" in os.path.basename(f)],
            "Distributions": [f for f in viz_files if "distribution_" in os.path.basename(f)],
            "Gene Expression": [f for f in viz_files if any(x in os.path.basename(f) for x in ["dotplot", "matrixplot"])],
            "Violin Plots": [f for f in viz_files if "stacked_violin" in os.path.basename(f)],
            "Histograms": [f for f in viz_files if "hist_" in os.path.basename(f)],
            "Dendrogram": [f for f in viz_files if "dendrogram" in os.path.basename(f)],
            "Summary": [f for f in viz_files if "silhouette_fscore" in os.path.basename(f)],
        }
        for cat_name, files in categories.items():
            if files:
                links = " | ".join(
                    f'<a href="{github_url(f)}" target="_blank">{os.path.basename(f)}</a>'
                    for f in sorted(files)
                )
                lines.append(f'   <p><strong>{cat_name}:</strong> {links}</p>')
                
        lines.append('   </div>')
        lines.append('   </details>')
        
    lines.append("")

    # --- Reference Selection Form ---
    lines.append("Reference Selection Form")
    lines.append("-" * len("Reference Selection Form"))
    lines.append("")
    lines.append("Use this form to select a reference dataset for this organ, add your name and notes, then download the selection as a CSV file.")
    lines.append("")
    lines.append(".. raw:: html")
    lines.append("")
    lines.append(f'   <div class="reference-form" id="form-{tissue}">')
    lines.append(f'   <h3>Reference Selection: {label}</h3>')
    lines.append('   <label for="reviewer-{tissue}"><strong>Your Name:</strong></label><br>')
    lines.append(f'   <input type="text" class="reviewer-name" id="reviewer-{tissue}" placeholder="Enter your name">')
    lines.append('   <br><br>')
    lines.append('   <table class="reference-table">')
    lines.append("   <thead>")
    lines.append("   <tr>")
    lines.append("     <th>Reference?</th>")
    lines.append("     <th>Dataset</th>")
    lines.append("     <th>Author</th>")
    lines.append("     <th>Year</th>")
    lines.append("     <th>Notes</th>")
    lines.append("   </tr>")
    lines.append("   </thead>")
    lines.append("   <tbody>")

    for ds in datasets:
        author = ds.get("first_author", "Unknown")
        year = ds.get("year", "")
        dataset_name = ds.get("dataset", "")
        collection_url = ds.get("collection_url", "")
        explorer_url = ds.get("explorer_url", "")

        lines.append(f'   <tr class="dataset-row" '
                     f'data-dataset="{dataset_name}" '
                     f'data-author="{author}" '
                     f'data-year="{year}" '
                     f'data-collection-url="{collection_url}" '
                     f'data-explorer-url="{explorer_url}">')
        lines.append(f'     <td><input type="checkbox" class="ref-checkbox" data-tissue="{tissue}"></td>')
        lines.append(f'     <td>{dataset_name}</td>')
        lines.append(f"     <td>{author}</td>")
        lines.append(f"     <td>{year}</td>")
        lines.append(f'     <td><input type="text" class="notes-input" placeholder="Add notes..."></td>')
        lines.append("   </tr>")

    lines.append("   </tbody>")
    lines.append("   </table>")
    lines.append(f'   <button class="download-csv-btn" data-tissue="{tissue}">Download CSV</button>')
    lines.append("   </div>")
    lines.append("")

    return "\n".join(lines)


def generate_index_rst(tissues):
    """Generate the main index.rst with toctree."""
    label = "Cell Knowledge Network (Cell-KN)"
    lines = []
    lines.append("=" * len(label))
    lines.append(label)
    lines.append("=" * len(label))
    lines.append("")
    lines.append("Welcome to the Cell Knowledge Network dataset quality dashboard.")
    lines.append("This site presents silhouette and F-score quality metrics for single-cell")
    lines.append("RNA-seq datasets across multiple human tissues, harvested from CellxGene.")
    lines.append("")
    lines.append("Select a tissue below to view dataset summaries, quality scores, and")
    lines.append("interactive Plotly reports. You can also select a reference dataset per")
    lines.append("tissue and download your selections as a CSV.")
    lines.append("")

    # Summary table
    lines.append("Tissue Overview")
    lines.append("-" * len("Tissue Overview"))
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: 30 15 20 20")
    lines.append("")
    lines.append("   * - Tissue")
    lines.append("     - Datasets")
    lines.append("     - Avg Median Silhouette")
    lines.append("     - Avg Median F-score")

    for tissue_name, datasets in sorted(tissues.items()):
        tissue_label = get_tissue_label(tissue_name)
        n_ds = len(datasets)
        avg_sil = avg_score(datasets, "median_silhouette")
        avg_f = avg_score(datasets, "median_fscore")
        lines.append(f"   * - :doc:`tissues/{tissue_name}`")
        lines.append(f"     - {n_ds}")
        lines.append(f"     - {avg_sil}")
        lines.append(f"     - {avg_f}")

    lines.append("")

    # Toctree
    lines.append(".. toctree::")
    lines.append("   :maxdepth: 2")
    lines.append("   :caption: Tissues")
    lines.append("   :hidden:")
    lines.append("")
    for tissue_name in sorted(tissues.keys()):
        lines.append(f"   tissues/{tissue_name}")
    lines.append("")

    return "\n".join(lines)


def avg_score(datasets, key):
    """Compute average of a score field across datasets."""
    vals = []
    for ds in datasets:
        try:
            vals.append(float(ds.get(key, 0)))
        except (ValueError, TypeError):
            pass
    if not vals:
        return "N/A"
    return f"{sum(vals) / len(vals):.4f}"


def main():
    print("Cell-KN Sphinx Page Generator")
    print("=" * 40)

    # Create output directories
    TISSUES_DIR.mkdir(parents=True, exist_ok=True)

    # Find all master CSV files
    csv_files = find_master_csvs()
    print(f"Found {len(csv_files)} master_dataset_summary.csv files")

    # Group datasets by tissue
    tissues = {}
    for csv_path in csv_files:
        row = read_csv_row(csv_path)
        if not row:
            print(f"  WARNING: Empty CSV: {csv_path}")
            continue

        # Determine tissue from the organ column or directory structure
        tissue = row.get("organ", "").strip()
        if not tissue:
            # Fallback: extract from path
            parts = Path(csv_path).parts
            for i, p in enumerate(parts):
                if p == "prod" and i + 1 < len(parts):
                    tissue = parts[i + 1]
                    break

        if not tissue:
            print(f"  WARNING: Cannot determine tissue for: {csv_path}")
            continue

        # Find all viz files and build GitHub URLs
        viz_files = find_all_viz_files(csv_path)
        row["_viz_files"] = viz_files

        # Find silhouette_fscore_summary for the report link
        summary_html = [f for f in viz_files if "silhouette_fscore_summary.html" in f]
        row["_report_url"] = github_url(summary_html[0]) if summary_html else ""

        tissues.setdefault(tissue, []).append(row)

    print(f"\nFound {len(tissues)} tissues:")
    for t, ds in sorted(tissues.items()):
        print(f"  {t}: {len(ds)} datasets")

    # Generate per-tissue RST files
    for tissue, datasets in sorted(tissues.items()):
        rst_content = generate_tissue_rst(tissue, datasets)
        rst_path = TISSUES_DIR / f"{tissue}.rst"
        rst_path.write_text(rst_content, encoding="utf-8")
        print(f"  Generated: {rst_path.name}")

    # Generate index.rst
    index_content = generate_index_rst(tissues)
    index_path = DOCS_DIR / "index.rst"
    index_path.write_text(index_content, encoding="utf-8")
    print(f"  Generated: index.rst")

    print(f"\nDone! Generated {len(tissues)} tissue pages + index.rst")
    print(f"\nNext: cd docs && make html")


if __name__ == "__main__":
    main()
