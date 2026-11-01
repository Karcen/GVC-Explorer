# GVC Explorer · Trade Atlas

[中文](README.md) · [Offline formula handbook](docs/formulas_en.html) · [Jiacheng Zheng](https://karcen.github.io/)

Choose an exporter, its direct importer and a product industry to trace a bilateral export flow through the 16 WWZ components. The desktop application computes new tables; the offline atlas explores a completed run.

## Getting started

Unzip the project and open `offline_dashboard.html` for the 2007 benchmark. It opens on exports from Germany to the United States across all industries. Switch languages, select a trade direction, click a heatmap cell, or download the selected breakdown as CSV. The page needs neither Python nor a network connection.

To import data, install Python 3.10 or later with Tk. On macOS, open `start_studio.command`; on Windows, open `start_studio.bat`. First-time dependency installation needs internet access; computation and figure export do not. On Linux, or to launch manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python desktop.py
```

Click **Import annual table or ZIP**. Try `examples/fixture_3area_3sector.csv` for a small test with negative inventory changes and net product taxes. It is synthetic, not an observed OECD table. Each run creates a separate directory under `runs/`, or the output location you choose. Figures use the active language. After changing a filter or the language, **Export this selection** saves a new set without overwriting the first.

```bash
python studio_batch.py examples/fixture_3area_3sector.csv --output runs --language en
```

## Input and accounting basis

The annual reader accepts labelled OECD-style wide CSV, CSV.GZ, and ZIP archives containing annual CSVs. Rows supply products; columns use them. Keys such as `AUS_C26` align row and column blocks independently. The file must contain six final-demand categories per destination (HFCE, NPISH, GGFC, GFCF, INVNT and DPABR), a value-added row, and both a gross-output row and column. Negative inventory changes are retained. Duplicate keys, missing cells, unsupported classifications and out-of-tolerance balances stop the run. This adapter interprets amounts in USD million; use the matrix directory for other units.

When nonzero taxes less subsidies on products (TLS) enter the input balance, the decomposition attributes VA plus TLS, not pure value added. National accounts use the China and Mexico consolidated blocks, not those blocks plus their firm-type breakdowns. Split-only data without national totals are rejected. The supplied lookup covers the bundled 2025 Extended codebook; other editions may need their own lookup.

The program also accepts the exact reference workbook `2007global.xlsx`, or a directory with headerless `Z.csv`, `Y.csv`, `VA.csv`, `X.csv` and `metadata.json`. Order the matrices by economy, then industry. Aggregate final demand into one column per destination. Set `country_names`, `industry_names` in matrix order and specify `unit`. Custom names are displayed as supplied in both languages.

## Labels in the 2007 benchmark

Sheet1 of the input workbook identifies 48 economies/areas and 17 industries. Its 665,856 intermediate transactions and 117,504 final-demand entries match the numeric sheet read by the MATLAB program exactly. Sheet1 cell C4 specifies USD million. The eight Chinese regions remain distinct accounting units, so cross-region flows enter cross-unit exports and cannot be read directly as Chinese international trade. See the [axis audit](reports/legacy_axis_audit.json).

## Charts and output

Each run produces eight views: sixteen export components, five accounting groups, export destinations, bilateral industries, industry-by-destination heatmap, two-way trade, exports versus imports, and the largest bilateral flows. Each has a PDF, PNG, SVG and plotted-data CSV. The heatmap selects up to eight industries and ten destinations by gross exports, then colours cells by the chosen component in currency units. The trade profile and corridor ranking cover all economies. Each chart states its scope.

Every exported PDF runs through the upstream nature-figure text auditor with a 6.5 pt minimum. The figure directory contains its `nature_text_audit.json`.

`atlas.html` is the bilingual offline viewer; `results.npz` holds unrounded arrays; `metadata.json` records names and the accounting basis. `manifest.json` stores input and output hashes, version information, and the reconciliation residual. Benchmark exports in both languages are included in `reports/atlas_2007/`.

## WWZ 16-term decomposition: formulas and definitions

The following terms follow the T1–T16 order in `valueadded2007.m` and Table E1 of Wang, Wei, and Zhu (2013). Each term is an $`N\times1`$ vector of gross exports **by the exporting industry's product**, for exporter $`s`$ and direct importer $`r`$. The dashboard selects one component of that vector for each industry.

### Notation

- $`s`$ is the exporter, $`r`$ the direct importer, and $`t,u`$ index economies in subsequent production or final absorption; $`s\ne r`$. Each economy has $`N`$ industries.
- $`Z^{sr}`$ records intermediate transactions from $`s`$ to $`r`$, and $`A^{sr}=Z^{sr}\operatorname{diag}(X^r)^{-1}`$ is the corresponding input-coefficient block. $`X^r`$ is the gross-output vector of $`r`$.
- $`A`$ is the global input-coefficient matrix, $`B=(I-A)^{-1}`$ the global Leontief inverse, and $`B^{sr}`$ its $`(s,r)`$ block. $`L^{ss}=(I-A^{ss})^{-1}`$ is the domestic Leontief inverse of $`s`$.
- $`V^s=(v_1^s,\ldots,v_N^s)`$ is a row vector of value-added coefficients, with $`v_k^s=VA_k^s/X_k^s`$. $`Y^{sr}`$ is the vector of final products made in $`s`$ and absorbed in $`r`$, aggregated across final-demand categories.
- $`E^{sr}=A^{sr}X^r+Y^{sr}`$ is the bilateral gross-export vector. $`E^{r*}=\sum_{u\ne r}(A^{ru}X^u+Y^{ru})`$ is $`r`$'s vector of exports to all foreign destinations.
- $`Q^{sr}=\sum_{t\notin\{s,r\}}V^tB^{ts}`$ is the third-country value-added coefficient in the output of $`s`$. $`{}^{\mathsf{T}}`$ denotes transpose; $`\odot`$ denotes element-wise multiplication (MATLAB `.*`).

Because the terms are allocated by the exporting product industry, $`V^sB^{ss}`$ includes value added from other upstream industries in $`s`$. T1 is not restricted to value added generated within the exporting industry itself.

### Domestic value added absorbed abroad: T1–T5

**T1 — DVA_FIN: domestic value added in final-goods exports.**

```math
T_1^{sr}=(V^sB^{ss})^{\mathsf{T}}\odot Y^{sr}.
```

**T2 — DVA_INT: domestic value added in intermediate exports used by the direct importer to make final products absorbed there.**

```math
T_2^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot(A^{sr}B^{rr}Y^{rr}).
```

**T3 — DVA_INTrex1: domestic value added in intermediates re-exported by the direct importer and used to make final products absorbed within third countries.**

```math
T_3^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{tt}\right).
```

**T4 — DVA_INTrex2: domestic value added in intermediate exports embodied in the direct importer's final-goods exports to third countries.**

```math
T_4^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}B^{rr}\sum_{u\notin\{s,r\}}Y^{ru}\right).
```

**T5 — DVA_INTrex3: domestic value added in intermediates re-exported as intermediates to third countries and subsequently used for foreign final demand.**

```math
T_5^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}
\sum_{u\notin\{s,t\}}Y^{tu}\right).
```

### Returned domestic value added: T6–T8

**T6 — RDV_FIN1: domestic value added returning in final goods imported from the direct importer.**

```math
T_6^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot(A^{sr}B^{rr}Y^{rs}).
```

**T7 — RDV_FIN2: domestic value added returning in final goods imported from third countries.**

```math
T_7^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{ts}\right).
```

**T8 — RDV_INT: domestic value added returning as intermediate imports used for final production and consumption at home.**

```math
T_8^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot(A^{sr}B^{rs}Y^{ss}).
```

### Domestic double counting: T9–T10

**T9 — DDC_FIN: domestic value added counted more than once in the production of final-goods exports.** This is a gross-trade accounting component, not newly generated value added.

```math
T_9^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}B^{rs}\sum_{u\ne s}Y^{su}\right).
```

**T10 — DDC_INT: domestic value added counted more than once in intermediate exports.**

```math
T_{10}^{sr}=\left(V^sB^{ss}-V^sL^{ss}\right)^{\mathsf{T}}
\odot(A^{sr}X^r).
```

### Direct importer's value added and double counting: T11–T13

**T11 — MVA_FIN: value added originating in the direct importer and embodied in the exporter's final-goods exports.**

```math
T_{11}^{sr}=(V^rB^{rs})^{\mathsf{T}}\odot Y^{sr}.
```

**T12 — MVA_INT: value added originating in the direct importer and embodied in the exporter's intermediate exports.**

```math
T_{12}^{sr}=(V^rB^{rs})^{\mathsf{T}}\odot
(A^{sr}L^{rr}Y^{rr}).
```

**T13 — MDC: the direct importer's value added counted more than once in the exporter's production for export.**

```math
T_{13}^{sr}=(V^rB^{rs})^{\mathsf{T}}\odot
(A^{sr}L^{rr}E^{r*}).
```

### Third-country value added and double counting: T14–T16

**T14 — OVA_FIN: third-country value added embodied in the exporter's final-goods exports.**

```math
T_{14}^{sr}=(Q^{sr})^{\mathsf{T}}\odot Y^{sr}.
```

**T15 — OVA_INT: third-country value added embodied in the exporter's intermediate exports.**

```math
T_{15}^{sr}=(Q^{sr})^{\mathsf{T}}\odot
(A^{sr}L^{rr}Y^{rr}).
```

**T16 — ODC: third-country value added counted more than once in the exporter's production for export.**

```math
T_{16}^{sr}=(Q^{sr})^{\mathsf{T}}\odot
(A^{sr}L^{rr}E^{r*}).
```

### Accounting identities

For each exporter $`s`$, importer $`r\ne s`$, and exporting industry, the terms sum to gross bilateral exports:

```math
E^{sr}=\sum_{k=1}^{16}T_k^{sr}.
```

The main groups are domestic value added absorbed abroad ($`T_1+\cdots+T_5`$), returned domestic value added ($`T_6+T_7+T_8`$), domestic double counting ($`T_9+T_{10}`$), foreign value added ($`T_{11}+T_{12}+T_{14}+T_{15}`$), and foreign double counting ($`T_{13}+T_{16}`$). Terms T11–T13 originate in the direct importer; T14–T16 originate in third countries. Double-counting components are not additional value added. Shares should be recomputed from summed amounts rather than averaged without weights.

These formulas match the vector implementation in `valueadded2007.m`; the economic labels follow Equation (18) and Table E1 in Appendix E of [Wang, Wei, and Zhu (2013), NBER Working Paper 19677](https://www.nber.org/papers/w19677). The MATLAB `tt2`–`tt9` variables are intermediate-flow path calculations used in T2–T9, not a separate set of WWZ terms.

## Validation and limits

The Python benchmark was rerun and compared with the sixteen saved MATLAB CSVs. The largest elementwise scaled difference was 0.004986%, using the larger of one and the absolute reference value as the denominator. The maximum absolute bilateral industry reconciliation residual was 1.1642 × 10⁻¹⁰ USD million. MATLAB was not rerun. No equivalent full-size validation was performed for an entire OECD annual table. This port does not implement the separate full TiVA or regional linking routines. The legacy Streamlit entry point is optional and is not the bilingual desktop app.

To test: `python -m pip install -e '.[dev]'`, then `python -m pytest -q`. Rebuild the offline benchmark with `python build_offline_preview.py`. See `reports/figure_qa.json` for export checks. The archive grants no new redistribution rights for the original data and MATLAB source.

## Method citation

For research using the WWZ decomposition method implemented here, cite the original working paper:

Wang, Z., Wei, S. J., & Zhu, K. (2013). *Quantifying international production sharing at the bilateral and sector levels* (No. w19677). National Bureau of Economic Research.

[NBER Working Paper 19677](https://www.nber.org/papers/w19677)

Maintained by **[Jiacheng Zheng](https://karcen.github.io/)**.
