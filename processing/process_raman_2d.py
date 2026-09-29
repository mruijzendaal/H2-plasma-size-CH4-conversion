"""Process the 2D Raman (spectral imaging) measurements of 29 May 2026: produces
`processed_results.pkl` and the maps of Figures 5 and 9.

Provenance only: transcribed from `260529/final.ipynb` of the original analysis (cells 0, 1
and 3), which produced `Data/260529/processed_results.pkl` on 19 June 2026. It needs the raw
image stacks (Andor `.sif`, 0.4-0.5 GB each, available from the author on request), the
acquisition index files (`2s_16min.pkl`, `2s_21min.pkl`), the calibration curve
`2d_vib_calibration_260608.pkl`, and the in-house packages labctl and toddler (see README.md).
It is not needed to reproduce the figures.

Method (Del Cont-Bernard et al., JQSRT 328, 109145, 2024): the vibrational anti-Stokes
(bandpass 425 nm) and Stokes (bandpass 675 nm) Raman signals are imaged. Their ratio gives the
gas temperature through a calibration curve; the Stokes signal, relative to that of H2 at room
temperature, gives the H2 density. The dissociation degree follows from the H2 density,
assuming that the H/H2 stoichiometry is preserved and the ideal gas law.

Note: the calibration file was regenerated on 26 September 2026, after these results were
produced, with a finer temperature grid (10 K instead of 50 K). With the new file, the
temperatures differ by at most 30 K from those in the paper.
"""

from pathlib import Path

import numpy as np
import toddler
from labctl.experiments import Raman2DExperiment
from toddler.data.spectrum import Spectrum
from toddler.files.saving import load_from_pkl

f_base = Path("Data/260529")

# Acquisition configurations
pkl_16m = f_base / "2s_16min.pkl"
pkl_21m = f_base / "2s_21min.pkl"

# Vacuum data
signals_vac, info_vac = Raman2DExperiment.postprocess(f_data=f_base / "2s_16min_vac.sif", f_pickle=pkl_16m)

# Room temperature data: 100 mbar H2
signals_rt, info_rt = Raman2DExperiment.postprocess(f_data=f_base / "2s_16min_roomtemp_100mbar_15H2_0Ar.sif", f_pickle=pkl_16m)
rt_pressure = 100


def signal_to_intensity(s: Spectrum, info: dict) -> Spectrum:
    """Signal per laser pulse (30 Hz)."""
    pulses_per_frame = info["T_exposure"] // (1 / 30) + 1
    return s / pulses_per_frame


def signals_to_intensity(signals: dict, info: dict) -> dict:
    return {k: tuple([signal_to_intensity(s[i], info) for i in range(3)]) for k, s in signals.items()}


def process(signals, info):
    """Crop, bin 4x4 pixels, and subtract the background frames."""
    sig, bg, _ = signals

    sig = sig[:, 48:416, :]
    bg = bg[:, 48:416, :]

    N_bin = 4
    sig_binned = sig.c.bin2((N_bin, N_bin, sig.shape[-1]))
    bg_binned = bg.c.bin2((N_bin, N_bin, bg.shape[-1]))
    sig_corr = (sig_binned - bg_binned).squeeze()
    sig_corr.data = sig_corr.data.T

    return sig_corr, bg_binned


def vac_correct(signals, vac_signals):
    # The vacuum correction was disabled in the final analysis: a copy of the signals
    return {k: tuple([s[0].c, s[1].c, s[2].c]) for k, s in signals.items()}


signals_vac_intensity = signals_to_intensity(signals_vac, info_vac)
signals_rt_intensity = signals_to_intensity(signals_rt, info_rt)
vac_corrected_rt = vac_correct(signals_rt_intensity, signals_vac_intensity)
rt_675, _ = process(vac_corrected_rt["bp675"], info_rt)
rt_425, _ = process(vac_corrected_rt["bp425"], info_rt)

