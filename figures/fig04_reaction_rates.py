# %% [markdown]
# # Figure 4: volumetric reaction rates of CH4 conversion and H2 dissociation
# Net reaction rates at 500 mbar, calculated with GRI-Mech 3.0 (high-temperature thermo,
# `gri30_highT.yaml`, included with Cantera), for a given temperature and composition:
# (a) CH4 conversion in the quench zone, 30:5 H2:CH4 with 1% or 10% of the H2 dissociated;
# (b) H2 dissociation in the plasma zone, 30:30 H2:Ar with 0%, 1% or 10% of the H2 dissociated.
# The grey line is the reaction rate needed to convert 1 slm in a volume of 100 cm3.
#
# Output: `output/fig4a_reaction_rates_CH4.pdf`, `output/fig4b_reaction_rates_H2.pdf`
#
# The code that added the grey line was not saved; it is reconstructed here from the figure
# in the paper.

# %%
import re

import matplotlib.pyplot as plt
import numpy as np
import wedme
from matplotlib.lines import Line2D

import cantera as ct
from h2_plasma_size.chemistry import SLM_TO_KMOL_PER_S, format_reaction, gri30_highT, reverse_reaction
from h2_plasma_size.plotting import new_figure, savefig

# Reaction rate needed to convert 1 slm in 100 cm3 [kmol/m3/s]
RATE_1SLM_100CM3 = SLM_TO_KMOL_PER_S / 100e-6


def plot_reference_rate(x_text, ha):
    """Grey line and label. The label positions were measured from the figures in the paper."""
    plt.axhline(RATE_1SLM_100CM3, color="k", alpha=0.5)
    plt.text(x_text, RATE_1SLM_100CM3 / 1.4, "1 slm, 100 cm$^3$", color="k", alpha=0.5, ha=ha, va="top")


def plot_legends(H2_sim_methods):
    legend_elements = [Line2D([0], [0], color="k", linestyle=ls) for (_, ls, _) in H2_sim_methods]
    l1 = wedme.unique_legend(bbox_to_anchor=(0, 1.04), loc="lower left", borderaxespad=0)
    plt.legend(
        legend_elements,
        [label for (_, _, label) in H2_sim_methods],
        bbox_to_anchor=(1.025, 1.04),
        loc="lower right",
        borderaxespad=0,
        title="H:$H_2$",
    )
    plt.gca().add_artist(l1)


# %% [markdown]
# ## (a) CH4 conversion

# %%
gas = gri30_highT("C", "H")

T = np.linspace(300, 2000, 100)
# (H mole fraction of the hydrogen, line style, label)
H2_sim_methods = [(0.01, "-", "1%"), (0.1, "--", "10%")]

new_figure()
plot_colors = {}
for XH, linestyle, _ in H2_sim_methods:
    solarr = ct.SolutionArray(gas)
    for Ti in T:
        gas.TPX = Ti, 500e2, {"CH4": 5, "H2": 30 * (1 - XH), "H": 30 * XH}
        solarr.append(gas.state, T=Ti)

    # Every reaction that converts CH4 to CH3 (or vice versa)
    for i, reaci in enumerate(solarr.reactions()):
        mul = 1
        eq = reaci.equation
        reactants, products = list(reaci.reactants.keys()), list(reaci.products.keys())

        if not ("CH4" in reactants and "CH3" in products) and not ("CH4" in products and "CH3" in reactants):
            continue
        elif "CH4" in products:
            mul = -1
            eq = reverse_reaction(reaci.equation)

        ratei = solarr.net_rates_of_progress[:, i]
        if not np.any(np.abs(ratei) > 1e-8):
            continue

        if eq not in plot_colors:
            l = plt.plot(T, np.abs(ratei), linestyle, label=format_reaction(eq))
            plot_colors[eq] = l[0].get_color()
        else:
            plt.plot(T, ratei * mul, linestyle=linestyle, label=format_reaction(eq), color=plot_colors[eq])

plot_reference_rate(596, ha="left")

plt.yscale("log")
plt.ylim(1e-9, 1e4)
plt.xlim(np.min(T), np.max(T))
plt.xlabel("Temperature [K]")
plt.ylabel("Reaction rate [$kmol/m^3/s$]")
plot_legends(H2_sim_methods)
plt.subplots_adjust(top=0.3)
savefig("fig4a_reaction_rates_CH4")
plt.show()

# %% [markdown]
# ## (b) H2 dissociation

# %%
gas = gri30_highT("H", "Ar")
idx_H2 = gas.species_index("H2")

T = np.linspace(2000, 4500, 100)
H2_sim_methods = [(0.00, "-", "0%"), (0.01, "--", "1%"), (0.1, ":", "10%")]

new_figure()
plot_colors = {}
for XH, linestyle, _ in H2_sim_methods:
    solarr = ct.SolutionArray(gas)
    for Ti in T:
        gas.TPX = Ti, 500e2, {"Ar": 30, "H2": 30 * (1 - XH), "H": 30 * XH}
        solarr.append(gas.state, T=Ti)

    # The reactions that dissociate H2 with a third body other than M (i.e. H2 itself). The
    # plotted rate is the net production rate of H2 by all reactions.
    for i, reaci in enumerate(solarr.reactions()):
        mul = 1
        eq = reaci.equation
        reactants, products = list(reaci.reactants.keys()), list(reaci.products.keys())

        if not ("H2" in reactants and "H" in products) and not ("H2" in products and "H" in reactants):
            continue
        elif "M" in reaci.equation:
            continue
        elif "H2" in products:
            mul = -1
            eq = reverse_reaction(reaci.equation)

        ratei = solarr.net_production_rates[:, idx_H2]
        if not np.any(np.abs(ratei) > 1e-8):
            continue
        eq = re.sub(r"\+\sH2", r"\,(+\,M)", eq)

        if eq not in plot_colors:
            l = plt.plot(T, np.abs(ratei), linestyle, label=format_reaction(eq))
            plot_colors[eq] = l[0].get_color()
        else:
            plt.plot(T, ratei * mul, linestyle=linestyle, label=format_reaction(eq), color=plot_colors[eq])

plot_reference_rate(4358, ha="right")

plt.yscale("log")
plt.ylim(1e-5, 1e1)
plt.xlim(np.min(T), np.max(T))
plt.xlabel("Temperature [K]")
plt.ylabel("Reaction rate [$kmol/m^3/s$]")
plt.yticks([1e-5, 1e-3, 1e-1, 1e1])
plt.xticks([2000, 3000, 4000])
plot_legends(H2_sim_methods)
plt.subplots_adjust(top=0.3)
savefig("fig4b_reaction_rates_H2")
plt.show()
