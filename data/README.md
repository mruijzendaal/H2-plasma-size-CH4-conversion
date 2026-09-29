# Data

Measurement data and model results behind the figures of the paper. All files are plain CSV
(comma-separated, header row, `.` as decimal separator; empty = not available). They were
exported from the intermediate results of the original analysis by
`../processing/export_processed_data.py`; see `../processing/README.md` for how those were
obtained from the raw data. The raw data (camera image stacks, chromatograms) are available
from the author on request.

Flows are in slm (standard liters per minute). In every experiment, H2 and a diluent (Ar or
He) flow through the plasma, and CH4 is injected downstream of it (the quench).

## `raman_0d_temperatures.csv`

Gas temperature from the 0D (fiber-coupled) Raman spectra of January 2025 (Figures 2, 7b, 11a).
One row per spectrum.

| Column | Unit | Meaning |
|--------|------|---------|
| `file` | | Name of the raw spectrum file; links to `raman_0d_spectra.csv` |
| `run_id` | | Run number (first number of the filename) |
| `position` | | `core`: laser through the plasma core; `upstream`: in the mixing zone downstream of the plasma (the filename says `upstream`) |
| `power_W` | W | Microwave power, from the filename |
| `pressure_mbar` | mbar | Pressure set point |
| `H2_slm`, `Ar_slm`, `He_slm` | slm | Flows through the plasma |
| `CH4_slm` | slm | CH4 quench flow |
| `T_K` | K | Fitted rotational temperature of H2 |
| `T_err_K` | K | 1σ fit uncertainty of `T_K` (the figures show 3σ) |

Notes:
- Run 12 was measured at the 100 mbar set point, but its filename notes that the pressure
  increased to 150 mbar (`vac_increased_150mbar`).
- Figure 7b leaves out, as in the original analysis, the 25:5 slm H2:Ar runs (run 13 at
  100 mbar: 3128 ± 10 K; run 11 at 500 mbar: 1314 ± 175 K) and 10:20 slm H2:Ar at 500 mbar
  (run 08: 3333 ± 84 K).

## `raman_0d_spectra.csv`

The measured and fitted spectra behind every temperature in `raman_0d_temperatures.csv`
(Figure 2), one row per spectrum and wavelength.

| Column | Unit | Meaning |
|--------|------|---------|
| `file` | | Spectrum file, as in `raman_0d_temperatures.csv` |
| `wavelength_nm` | nm | Wavelength, after the fitted wavelength axis correction |
| `I_meas` | – | Measured intensity, background subtracted and normalized to its maximum |
| `I_fit` | – | Fitted synthetic spectrum of the vibrational Stokes Raman band of H2 |

## `raman_2d_maps.csv`

2D Raman (spectral imaging) maps in the plasma core of 29 May 2026, at 500 mbar (Figures 5
and 9). One row per (binned) pixel; 92 × 128 pixels per map.

| Column | Unit | Meaning |
|--------|------|---------|
| `file` | | Name of the raw image stack |
| `power_W` | W | Power in the filename (see note) |
| `pressure_mbar` | mbar | Pressure |
| `H2_slm`, `Ar_slm` | slm | Flows through the plasma |
| `row`, `col` | | Pixel index (row: transverse, col: axial) |
| `x_mm` | mm | Axial position, relative to the center of the image |
| `y_mm` | mm | Transverse position, relative to the center of the image |
| `I_425` | counts/pulse | Vibrational anti-Stokes signal (bandpass filter 425 nm) per camera pixel and laser pulse: median over 4 × 4 camera pixels and all frames, minus that of the background frames |
| `I_675` | counts/pulse | Vibrational Stokes signal (bandpass filter 675 nm), idem |
| `ratio_425_675` | – | `I_425 / I_675`, which gives the temperature through a calibration curve |
| `T_K` | K | Gas temperature (empty where the Stokes signal is too low) |
| `H2_density_mbar` | mbar | H2 density, as the pressure of H2 at 288 K with the same density |
| `dissociation` | – | H2 dissociation degree (empty where the Stokes signal is too low) |

Notes:
- The temperature is the calibration curve temperature closest to `ratio_425_675`, on a grid
  of 50 K. The calibration curve was later recomputed on a finer grid; with that version, the
  temperatures differ by at most 30 K.
- The filenames give 850 W (30:0 slm H2:Ar) and 900 W (the other conditions); the captions of
  Figures 5 and 9 say 1000 W.

## `gc_pure_h2.csv`

GC results of the power scans with pure H2 of April 2024 (Figure 3): 30 slm H2, 5 slm CH4.
One row per GC sample; Figure 3 shows the mean and standard deviation per power.

| Column | Unit | Meaning |
|--------|------|---------|
| `pressure_mbar` | mbar | Pressure set point |
| `power_W` | W | Microwave power |
| `H2_slm`, `CH4_slm` | slm | Flows |
| `X_CH4` | – | CH4 conversion (fraction) |

## `gc_dilution.csv`

GC results of the argon and helium dilution scans of January 2025 (Figures 7a, 8, 11b), one
row per run, averaged over the GC samples of that run.

| Column | Unit | Meaning |
|--------|------|---------|
| `run_id` | | Run number; the same runs as in `raman_0d_temperatures.csv` |
| `power_W` | W | Absorbed microwave power |
| `pressure_mbar` | mbar | Pressure set point |
| `pressure_measured_mbar` | mbar | Measured pressure |
| `H2_slm`, `Ar_slm`, `He_slm` | slm | Flows through the plasma |
| `CH4_slm` | slm | CH4 quench flow |
| `Ar_internal_standard_slm` | slm | Ar added downstream of the reactor as internal standard for the GC |
| `X_CH4` | – | CH4 conversion (fraction), using the Ar internal standard (Eq. 1) |
| `S_C2H2`, `S_C2H4`, `S_C2H6` | – | Carbon selectivity to C2H2, C2H4 and C2H6 (fraction, Eq. 2) |

Note: Figures 7a and 8 also show a run with pure argon (0:30 slm H2:Ar, 500 mbar) that gave no
CH4 conversion. It is not in the spreadsheet of the original analysis, and is added in the
figure scripts, as in the original analysis.

## `model/neutral_vs_charged_chemistry.csv`

Results of the 0D H2/Ar plasma model (Figure 10), made with `../model/neutral_vs_charged_chemistry.py`
and the chemistry set of the paper (`DLR_3`, see `../mechanism/README.md`). One row per case.

| Column | Unit | Meaning |
|--------|------|---------|
| `ne_target_m3` | m⁻³ | Target electron density (10 m⁻³ stands for 0) |
| `Tg_K` | K | Gas temperature |
| `X_Ar_inlet` | – | Ar fraction of the H2/Ar mixture |
| `Te_eV` | eV | Electron temperature that gives the target electron density |
| `ne_m3` | m⁻³ | Resulting electron density (within 10% of the target, or the closest reachable) |
| `production_H_kmol_m3_s` | kmol/m³/s | Net production rate of H |
| `X_H`, `X_H2` | – | Mole fractions of H and H2 after 100 ms |
| `density_kmol_m3` | kmol/m³ | Total molar density |

## `photos/`

The optical images of Figure 6 (500 mbar, 1000 W, 0.5 s exposure), as processed for the
paper (normalized to the 99th percentile of the intensity, clipped and mirrored): 30:0, 5:25 and 1:29
slm H2:Ar.

## License

[CC BY 4.0](LICENSE).
