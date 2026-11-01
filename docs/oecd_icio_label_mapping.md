# OECD ICIO 2025 Extended — Dimension mapping

Source: user-provided `data/oecd_source/ReadMe_ICIO_extended.xlsx`, sheet `Area_Activities`. The `RowItems` and `ColItems` sheets verify the ordering of all 4,250 intermediate-input activity columns and rows.

- 85 economy/area codes: 80 economies, ROW (Rest of the World), and China/Mexico split components CN1, CN2, MX1, MX2. Treat these as **85 area codes**, not 85 sovereign states.
- 50 sectors per area using ISIC Rev.4 descriptions.
- `RowItems` and `ColItems` contain the ordered 4,250 combinations (`AGO_A01` ... `CN2_T`) in the intermediate-use block. Additional final-demand, total, and value-added items are present in the workbooks and must not be treated as 4,250 extra industries.
- Example economies: `CHN = China, People's Republic of`, `DEU = Germany`, `USA = United States`.
- Example sectors: `C26 = Manufacture of computer, electronic and optical products`; `K = Financial and insurance activities`.

The application ships with the full dictionary `src/gvc/data/oecd_icio_2025_extended.json` and two Excel-compatible CSV exports in `data/catalog/`.

## Correct data assignment

The built-in 2007 MATLAB sample has a different 48-area × 17-sector structure with unverified labels. Its charts retain explicit index labels. Applying the 2025 OECD names by order to 2007 results would be incorrect.

For a new, correctly structured 2025 Extended dataset:

1. Prepare `Z.csv` (4250×4250), `Y.csv` (4250×85), `VA.csv` (4250 values), `X.csv` (4250 values) using the project's canonical input specification. The published ICIO table is **not already in this canonical CSV layout**; the input and final-demand categories must first be correctly transformed. The project's direct-import adapter for original OECD releases is not implemented.
2. Add the supplied `examples/oecd_icio_2025_metadata_template.json` as `metadata.json` alongside those four files.
3. Independently verify the actual matrix order against RowItems and ColItems, and that any aggregation of final-demand categories preserves the intended destinations. Set `axis_order_confirmed` to `true` only after verification. The code lists must match exactly.
4. In Streamlit choose `85` economies and `50` industries and select the directory or ZIP. If dimensions, order, or metadata do not match, the application rejects label assignment.

This is a naming/metadata integration. It is not evidence that the current WWZ computational engine has been performance-tested or numerically validated on an 85×50 ICIO dataset. No 2025 transactional IO table was supplied in the workbook, only the README.

## Source verification

Verified against all 85 names and 50 sectors in the attached workbook, including sector ISIC descriptions. Also checked the complete 4,250-item ordered intermediate activity identifiers in both RowItems and ColItems. The arrays exactly match the JSON dictionary and the Cartesian product in economy-major, sector-minor order.

OECD source information: https://oe.cd/icio. This project is not affiliated with OECD.