# %% Signal maps of every condition
results = {}
for path, (slmH2, slmAr, pressure, exptime) in toddler.files.filenames.glob(f_base, "*0W.sif", r"(\d+)H2", r"(\d+)Ar", r"(\d+)mbar", r"(\d+)min"):
    pkl = {16: pkl_16m, 21: pkl_21m}[exptime]
    if slmH2 == 10:
        continue

    signals, info = Raman2DExperiment.postprocess(f_data=f_base / path.name, f_pickle=pkl)
    signals_intensity = signals_to_intensity(signals, info)
    vac_corrected_signals = vac_correct(signals_intensity, signals_vac_intensity)

    sig_675, bg_675 = process(vac_corrected_signals["bp675"], info)
    sig_425, bg_425 = process(vac_corrected_signals["bp425"], info)

    # As in the original analysis: shift the Stokes image of the 30:0 measurement by one
    # (binned) pixel
    if slmH2 == 30:
        sig_675.data = np.roll(sig_675.data, 1, axis=0)
    ratio = sig_425 / sig_675

    results[path.name] = {
        "slmH2": slmH2,
        "slmAr": slmAr,
        "pressure": pressure,
        "exptime": exptime,
        "ratio": ratio,
        "bp425": sig_425,
        "bp675": sig_675,
        "bg425": vac_corrected_signals["bp425"][1].c.median(axis=2),
        "bg675": vac_corrected_signals["bp675"][1].c.median(axis=2),
    }

# %% Temperature, H2 density and dissociation degree
calcurve = load_from_pkl(f_base / "2d_vib_calibration_260608.pkl")
mycalcurve = calcurve["QE_corrected"]["sig425/sig675"][0, 0, :]

# The pixel-based, calibration-curve-corrected sensitivity of the Stokes signal
H2_sensitivity_675 = (rt_675 / rt_pressure) / calcurve["QE_corrected"]["sig675"][0, 0, 0]  # [counts/s/mbar-H2 at room temperature]

M = 13.4e-3 * 4 * 2 * 100 / 80  # Pixel size * binning * magnification [mm]
x = np.arange(rt_675.shape[1]) * M
x -= x.mean()
y = np.arange(rt_675.shape[0]) * M
y -= y.mean()
X, Y = np.meshgrid(x, y)
T_roomtemp = 288  # K


def get_Tmap(ratio):
    """Temperature of the calibration curve point closest to each pixel's signal ratio."""
    origshape = ratio.shape
    ratio_flat = ratio.flatten()
    idmin = np.argmin(np.abs(ratio_flat - mycalcurve[:, np.newaxis]), axis=0)
    T = calcurve["T"].squeeze()[idmin].reshape(origshape)
    bp425cs = calcurve["QE_corrected"]["sig425"][0, 0, :][idmin].reshape(origshape)
    bp675cs = calcurve["QE_corrected"]["sig675"][0, 0, :][idmin].reshape(origshape)
    return T, bp425cs, bp675cs


for name, res in results.items():
    T, bp425cs, bp675cs = get_Tmap(res["ratio"].sdata)
    pressure, slmH2, slmAr = res["pressure"], res["slmH2"], res["slmAr"]

    H2_intensity_675 = res["bp675"] / bp675cs  # [counts/s]
    H2_density = H2_intensity_675 / H2_sensitivity_675  # [mbar-H2]
    H2_frac = H2_density * (T / T_roomtemp) / pressure
    H2_frac_expected = slmH2 / (slmH2 + slmAr)
    H2_frac_relative = H2_frac / H2_frac_expected
    H_frac_relative = 1 - H2_frac_relative
    diss = H_frac_relative / (2 * H2_frac_relative + H_frac_relative)

    if pressure != 500:
        continue

    # Mask pixels with too little Stokes signal
    T = T.astype(float)
    mask_bad = H2_intensity_675.sdata < 24
    T[mask_bad] = np.nan
    diss.data[mask_bad] = np.nan

    results[name] = {
        **res,
        "T": T,
        "bp425cs": bp425cs,
        "bp675cs": bp675cs,
        "H2_density": H2_density,
        "H2_frac": H2_frac.sdata,
        "H2_frac_relative": H2_frac_relative.sdata,
        "diss": diss.sdata,
        "X": X,
        "Y": Y,
    }

toddler.files.saving.save_to_pkl(results, f_base / "processed_results.pkl")
