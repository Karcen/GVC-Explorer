# GVC Explorer

[中文版](README.md) · [Jiacheng Zheng](https://karcen.github.io/)

GVC Explorer is a Python port of the 16-term export decomposition (T1–T16) in `valueadded2007.m`. The repository keeps the original MATLAB scripts, the 2007 input–output workbook, and its saved calculation outputs so that the implementation can be checked against the source. The computation is separate from the interface: Streamlit reads and computes IO data; `offline_dashboard.html` displays the precomputed 2007 results.

The implemented scope is the bilateral, industry-level 16-term decomposition in the original MATLAB script. The full TiVA routines and the Chinese regional IO linking procedure have not been ported.

## Quick start

Open `offline_dashboard.html` in a browser to inspect the included 2007 results without installing Python. You can select an exporter, importer, industry, and decomposition term. The page updates the 16-term chart, industry–destination heatmap, and destination ranking; clicking a heatmap cell updates the selection. The button in the header switches between light and dark appearance. Where browser storage permits, the setting persists across visits. This HTML file is a read-only viewer, not a computation engine.

To calculate from input data, open a terminal in the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
streamlit run app.py
```

Choose **Built-in 2007 sample** (内置 2007 样例), then click **Load and compute** (载入并计算). The app also accepts a local IO directory or a ZIP archive containing a complete dataset. The Python requirement is defined in `pyproject.toml` (currently Python 3.10 or newer).

For a command-line run:

```bash
python run_batch.py --input data/reference_2007 --output output
```

This writes `output/wwz_results.npz` and `output/validation.json`. The `terms` array has shape `(16, S×N, S)`; both `total_exports` and `discrepancy` have shape `(S×N, S)`, with `S` economies and `N` industries per economy.

## Input format

Two input layouts are currently defined.

The legacy workbook layout uses a file named `2007global.xlsx` with a numeric `Sheet2` arranged as in the original MATLAB code.

The canonical CSV layout is a directory with all four files below:

| File | Content | Shape |
| --- | --- | --- |
| `Z.csv` | Intermediate transaction matrix | `(S×N, S×N)` |
| `Y.csv` | Final demand aggregated by destination economy | `(S×N, S)` |
| `VA.csv` | Value-added vector | `(S×N,)` |
| `X.csv` | Gross-output vector | `(S×N,)` |

Rows and columns must follow economy-major, industry-minor order. All four files must use the same economy and industry ordering; every economy must have the same number of industries. `Y.csv` is already aggregated across final-demand categories within each destination economy. A raw final-demand matrix with separate consumption categories cannot be passed unchanged.

An optional `metadata.json` may specify `year`, `unit`, `country_names`, and `industry_names`. Label arrays must match the input dimensions. Without a verified mapping, the interface displays indices rather than inferred country or industry names. See `examples/` for templates.

The loader does not automatically infer the structure of arbitrary OECD or WIOD spreadsheets. Convert unsupported table layouts to the documented input format first.

## OECD ICIO 2025 Extended directory

The label dictionary was transcribed from `data/oecd_source/ReadMe_ICIO_extended.xlsx`. It contains 85 economy/area codes and 50 industry codes, with ISIC Rev.4 descriptions. The `RowItems` and `ColItems` order was checked against all 4,250 economy–industry positions. The resulting catalogs are stored under `data/catalog/` and `src/gvc/data/oecd_icio_2025_extended.json`.

The Streamlit interface provides a searchable directory. The offline viewer has separate OECD economy and sector selectors. These are reference tools; selecting an OECD code does not relabel the legacy 2007 results.

**The legacy 2007 data have 48 economies/areas and 17 industries.** Their authoritative label order has not been established. Assigning the 2025 OECD 85×50 names to those arrays by position would be incorrect. For an actual OECD ICIO 2025 Extended dataset, confirm the row and column order and use `examples/oecd_icio_2025_metadata_template.json`. See `docs/oecd_icio_label_mapping.md` for the mapping requirements.

The OECD README supplies labels, not the 2025 numerical IO matrices. Full 85×50 computation and performance have not been validated.

## WWZ 16-term decomposition: formulas and definitions

The following terms follow the T1–T16 order in `valueadded2007.m` and Table E1 of Wang, Wei, and Zhu (2013). Each term is an $N\times1$ vector of gross exports **by the exporting industry's product**, for exporter $s$ and direct importer $r$. The dashboard selects one component of that vector for each industry.

### Notation

- $s$ is the exporter, $r$ the direct importer, and $t,u$ index economies in subsequent production or final absorption; $s\ne r$. Each economy has $N$ industries.
- $Z^{sr}$ records intermediate transactions from $s$ to $r$, and $A^{sr}=Z^{sr}\operatorname{diag}(X^r)^{-1}$ is the corresponding input-coefficient block. $X^r$ is the gross-output vector of $r$.
- $A$ is the global input-coefficient matrix, $B=(I-A)^{-1}$ the global Leontief inverse, and $B^{sr}$ its $(s,r)$ block. $L^{ss}=(I-A^{ss})^{-1}$ is the domestic Leontief inverse of $s$.
- $V^s=(v_1^s,\ldots,v_N^s)$ is a row vector of value-added coefficients, with $v_k^s=VA_k^s/X_k^s$. $Y^{sr}$ is the vector of final products made in $s$ and absorbed in $r$, aggregated across final-demand categories.
- $E^{sr}=A^{sr}X^r+Y^{sr}$ is the bilateral gross-export vector. $E^{r*}=\sum_{u\ne r}(A^{ru}X^u+Y^{ru})$ is $r$'s vector of exports to all foreign destinations.
- $Q^{sr}=\sum_{t\notin\{s,r\}}V^tB^{ts}$ is the third-country value-added coefficient in the output of $s$. ${}^{\mathsf T}$ denotes transpose; $\odot$ denotes element-wise multiplication (MATLAB `.*`).

Because the terms are allocated by the exporting product industry, $V^sB^{ss}$ includes value added from other upstream industries in $s$. T1 is not restricted to value added generated within the exporting industry itself.

### Domestic value added absorbed abroad: T1–T5

**T1 — DVA_FIN: domestic value added in final-goods exports.**

$$
T_1^{sr}=(V^sB^{ss})^{\mathsf T}\odot Y^{sr}.
$$

**T2 — DVA_INT: domestic value added in intermediate exports used by the direct importer to make final products absorbed there.**

$$
T_2^{sr}=(V^sL^{ss})^{\mathsf T}\odot(A^{sr}B^{rr}Y^{rr}).
$$

**T3 — DVA_INTrex1: domestic value added in intermediates re-exported by the direct importer and used to make final products absorbed within third countries.**

$$
T_3^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{tt}\right).
$$

**T4 — DVA_INTrex2: domestic value added in intermediate exports embodied in the direct importer's final-goods exports to third countries.**

$$
T_4^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}B^{rr}\sum_{u\notin\{s,r\}}Y^{ru}\right).
$$

**T5 — DVA_INTrex3: domestic value added in intermediates re-exported as intermediates to third countries and subsequently used for foreign final demand.**

$$
T_5^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}
\sum_{u\notin\{s,t\}}Y^{tu}\right).
$$

### Returned domestic value added: T6–T8

**T6 — RDV_FIN1: domestic value added returning in final goods imported from the direct importer.**

$$
T_6^{sr}=(V^sL^{ss})^{\mathsf T}\odot(A^{sr}B^{rr}Y^{rs}).
$$

**T7 — RDV_FIN2: domestic value added returning in final goods imported from third countries.**

$$
T_7^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{ts}\right).
$$

**T8 — RDV_INT: domestic value added returning as intermediate imports used for final production and consumption at home.**

$$
T_8^{sr}=(V^sL^{ss})^{\mathsf T}\odot(A^{sr}B^{rs}Y^{ss}).
$$

### Domestic double counting: T9–T10

**T9 — DDC_FIN: domestic value added counted more than once in the production of final-goods exports.** This is a gross-trade accounting component, not newly generated value added.

$$
T_9^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}B^{rs}\sum_{u\ne s}Y^{su}\right).
$$

**T10 — DDC_INT: domestic value added counted more than once in intermediate exports.**

$$
T_{10}^{sr}=\left(V^sB^{ss}-V^sL^{ss}\right)^{\mathsf T}
\odot(A^{sr}X^r).
$$

### Direct importer's value added and double counting: T11–T13

**T11 — MVA_FIN: value added originating in the direct importer and embodied in the exporter's final-goods exports.**

$$
T_{11}^{sr}=(V^rB^{rs})^{\mathsf T}\odot Y^{sr}.
$$

**T12 — MVA_INT: value added originating in the direct importer and embodied in the exporter's intermediate exports.**

$$
T_{12}^{sr}=(V^rB^{rs})^{\mathsf T}\odot
(A^{sr}L^{rr}Y^{rr}).
$$

**T13 — MDC: the direct importer's value added counted more than once in the exporter's production for export.**

$$
T_{13}^{sr}=(V^rB^{rs})^{\mathsf T}\odot
(A^{sr}L^{rr}E^{r*}).
$$

### Third-country value added and double counting: T14–T16

**T14 — OVA_FIN: third-country value added embodied in the exporter's final-goods exports.**

$$
T_{14}^{sr}=(Q^{sr})^{\mathsf T}\odot Y^{sr}.
$$

**T15 — OVA_INT: third-country value added embodied in the exporter's intermediate exports.**

$$
T_{15}^{sr}=(Q^{sr})^{\mathsf T}\odot
(A^{sr}L^{rr}Y^{rr}).
$$

**T16 — ODC: third-country value added counted more than once in the exporter's production for export.**

$$
T_{16}^{sr}=(Q^{sr})^{\mathsf T}\odot
(A^{sr}L^{rr}E^{r*}).
$$

### Accounting identities

For each exporter $s$, importer $r\ne s$, and exporting industry, the terms sum to gross bilateral exports:

$$
E^{sr}=\sum_{k=1}^{16}T_k^{sr}.
$$

The main groups are domestic value added absorbed abroad ($T_1+\cdots+T_5$), returned domestic value added ($T_6+T_7+T_8$), domestic double counting ($T_9+T_{10}$), foreign value added ($T_{11}+T_{12}+T_{14}+T_{15}$), and foreign double counting ($T_{13}+T_{16}$). Terms T11–T13 originate in the direct importer; T14–T16 originate in third countries. Double-counting components are not additional value added. Shares should be recomputed from summed amounts rather than averaged without weights.

These formulas match the vector implementation in `valueadded2007.m`; the economic labels follow Equation (18) and Table E1 in Appendix E of [Wang, Wei, and Zhu (2013), NBER Working Paper 19677](https://www.nber.org/papers/w19677). The MATLAB `tt2`–`tt9` variables are intermediate-flow path calculations used in T2–T9, not a separate set of WWZ terms.

## Computation and validation

`src/gvc/engine.py` ports T1–T16 and the related intermediate-export calculations from `valueadded2007.m`. Input handling is in `src/gvc/loaders.py`; the Leontief linear system is solved with SciPy.

The port was run on the supplied 2007 workbook and compared element by element with the 16 saved MATLAB CSV exports:

- Input structure: 48 economies/areas, 17 industries each.
- Decomposition output: `(16, 816, 48)`.
- Maximum scaled relative difference across the 16 terms: below 0.005%, using `max(|CSV reference|, 1)` as the denominator.
- Maximum absolute difference between the sum of the 16 terms and gross bilateral industry exports: approximately `1.16×10⁻¹⁰`, in the source workbook's units.

Per-term comparisons are in `reports/validation_2007.json`. The saved CSV files have limited significant digits, which affects the attainable elementwise agreement. MATLAB was not rerun in this environment: this is a replication against **saved MATLAB output**, not a fresh two-runtime parity test. Other years, source layouts, and full-scale OECD 2025 data have not received equivalent numerical validation.

Run the Python tests with:

```bash
python -m pytest -q
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit computation and charts |
| `offline_dashboard.html` | Self-contained 2007 results viewer; light/dark themes |
| `build_offline_preview.py` | Rebuild the offline viewer from saved results |
| `src/gvc/engine.py` | 16-term decomposition engine |
| `src/gvc/loaders.py` | IO data loading |
| `src/gvc/metadata.py` | Label provenance and axis-order checks |
| `data/reference_2007/` | 2007 inputs and historical exports |
| `data/matlab_original/` | Unmodified MATLAB source files |
| `data/catalog/` | OECD 2025 Extended label catalogs |
| `reports/` | Validation records and figures |
| `tests/` | Automated Python tests |

After installation, regenerate the offline page using:

```bash
python build_offline_preview.py
```

The builder reads `output/wwz_python_2007.npz`. It does not recompute the decomposition.

## What is not yet covered

The repository retains `tradeinvalueadded2007.m`, `GVCDVC.m`, and the regional IO linking workbook without a completed Python port. Group labels in the UI are navigational summaries of the source code, not substitutes for the paper's formal term definitions. The reproduced data cover one year, so they do not support time-series charts. The original workbook's currency unit has not been independently established.

The offline viewer has undergone a Chromium interaction check. A complete end-to-end run of the Streamlit server is still pending in an environment with Streamlit installed. Publication figures use Matplotlib and have not been certified against the user's local Nature Figure Skill.

The application performs computation locally and does not send IO tables to external services. Before publishing this repository, check the redistribution rights for the original MATLAB scripts and IO data. `.gitignore` excludes those source-data directories by default. `AGENTS.md` and `docs/CODEX_HANDOFF.md` contain instructions for future Codex work; they are not evidence that Codex ran on this release.

## Method citation

For research using the WWZ decomposition method implemented here, cite the original working paper:

Wang, Z., Wei, S. J., & Zhu, K. (2013). *Quantifying international production sharing at the bilateral and sector levels* (No. w19677). National Bureau of Economic Research.

[NBER Working Paper 19677](https://www.nber.org/papers/w19677)

Maintained by **[Jiacheng Zheng](https://karcen.github.io/)**.
