# Gene Mapping Utilities

Utilities for mapping Ensembl gene IDs (ENSG) to human-readable gene symbols using the [cell-kn gene mapping file](https://github.com/NIH-NLM/cell-kn/blob/main/data/biomart/gene_mapping.csv).

## Quick Start

### Installation

Just copy `gene_mapping_utils.py` into your project directory.

```bash
# Download the utility script
curl -O https://raw.githubusercontent.com/NIH-NLM/cell-kn/main/utils/gene_mapping_utils.py
```

Or save directly from: [gene_mapping_utils.py](gene_mapping_utils.py)

### Basic Usage

```python
from gene_mapping_utils import load_gene_mapping, create_mapping_dict

# Load mapping (cached locally for speed)
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)

# Map a single list
genes = ['ENSG00000167286', 'ENSG00000010610', 'ENSG00000153563']
mapped = [ensg_to_symbol.get(g, g) for g in genes]
print(mapped)
# Output: ['CD3D', 'CD4', 'CD8A']
```

## Use Cases

### 1. NSForest Results

Map marker genes from NSForest output:

```python
import pandas as pd
from gene_mapping_utils import load_gene_mapping, create_mapping_dict

# Load NSForest results
results = pd.read_csv("nsforest_results.csv")

# Load gene mapping
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)

# Map ENSG IDs to gene names (FAST using list comprehension)
results['gene_names'] = [
    [ensg_to_symbol.get(gene, gene) for gene in markers]
    for markers in results['NSForest_markers']
]

# Create markers dictionary for plotting
markers_dict = dict(zip(results["clusterName"], results["gene_names"]))

# Plot with readable gene names
import nsforest as ns
ns.pl.dotplot(adata, markers_dict, cluster_header, dendrogram=True)
```

### 2. Single-cell Analysis

Map differentially expressed genes:

```python
# Load DEG results
deg_df = pd.read_csv("deg_results.csv")

# Map gene IDs
gene_mapping = load_gene_mapping()
ensg_to_symbol = create_mapping_dict(gene_mapping)
deg_df['gene_symbol'] = deg_df['gene_id'].map(ensg_to_symbol)

# Now you have readable gene names for downstream analysis
```

### 3. Quick One-Liner

For simple cases:

```python
from gene_mapping_utils import quick_map

# Map a list
mapped_genes = quick_map(['ENSG00000167286', 'ENSG00000010610'])

# Or map a dataframe column
df = quick_map(results_df, column='NSForest_markers')
```

## Performance

The utility includes optimizations for large-scale mapping:

| Method | Speed | Description |
|--------|-------|-------------|
| First run | ~2-5s | Downloads and caches gene_mapping.csv |
| Subsequent runs | ~0.2s | Loads from cached file |
| Mapping | Fast | Uses list comprehension (5-10x faster than apply) |

**Tip:** The first time you run `load_gene_mapping()`, it downloads and caches the file locally. All subsequent runs load from the cache for maximum speed.

## API Reference

### `load_gene_mapping(cache_file="gene_mapping.csv", use_cache=True)`

Load gene mapping file from GitHub or local cache.

**Parameters:**
- `cache_file` (str): Local filename to cache the mapping file
- `use_cache` (bool): If True, use cached file if it exists

**Returns:** pd.DataFrame with columns `ensembl_gene_id` and `external_gene_name`

---

### `create_mapping_dict(gene_mapping)`

Create ENSG ID to gene symbol mapping dictionary.

**Parameters:**
- `gene_mapping` (pd.DataFrame): Gene mapping dataframe from `load_gene_mapping()`

**Returns:** dict mapping ensembl_gene_id to external_gene_name

---

### `map_genes(gene_list, mapping_dict)`

Map a list of ENSG IDs to gene symbols.

**Parameters:**
- `gene_list` (list): List of gene identifiers (ENSG IDs or symbols)
- `mapping_dict` (dict): Dictionary from `create_mapping_dict()`

**Returns:** list of gene symbols (keeps original if mapping not found)

---

### `map_dataframe_column(df, column, mapping_dict, new_column=None)`

Map ENSG IDs in a dataframe column to gene symbols.

**Parameters:**
- `df` (pd.DataFrame): Dataframe containing gene lists
- `column` (str): Column name containing lists of ENSG IDs
- `mapping_dict` (dict): Dictionary from `create_mapping_dict()`
- `new_column` (str): Name for new column (default: `{column}_symbols`)

**Returns:** pd.DataFrame with new column containing mapped gene symbols

---

### `quick_map(gene_list_or_df, column=None, cache_file="gene_mapping.csv")`

Quick one-function mapping for common use cases.

**Parameters:**
- `gene_list_or_df` (list or pd.DataFrame): List of genes or dataframe
- `column` (str): Column name if using dataframe
- `cache_file` (str): Local cache filename

**Returns:** Mapped genes as list or dataframe with new mapped column

## Examples

See the examples in `gene_mapping_utils.py` or run:

```python
python gene_mapping_utils.py
```

## Data Source

This utility uses the gene mapping file from the NIH NLM cell-kn repository:
- **Repository:** https://github.com/NIH-NLM/cell-kn
- **Mapping file:** data/biomart/gene_mapping.csv
- **Source:** BioMart Ensembl gene annotations

## Troubleshooting

**Issue:** Slow performance

**Solution:** Make sure caching is enabled (default). First run downloads the file, subsequent runs are much faster.

---

**Issue:** Some genes don't map

**Solution:** The function keeps the original gene ID if no mapping is found. This is expected for some genes not in the BioMart database.

---

**Issue:** "KeyError: 'ensembl_gene_id'"

**Solution:** Make sure you're using the correct gene_mapping.csv file from the cell-kn repository.

## Contributing

Issues and pull requests welcome at: https://github.com/NIH-NLM/cell-kn

## License

Same as parent repository (cell-kn)
