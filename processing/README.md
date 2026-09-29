# Processing (provenance)

These scripts document how the files in `../data/` were obtained from the raw measurement data.
They are **not needed to reproduce the figures**, and they cannot be run from this repository
alone: they need the raw data (available from the author on request) and in-house analysis
packages.

| Script | Input | Output | Requires |
|--------|-------|--------|----------|
| `process_raman_0d.py` | Raw 0D Raman spectra of January 2025 (Andor `.sif`) | `results.pkl` (temperatures and spectra) | [ramlab](https://github.com/Brightsite-Plasmalab/ramlab), [labctl](https://github.com/Brightsite-Plasmalab/labctl), [toddler](https://github.com/mruijzendaal/toddler) |
| `process_raman_2d.py` | Raw 2D Raman image stacks of 29 May 2026 (Andor `.sif`) and the calibration curve | `processed_results.pkl` (maps) | labctl, toddler |
| `export_processed_data.py` | The files above, and the GC spreadsheets | `../data/*.csv` | toddler (to read `processed_results.pkl`), openpyxl |

`export_processed_data.py` can be run with `uv run --group processing processing/export_processed_data.py <dir>`,
where `<dir>` is the author's OneDrive directory that contains `Data/` and `Contributions/`.

The two processing scripts are transcriptions of the notebooks of the original analysis
(`exp_fit.ipynb` and `260529/final.ipynb`), with the absolute paths removed and the plotting
cells left out. They were not re-run for this repository: the figures in the paper come from
the pickled results that they produced, and those are exported by `export_processed_data.py`.
They were produced with development versions of the in-house packages (labctl, ramlab and
toddler, installed from their working trees), which were not tagged.

The GC results were computed in spreadsheets (not included; available on request):
- `30H2_5CH4_<p>mBar_mi_20240417.xlsx`, sheet "GC analysis", one per pressure: the pure H2
  power scans (`gc_pure_h2.csv`);
- `Quenching experiment_2025_MLA_MR_averages.xlsx`, sheet "Averages" (version of 8 June 2026):
  the dilution scans (`gc_dilution.csv`). The version of 12 March 2026 has the same values in
  the columns that the figures use.

The photographs of Figure 6 (`../data/photos/`) were processed from the camera images (TIFF)
by `oes_img_tiff.ipynb` of the original analysis; they are included as they appear in the paper.
