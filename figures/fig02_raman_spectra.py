# %% [markdown]
# # Figure 2: Raman spectra at low and high temperature
# Measured (normalized) vibrational Stokes Raman spectrum of H2 and the fitted synthetic
# spectrum, at 200 mbar, 30 slm H2, 5 slm CH4:
# (a) 1000 W, in the mixing zone downstream of the plasma (file `..._upstream.sif`);
# (b) 500 W, in the core of the plasma.
# The uncertainty in the legend is 3 sigma of the fit.
#
# Output: `output/fig2a_raman_spectrum_738K.pdf`, `output/fig2b_raman_spectrum_2627K.pdf`

# %%
import matplotlib.pyplot as plt

from h2_plasma_size.data import load_raman_0d, load_raman_0d_spectrum
from h2_plasma_size.plotting import new_figure, savefig

raman = load_raman_0d().set_index("file")

# %%
panels = {
    "fig2a_raman_spectrum_738K": "01_200mbar_30slmH2_0slmAr_5slmCH4_1000W_upstream.sif",
    "fig2b_raman_spectrum_2627K": "19_200mbar_30slmH2_00slmAr_5slmCH4_500W.sif",
}

for name, file in panels.items():
    run = raman.loc[file]
    spectrum = load_raman_0d_spectrum(file)
    stderr_str = f"{3 * run['T_err_K']:.0f}"

    # Made in spring 2026, when the paper style had the matplotlib default `axes.labelpad: 4`
    new_figure(labelpad=4)
    plt.plot(spectrum["wavelength_nm"], spectrum["I_meas"], "r.", label="Data")
    plt.plot(spectrum["wavelength_nm"], spectrum["I_fit"], "k-", label=rf"Fit ($T={run['T_K']:.0f} \pm {stderr_str}$)")
    plt.xlim(662, 686)
    plt.xlabel("Wavelength [nm]")
    plt.ylabel(r"Intensity [$\endash$]")
    plt.legend()
    savefig(name)
    plt.show()
