# %% [markdown]
# # Figure 10: H radical mole fraction with and without charged-particle chemistry
# Results of the 0D H2/Ar plasma model at 500 mbar (model/neutral_vs_charged_chemistry.py),
# for several electron densities. The gas temperature (bottom axis) and argon fraction (top
# axis) are varied together. "n_e = 0" is a run at 10 m-3.
#
# Output: `output/fig10_neutral_vs_charged_chemistry.pdf`

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from h2_plasma_size import DIR_DATA
from h2_plasma_size.plotting import new_figure, savefig, twiny

model = pd.read_csv(DIR_DATA / "model" / "neutral_vs_charged_chemistry.csv")

# %%
new_figure()

# The results for 1e20 m-3 were calculated but are not shown
for ne_i in [1e1, 1e17, 1e18, 1e19]:
    run = model[model["ne_target_m3"] == ne_i].sort_values("Tg_K")

    ne_str = f"{ne_i:.0e}".replace("1e+", "10^{") + "}"
    ne_str = rf"$\mathrm{{n_e = {ne_str}\ m^{{-3}}}}$"
    fmt = ""
    zorder = 1

    if ne_i < 1e10:
        ne_str = r"$\mathrm{n_e = 0}$"
        fmt = "k:"
        zorder = 2

    plt.plot(run["Tg_K"], 100 * run["X_H"], fmt, label=ne_str, zorder=zorder)

plt.xlabel("Gas temperature [K]")
plt.ylabel(r"H mole fraction [%]")
plt.xlim(3000, 4500)

Tg, X_ar = run["Tg_K"].to_numpy(), run["X_Ar_inlet"].to_numpy()
_, ax2 = twiny(Tg, X_ar * 100)
ax2.set_xlabel("Argon mole fraction [%]", labelpad=2.5)
ax2.set_xticks([0, 25, 50, 75, 100])

plt.legend()

plt.ylim(0, 60)
savefig("fig10_neutral_vs_charged_chemistry")
plt.show()
