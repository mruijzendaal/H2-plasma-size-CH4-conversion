"""Export the intermediate analysis results to the plain-text files in `data/`.

This script documents how the files in `data/` were produced. It is NOT needed to
reproduce the figures, and it cannot be run without the original data directories of the
author (which contain the pickled intermediate results and spreadsheets listed below).

Usage:
    uv run --group processing processing/export_processed_data.py /path/to/OneDrive-MaastrichtUniversity

Inputs (relative to that directory):
    Data/250116/results.pkl                                        0D Raman fits (process_raman_0d.py)
    Data/250116/H2_Ar_GC/Quenching experiment_2025_MLA_MR_averages.xlsx
                                                                   GC results of the dilution scans
    Contributions/H2_Ar/data/H2_Ar_GC/30H2_5CH4_<p>mBar_mi_20240417.xlsx
                                                                   GC results of the pure H2 power scans
    Data/260529/processed_results.pkl                              2D Raman maps (process_raman_2d.py)
"""

import pickle
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DIR_DATA = Path(__file__).resolve().parents[1] / "data"


def parse_raman_0d_filename(name: str) -> dict:
    """Conditions from a filename like `19_200mbar_30slmH2_00slmAr_5slmCH4_500W.sif`.

    The `power` field in results.pkl is 1000 W for every run, also for the 500 W runs, so the
    power is taken from the filename instead.
    """
    diluent = "He" if "slmHe" in name else "Ar"
    return {
        "run_id": int(name.split("_")[0]),
        "position": "upstream" if "upstream" in name else "core",
        "power_W": int(re.search(r"_(\d+)W", name).group(1)),
        "pressure_mbar": int(re.search(r"_(\d+)mbar", name).group(1)),
        "H2_slm": int(re.search(r"(\d+)slmH2", name).group(1)),
        "Ar_slm": int(re.search(r"(\d+)slmAr", name).group(1)) if diluent == "Ar" else 0,
        "He_slm": int(re.search(r"(\d+)slmHe", name).group(1)) if diluent == "He" else 0,
        "CH4_slm": int(re.search(r"(\d+)slmCH4", name).group(1)),
    }


def export_raman_0d(dir_onedrive: Path):
    results = pickle.load(open(dir_onedrive / "Data/250116/results.pkl", "rb"))
    rows, spectra = [], []
    for name, res in results.items():
        conditions = parse_raman_0d_filename(name)
        assert conditions["pressure_mbar"] == res["pressure"] and conditions["H2_slm"] == res["slmH2"]
        rows.append({"file": name, **conditions, "T_K": res["T"], "T_err_K": res["T_err"]})

        # The fit is evaluated on the (corrected) wavelength axis of the processed data
        assert np.array_equal(res["data"]["lambda"], res["fit"]["lambda"])
        spectra.append(
            pd.DataFrame(
                {
                    "file": name,
                    "wavelength_nm": res["data"]["lambda"],
                    "I_meas": res["data"]["data"],
                    "I_fit": res["fit"]["data"],
                }
            )
        )

    # The keys of results.pkl are in the (arbitrary) order of the file system; keep that order,
    # because it sets the plotting order in Figure 7b and 11a.
    out = pd.DataFrame(rows)
    out.to_csv(DIR_DATA / "raman_0d_temperatures.csv", index=False, float_format="%.6g")
    pd.concat(spectra).to_csv(DIR_DATA / "raman_0d_spectra.csv", index=False, float_format="%.6g")
    print(f"Raman 0D: {len(out)} spectra")


def export_gc_pure_h2(dir_onedrive: Path):
    rows = []
    for pressure in [200, 300, 400, 500]:
        f = dir_onedrive / f"Contributions/H2_Ar/data/H2_Ar_GC/30H2_5CH4_{pressure}mBar_mi_20240417.xlsx"
        df = pd.read_excel(f, sheet_name="GC analysis", header=0).iloc[:, 1:]
        df = df[df["Power (W)"] != "BLANK"]
        for _, row in df.iterrows():
            rows.append(
                {
                    "pressure_mbar": pressure,
                    "power_W": int(row["Power (W)"]),
                    "H2_slm": row["H2 flow (slm)"],
                    "CH4_slm": row["CH4 flow (slm)"],
                    "X_CH4": row["XCH4 (%)"],
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(DIR_DATA / "gc_pure_h2.csv", index=False, float_format="%.6g")
    print(f"GC pure H2: {len(out)} samples")


def export_gc_dilution(dir_onedrive: Path):
    f = dir_onedrive / "Data/250116/H2_Ar_GC/Quenching experiment_2025_MLA_MR_averages.xlsx"
    df = pd.read_excel(f, sheet_name="Averages", header=0).iloc[:, 1:]
    df = df.dropna(subset=["Experiment"])
    out = pd.DataFrame(
        {
            "run_id": df["Experiment"].astype(int),
            "power_W": df["Absorbed power"],
            "pressure_mbar": df["Pressure set point (mbar)"],
            "pressure_measured_mbar": df["Pressure effective (mbar)"],
            "H2_slm": df["H2 flow (slm)"],
            "Ar_slm": df["Ar flow mixture (slm)"],
            "He_slm": df["He flow mixture (slm)"],
            "CH4_slm": df["CH4 flow (slm)"],
            "Ar_internal_standard_slm": df["Ar flow (slm)"],
            "X_CH4": df["XCH4 (%) with Ar"],
            "S_C2H2": df["S C2H2"],
            "S_C2H4": df["S C2H4"],
            "S_C2H6": df["S C2H6"],
        }
    )
    out.to_csv(DIR_DATA / "gc_dilution.csv", index=False, float_format="%.6g")
    print(f"GC dilution: {len(out)} runs")


def export_raman_2d(dir_onedrive: Path):
    # Contains toddler.data.spectrum.Spectrum objects
    from toddler.files.saving import load_from_pkl

    results = load_from_pkl(dir_onedrive / "Data/260529/processed_results.pkl")
    maps = []
    for name, res in results.items():
        power = int(re.search(r"_(\d+)W", name).group(1))
        X, Y = res["X"], res["Y"]
        maps.append(
            pd.DataFrame(
                {
                    "file": name,
                    "power_W": power,
                    "pressure_mbar": res["pressure"],
                    "H2_slm": res["slmH2"],
                    "Ar_slm": res["slmAr"],
                    "row": np.repeat(np.arange(X.shape[0]), X.shape[1]),
                    "col": np.tile(np.arange(X.shape[1]), X.shape[0]),
                    "x_mm": X.ravel(),
                    "y_mm": Y.ravel(),
                    "I_425": res["bp425"].sdata.ravel(),
                    "I_675": res["bp675"].sdata.ravel(),
                    "ratio_425_675": res["ratio"].sdata.ravel(),
                    "T_K": res["T"].ravel(),
                    "H2_density_mbar": res["H2_density"].sdata.ravel(),
                    "dissociation": res["diss"].ravel(),
                }
            )
        )
    out = pd.concat(maps)
    out.to_csv(DIR_DATA / "raman_2d_maps.csv", index=False, float_format="%.6g")
    print(f"Raman 2D: {len(maps)} maps of {X.shape[0]} x {X.shape[1]} pixels")


if __name__ == "__main__":
    dir_onedrive = Path(sys.argv[1])
    export_raman_0d(dir_onedrive)
    export_gc_pure_h2(dir_onedrive)
    export_gc_dilution(dir_onedrive)
    export_raman_2d(dir_onedrive)
