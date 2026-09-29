# %% [markdown]
# # Figures 5 and 9: 2D maps of gas temperature and H2 dissociation degree
# From the 2D Raman (spectral imaging) measurements in the plasma core at 500 mbar:
# Figure 5 for 30:0 slm H2:Ar, Figure 9 for 15:15 slm H2:Ar. Pixels with too little H2 Raman
# signal are grey (masked). The color scale of the temperature spans the 5th to 95th
# percentile; that of the dissociation degree 0 to the 99.5th percentile.
#
# Output: `output/fig5{a,b}_*_30H2_0Ar.pdf`, `output/fig9{a,b}_*_15H2_15Ar.pdf`

# %%
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import wedme

from h2_plasma_size.data import load_raman_2d
from h2_plasma_size.plotting import SIZE_HALF_COLUMN_GOLDEN, new_figure, savefig


def format_axes():
    plt.gca().set_facecolor((0.75,) * 3)
    plt.xticks(np.arange(-8, 8.1, 4))
    plt.yticks(np.arange(-5, 5.1, 2.5))
    plt.xlabel("Axial position [mm]")
    plt.ylabel("Transverse position [mm]")


# %%
for fig, H2_slm, Ar_slm in [(5, 30, 0), (9, 15, 15)]:
    m = load_raman_2d(pressure_mbar=500, H2_slm=H2_slm, Ar_slm=Ar_slm)
    extent = (m["x_mm"].min(), m["x_mm"].max(), m["y_mm"].min(), m["y_mm"].max())
    suffix = f"{H2_slm}H2_{Ar_slm}Ar"

    # (a) Gas temperature; masked pixels transparent, so that the grey background shows
    new_figure(figsize=SIZE_HALF_COLUMN_GOLDEN)
    cmap = mpl.colormaps["inferno"].with_extremes(bad=("grey", 0))
    wedme.util.imshow(m["T_K"], 5, 95, cmap=cmap, extent=extent, origin="lower")
    plt.gca().set_facecolor((0.75,) * 3)
    wedme.colorbar(label="Temperature [K]")
    format_axes()
    savefig(f"fig{fig}a_temperature_map_{suffix}")
    plt.show()

    # (b) H2 dissociation degree
    new_figure(figsize=SIZE_HALF_COLUMN_GOLDEN)
    wedme.imshow(m["dissociation"] * 100, vmin=0, vmax_percentile=99.5, cmap=mpl.colormaps["Blues"], extent=extent, origin="lower")
    format_axes()
    wedme.colorbar(label="Dissociation degree [%]")
    savefig(f"fig{fig}b_dissociation_map_{suffix}")
    plt.show()
