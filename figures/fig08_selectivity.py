# %% [markdown]
# # Figure 8: C2 selectivities versus CH4 conversion
# The argon dilution scans of Figure 7a, at 100, 200 and 500 mbar (lighter colors for lower
# pressures). The error bars are 2 sigma, for relative uncertainties of 2.5% (C2H2),
# 3.4% (C2H4) and 5.5% (C2H6).
#
# Output: `output/fig8_selectivity_vs_conversion.pdf`

# %%
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wedme

from h2_plasma_size.data import load_gc_dilution
from h2_plasma_size.plotting import lighten_color, new_figure, savefig

# %%
# The same selection as in Figure 7a
df = load_gc_dilution()
new_row = pd.DataFrame({"Ar_slm": [30], "X_CH4": [0], "pressure_mbar": [500]})
df = pd.concat([df, new_row], ignore_index=True)
df = df.sort_values(["Ar_slm", "pressure_mbar"])

df_500mbar = df[df["pressure_mbar"] == 500]
df_200mbar = df[(df["pressure_mbar"] == 200) & (df["He_slm"] == 0) & (df["power_W"] > 550)]
df_100mbar = df[df["pressure_mbar"] == 100]

# %%
colors = {}
err_rel = {
    "C2H2": 0.025,
    "C2H4": 0.034,
    "C2H6": 0.055,
}

# Made in spring 2026, when the paper style had the matplotlib default `axes.labelpad: 4`
new_figure(figsize=(wedme.PAPER_SCW * 0.55, wedme.PAPER_DH * 0.8), labelpad=4)
for j, species in enumerate(["C2H2", "C2H4", "C2H6"]):
    label = re.subn(r"(?<=[C|H])([^CH]+)", r"$_{\1}$", species)[0]
    for i, p in enumerate(reversed([df_100mbar, df_200mbar, df_500mbar])):
        alpha = np.interp(i, [0, 2], [0, 0.6])
        # Selectivity as a function of conversion; 500 mbar in the next color of the color
        # cycle, lower pressures in lighter versions of it
        c = colors.get(species, None)
        if c is not None:
            c = lighten_color(c, alpha)
        l = plt.plot(100 * p["X_CH4"], 100 * p[f"S_{species}"], "s-", label=label if c is None else None, color=c, zorder=2 + j)[0]
        if c is None:
            c = l.get_color()
            colors[species] = c
        plt.errorbar(100 * p["X_CH4"], 100 * p[f"S_{species}"], yerr=2 * 100 * p[f"S_{species}"] * err_rel[species], fmt="none", ecolor=c, zorder=2 - j)

        if species == "C2H2" and i == 2:
            plt.text(df_100mbar["X_CH4"].iloc[-1] * 100 + 0.25, df_100mbar[f"S_{species}"].iloc[-1] * 100, "100 mbar", c=c, va="bottom")
        elif species == "C2H2" and i == 1:
            plt.text(df_200mbar["X_CH4"].iloc[-1] * 100 + 0.25, df_200mbar[f"S_{species}"].iloc[-1] * 100 - 1, "200 mbar", c=c, va="top")
        elif species == "C2H2" and i == 0:
            plt.text(df_500mbar["X_CH4"].iloc[-2] * 100 - 0.2, df_500mbar[f"S_{species}"].iloc[-2] * 100 - 1, "500 mbar", c=c, va="top", ha="right")

plt.ylim(0, 70)
plt.ylabel("Selectivity [%]")

plt.xlim(0)
plt.xlabel("CH$_4$ conversion [%]")
plt.legend(loc="lower right", bbox_to_anchor=(0.975, 0.15))
savefig("fig8_selectivity_vs_conversion")
plt.show()
