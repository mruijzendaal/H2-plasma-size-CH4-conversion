# %% [markdown]
# # Figure 7: CH4 conversion and core gas temperature versus argon dilution
# 1000 W, 30 slm H2 + Ar through the plasma, 5 slm CH4 quench, 100, 200 and 500 mbar.
# (a) CH4 conversion from GC. The error bars are 2 sigma, for a relative uncertainty of 3%.
# (b) Gas temperature in the plasma core from 0D Raman. The error bars are 3 sigma of the
#     fit; the dashed lines are linear extrapolations of the last two points.
#
# Output: `output/fig7a_conversion_vs_argon.pdf`, `output/fig7b_temperature_vs_argon.pdf`

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy

from h2_plasma_size.data import load_gc_dilution, load_raman_0d
from h2_plasma_size.plotting import new_figure, plot_double_axis, savefig

# %% [markdown]
# ## (a) CH4 conversion

# %%
df = load_gc_dilution()

# Pure argon (0:30 slm H2:Ar) at 500 mbar gave no CH4 conversion; this run is not in the
# spreadsheet with the GC results, and was added by hand.
new_row = pd.DataFrame({"Ar_slm": [30], "X_CH4": [0], "pressure_mbar": [500]})
df = pd.concat([df, new_row], ignore_index=True)
df = df.sort_values(["Ar_slm", "pressure_mbar"])

df_500mbar = df[df["pressure_mbar"] == 500]
df_200mbar = df[(df["pressure_mbar"] == 200) & (df["He_slm"] == 0) & (df["power_W"] > 550)]
df_100mbar = df[df["pressure_mbar"] == 100]

# Made in spring 2026, when the paper style had the matplotlib default `axes.labelpad: 4`
new_figure(labelpad=4)
for p, df_p in zip([100, 200, 500], [df_100mbar, df_200mbar, df_500mbar]):
    l = plt.plot(df_p["Ar_slm"] / 30 * 100, 100 * df_p["X_CH4"], "s-", label=f"{p} mbar")
    plt.errorbar(df_p["Ar_slm"] / 30 * 100, 100 * df_p["X_CH4"], yerr=2 * 100 * df_p["X_CH4"] * 0.03, fmt="none", ecolor=l[0].get_color())
plt.legend()
plt.ylabel("$CH_4$ conversion [%]")

# Secondary x axis with the argon flow in slm
ax1 = plt.gca()
plt.xlabel("Argon flow [%]")
plt.xlim(0, 101)
ax2 = plt.gca().twiny()
plot_double_axis(ax1, ax2, ax1.get_xlim(), 30 * np.array(ax1.get_xlim()) / 100)
plt.xlabel("Argon flow [slm]")

plt.ylim(0, 20)
plt.ylabel("$CH_4$ conversion [%]")
savefig("fig7a_conversion_vs_argon")
plt.show()

# %% [markdown]
# ## (b) Core gas temperature

# %%
raman = load_raman_0d()

# Made in December 2025, when the paper style had `axes.labelpad: 3`
new_figure(labelpad=3)
for pressure in [100, 200, 500]:
    runs = raman[
        (raman["pressure_mbar"] == pressure)
        & (raman["position"] == "core")
        & (raman["power_W"] == 1000)
        & (raman["He_slm"] == 0)
        # Left out in the original analysis: the 25:5 slm H2:Ar runs, and 10:20 at 500 mbar
        # (see data/README.md)
        & (raman["Ar_slm"] != 5)
        & ~((raman["Ar_slm"] == 20) & (pressure == 500))
    ]
    slmH2 = runs["H2_slm"].to_numpy()
    T_vals = runs["T_K"].to_numpy()
    T_err = runs["T_err_K"].to_numpy()
    slmAr = 30 - slmH2

    idx_sort = np.argsort(slmAr)
    slmAr = slmAr[idx_sort]
    T_vals = T_vals[idx_sort]
    T_err = T_err[idx_sort]

    l = plt.errorbar(slmAr * 100 / 30, T_vals, yerr=3 * T_err, fmt="s-", label=f"{pressure} mbar")

    # Extrapolate linearly to 100% argon
    slmAr_last = np.max(slmAr)
    slmAr_extrap = np.linspace(slmAr_last, 30, 20)
    T_extrap = scipy.interpolate.interp1d(slmAr, T_vals, kind="linear", fill_value="extrapolate")(slmAr_extrap)
    plt.plot(slmAr_extrap * 100 / 30, T_extrap, "--", color=l[0].get_color())

plt.ylim(2500, 4500)
plt.legend()
ax1 = plt.gca()
plt.xlabel("Argon flow [%]")
plt.ylabel("Temperature [K]")

plt.xlim(0, 101)
ax2 = plt.gca().twiny()
plot_double_axis(ax1, ax2, ax1.get_xlim(), 30 * np.array(ax1.get_xlim()) / 100)

plt.xlabel("Argon flow [slm]")
savefig("fig7b_temperature_vs_argon")
plt.show()
