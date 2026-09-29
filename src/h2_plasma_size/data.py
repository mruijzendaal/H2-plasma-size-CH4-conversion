"""Load the measurement data in `data/` (see data/README.md for the columns)."""

import numpy as np
import pandas as pd

from h2_plasma_size import DIR_DATA


def load_raman_0d() -> pd.DataFrame:
    """Gas temperatures from the 0D Raman spectra, one row per spectrum."""
    return pd.read_csv(DIR_DATA / "raman_0d_temperatures.csv")


def load_raman_0d_spectrum(file: str) -> pd.DataFrame:
    """Measured and fitted Raman spectrum behind one row of `load_raman_0d()`."""
    spectra = pd.read_csv(DIR_DATA / "raman_0d_spectra.csv")
    return spectra[spectra["file"] == file]


def load_gc_pure_h2() -> pd.DataFrame:
    """GC results of the power scans with pure H2, one row per GC sample."""
    return pd.read_csv(DIR_DATA / "gc_pure_h2.csv")


def load_gc_dilution() -> pd.DataFrame:
    """GC results of the Ar and He dilution scans, one row per run (averaged over samples)."""
    return pd.read_csv(DIR_DATA / "gc_dilution.csv")


def load_raman_2d(pressure_mbar: int, H2_slm: int, Ar_slm: int) -> dict[str, np.ndarray]:
    """2D Raman maps of one condition, as 2D arrays indexed [row, col] (y, x)."""
    maps = pd.read_csv(DIR_DATA / "raman_2d_maps.csv")
    m = maps[(maps["pressure_mbar"] == pressure_mbar) & (maps["H2_slm"] == H2_slm) & (maps["Ar_slm"] == Ar_slm)]
    shape = (m["row"].max() + 1, m["col"].max() + 1)
    m = m.sort_values(["row", "col"])
    return {c: m[c].to_numpy().reshape(shape) for c in m.columns if c not in ["file", "row", "col"]}
