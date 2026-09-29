# %% [markdown]
# # Figure 11: core gas temperature and CH4 conversion versus helium dilution
# 1000 W, 200 mbar, 30 slm H2 + He through the plasma, 5 slm CH4 quench.
# (a) Gas temperature in the plasma core from 0D Raman. The error bars are 3 sigma of the
#     fit; the dashed line is a linear extrapolation of the last two points.
# (b) CH4 conversion from GC.
#
# Output: `output/fig11a_temperature_vs_helium.pdf`, `output/fig11b_conversion_vs_helium.pdf`

# %%
import matplotlib.pyplot as plt
import numpy as np
import scipy

from h2_plasma_size.data import load_gc_dilution, load_raman_0d
from h2_plasma_size.plotting import new_figure, plot_double_axis, savefig

# %% [markdown]
# ## (a) Core gas temperature

# %%
raman = load_raman_0d()

# Made in December 2025, when the paper style had `axes.labelpad: 3`
new_figure(labelpad=3)
pressure = 200
runs = raman[
    (raman["pressure_mbar"] == pressure)
    & (raman["position"] == "core")
    & (raman["power_W"] == 1000)
    # The helium dilution scan, and pure H2
    & ~((raman["He_slm"] == 0) & (raman["Ar_slm"] != 0))
]
slmH2 = runs["H2_slm"].to_numpy()
T_vals = runs["T_K"].to_numpy()
T_err = runs["T_err_K"].to_numpy()
slmHe = 30 - slmH2

idx_sort = np.argsort(slmHe)
slmHe = slmHe[idx_sort]
T_vals = T_vals[idx_sort]
T_err = T_err[idx_sort]

l = plt.errorbar(slmHe * 100 / 30, T_vals, yerr=3 * T_err, fmt="s-", label=f"{pressure} mbar")

# Extrapolate linearly to 100% helium
slmHe_last = np.max(slmHe)
slmHe_extrap = np.linspace(slmHe_last, 30, 20)
T_extrap = scipy.interpolate.interp1d(slmHe, T_vals, kind="linear", fill_value="extrapolate")(slmHe_extrap)
plt.plot(slmHe_extrap * 100 / 30, T_extrap, "--", color=l[0].get_color())

plt.ylim(2500, 4500)
ax1 = plt.gca()
plt.xlabel("Helium flow [%]")
plt.ylabel("Temperature [K]")

plt.xlim(0, 101)
ax2 = plt.gca().twiny()
plot_double_axis(ax1, ax2, ax1.get_xlim(), 30 * np.array(ax1.get_xlim()) / 100)

plt.xlabel("Helium flow [slm]")
savefig("fig11a_temperature_vs_helium")
plt.show()

# %% [markdown]
# ## (b) CH4 conversion

# %%
df = load_gc_dilution()
df_200mbar = df[(df["pressure_mbar"] == 200) & (df["Ar_slm"] == 0) & (df["power_W"] == 1000)]
df_200mbar = df_200mbar.sort_values("He_slm")

# Made in spring 2026, when the paper style had the matplotlib default `axes.labelpad: 4`
new_figure(labelpad=4)
plt.plot(df_200mbar["He_slm"] / 30 * 100, 100 * df_200mbar["X_CH4"], "s-", label="200 mbar")
plt.ylabel("$CH_4$ conversion [%]")

# Secondary x axis with the helium flow in slm
ax1 = plt.gca()
plt.xlabel("Helium flow [%]")
plt.xlim(0, 101)
ax2 = plt.gca().twiny()
plot_double_axis(ax1, ax2, ax1.get_xlim(), 30 * np.array(ax1.get_xlim()) / 100)
plt.xlabel("Helium flow [slm]")

plt.ylim(0, 20)
plt.ylabel("$CH_4$ conversion [%]")
savefig("fig11b_conversion_vs_helium")
plt.show()
