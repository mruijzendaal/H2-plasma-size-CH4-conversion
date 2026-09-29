"""Fit the 0D Raman spectra of the January 2025 campaign: produces `results.pkl`.

Provenance only: transcribed from `exp_fit.ipynb` of the original analysis (cells 0, 2 and 4),
which produced `Data/250116/results.pkl` on 26 February 2025. It needs the raw spectra
(Andor `.sif`, available from the author on request) and the in-house packages labctl, ramlab
and toddler (see README.md). It is not needed to reproduce the figures.

The lineshape and the higher orders of the wavelength correction are fitted once to a spectrum
with a high signal (06: 500 mbar, 30 slm H2), and then fixed for all other spectra, of which
only the temperature, amplitude and wavelength offset are fitted.

Note: `power` is stored as 1000 W for every spectrum, also for the 500 W runs (19, 20, 27);
export_processed_data.py takes the power from the filename instead.
"""

import pickle
from pathlib import Path

import toddler
from labctl.experiments import SimpleLaserExperiment
from ramlab.fit.modifiers import MeasurementSpectrum, WavelengthAxisCorrection
from ramlab.fit.recipe import SingleMoleculeFitRecipe
from ramlab.molecules.H2 import H2
from ramlab.molecules.polarisation import Polarisation
from ramlab.simulate import RawBinnedSimulationMethod
from ramlab.simulate.linespreadfunction import Voigt

# The directory with the raw data of the campaign
f_dir = Path("Data/250116")

# The frame indices (signal/background) are the same for all acquisitions
f_pkl = f_dir / "01_200mbar_30slmH2_0slmAr_5slmCH4_1000W_idx.pkl"

_, _, s30H2 = SimpleLaserExperiment.postprocess(f_dir / "06_500mbar_30slmH2_00slmAr_5slmCH4_1000W.sif", f_pkl)

# %% Fit recipe: vibrational Stokes transitions of H2
M = H2
transitions = M.get_all_transitions(laser_wavelength=532e-9).filter(dv=1)

lineshape = Voigt(w_g=0.1, w_l=0.1)
wavelength_correction = WavelengthAxisCorrection(2)

fit = SingleMoleculeFitRecipe(
    molecule=M,
    transitions=transitions,
    polarisation=Polarisation.COMBINED,
    lineshape=lineshape,
    modifiers=[wavelength_correction],
    simulation_method=RawBinnedSimulationMethod(N_bin=10),
)

# Fit one of the spectra that has very good signal
fit.prepare()
fitresults = fit.fit(MeasurementSpectrum(s30H2))

# Apply the resulting fit parameters (lineshape, wavelength correction) to the other spectra
fit.apply_parameters(
    fitresults.fit_params,
    vary_l=False,
    vary_g=False,  # Fix the linewidths
    vary_wl=[True, False, False, False],  # Fix the wavelength correction other than 0th order
)

# %% Fit all spectra
results = {}
for diluent in ["Ar", "He"]:
    for f, pars in toddler.files.filenames.glob(f_dir, "*.sif", r"\d{2}_(\d+)mbar", r"(\d+)slmH2", rf"(\d+)slm{diluent}"):
        if None in pars:
            continue
        pressure, slmH2, slm_diluent = pars

        if "afterglow" in f.name or "oes" in f.name:
            continue

        print(f"Processing {f.name}")
        fg, bg, s = SimpleLaserExperiment.postprocess(f, f_pkl)

        fit.prepare()
        fitresults = fit.fit(MeasurementSpectrum(s)).to_dict()

        results[f.name] = {
            "power": 1000,
            "pressure": pressure,
            "slmH2": slmH2,
            f"slm{diluent}": slm_diluent,
            "slmCH4": 5,
            "slmArRef": "1 slm always added after the reactor",
            **fitresults,
        }

pickle.dump(results, open(f_dir / "results.pkl", "wb"))
