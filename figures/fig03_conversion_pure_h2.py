# %% [markdown]
# # Figure 3: CH4 conversion versus power, for pure H2
# 30 slm H2 through the plasma, 5 slm CH4 quench, 200-500 mbar. Every point is the mean of
# the GC samples at that power; the error bars are their standard deviation.
#
# Output: `output/fig3_conversion_pure_h2.pdf`

# %%
import matplotlib.pyplot as plt

from h2_plasma_size.data import load_gc_pure_h2
from h2_plasma_size.plotting import new_figure, savefig

gc = load_gc_pure_h2()

# %%
# Made in spring 2026, when the paper style had the matplotlib default `axes.labelpad: 4`
new_figure(labelpad=4)

# Skip the first color of the color cycle
plt.plot([], [], label=None)
for pressure in [200, 500, 400, 300]:
    df = gc[gc["pressure_mbar"] == pressure]

    # Average measurements with equal power. Put their standard deviation in the error bars.
    df = df.groupby("power_W").agg({"X_CH4": ["mean", "std"]}).reset_index()
    df.columns = ["power_W", "X_CH4", "X_CH4_std"]

    l = plt.plot(df["power_W"], 100 * df["X_CH4"], "s-", label=f"{pressure:.0f} mbar")
    plt.errorbar(df["power_W"], 100 * df["X_CH4"], yerr=100 * df["X_CH4_std"], fmt="none", ecolor=l[0].get_color(), capsize=0, zorder=10 - pressure / 100)

# Order the legend by pressure
handles, labels = plt.gca().get_legend_handles_labels()
idx = [0, 3, 2, 1]
handles = [handles[i] for i in idx]
labels = [labels[i] for i in idx]

plt.legend(handles, labels).set_zorder(1e5)
plt.ylabel("$CH_4$ conversion [%]")
plt.xlabel("Power [W]")
plt.ylim(0)
plt.xlim(300)
savefig("fig3_conversion_pure_h2")
plt.show()
