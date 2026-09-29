"""Zero-dimensional H2/Ar plasma model (Section 2.4 of the paper).

A constant-pressure volume at a fixed gas temperature, inlet composition and electron
temperature, integrated for 100 ms. The electron temperature is iterated until the electron
density reaches a desired value (`get_steady_state_ne`).
"""

import warnings
from functools import cache

import cantera as ct
import numpy as np

from h2_plasma_size import DIR_MECHANISM

N_AVOGADRO = 6e23  # [1/mol], as in the original analysis


def mechanism_name() -> str:
    """`DLR_3` if the neutral chemistry set of the paper is present in `mechanism/`, otherwise
    `gri30` (GRI-Mech 3.0, included with Cantera). See mechanism/README.md."""
    return "DLR_3" if (DIR_MECHANISM / "DLR_3.yaml").exists() else "gri30"


@cache
def _mechanism_yaml() -> str:
    ct.add_directory(str(DIR_MECHANISM))
    text = (DIR_MECHANISM / "H2_Ar.yaml").read_text()
    if mechanism_name() == "gri30":
        text = text.replace("- DLR_3.yaml/reactions:", "- gri30.yaml/reactions:")
    return text


def new_gas() -> ct.Solution:
    return ct.Solution(yaml=_mechanism_yaml())


def get_steady_state(Te, Tg, X_ar):
    """State after 100 ms at electron temperature `Te` [eV], gas temperature `Tg` [K] and argon
    fraction `X_ar` of the H2/Ar mixture, at 500 mbar."""
    gas = new_gas()
    alpha = 1e-6
    gas.TPX = Tg, 500e2, {"Ar": X_ar, "H2": 1 - X_ar}
    gas.X = {**gas.mole_fraction_dict(), "e": alpha, "H2+": alpha * (1 - X_ar), "Ar+": alpha * X_ar}
    gas.mean_electron_energy = 3 / 2 * Te
    gas.update_electron_energy_distribution()

    r = ct.ConstPressureReactor(gas, energy="off", clone=False, volume=2e-6)

    sim = ct.ReactorNet([r])
    sim.verbose = False
    sim.initialize()

    sim.advance(100e-3)

    return r.phase


def electron_density(state) -> float:
    """[1/m3]"""
    return state.X[state.species_index("e")] * state.density_mole * N_AVOGADRO * 1e3


def get_steady_state_ne(
    ne_target,
    Tg,
    X_ar,
    te_bounds=(0.05, 8.0),
    rtol=0.1,
    max_iter=30,
    max_expand=12,
    expand_factor=1.8,
    min_te=1e-3,
):
    """Find Te such that electron density matches ne_target.

    The solver works in log-space because ne(Te) is strongly nonlinear.

    Returns
    -------
    state : cantera.Solution
        Steady-state solution at converged Te.
    Te : float
        Electron temperature in eV.
    ne : float
        Converged electron density in 1/m^3.
    """
    if ne_target <= 0:
        raise ValueError("ne_target must be positive")

    te_low, te_high = te_bounds
    if te_low <= 0 or te_high <= 0 or te_low >= te_high:
        raise ValueError("te_bounds must be positive and te_low < te_high")

    target_log = np.log10(ne_target)

    def solve_and_get_ne(te):
        state = get_steady_state(te, Tg, X_ar)
        ne = electron_density(state)
        if ne <= 0 or not np.isfinite(ne):
            raise RuntimeError(f"Invalid ne={ne} at Te={te}")
        return state, ne, np.log10(ne)

    # 1) Expand bounds until target is bracketed in log-space.
    state_low, ne_low, log_low = solve_and_get_ne(te_low)
    state_high, ne_high, log_high = solve_and_get_ne(te_high)

    bracketed = (log_low - target_log) * (log_high - target_log) <= 0

    for _ in range(max_expand):
        if bracketed:
            break

        if log_low < target_log and log_high < target_log:
            te_low, state_low, ne_low, log_low = te_high, state_high, ne_high, log_high
            te_high *= expand_factor
            state_high, ne_high, log_high = solve_and_get_ne(te_high)
        else:
            te_high, state_high, ne_high, log_high = te_low, state_low, ne_low, log_low
            te_low = max(min_te, te_low / expand_factor)
            state_low, ne_low, log_low = solve_and_get_ne(te_low)

        bracketed = (log_low - target_log) * (log_high - target_log) <= 0

    if not bracketed:
        # Out of achievable bracket: return the closest boundary in log-space.
        if abs(log_low - target_log) <= abs(log_high - target_log):
            boundary_state, boundary_te, boundary_ne = state_low, te_low, ne_low
        else:
            boundary_state, boundary_te, boundary_ne = state_high, te_high, ne_high

        warnings.warn(
            f"ne_target {ne_target:.3e} is outside the reachable bracket after Te expansion. "
            f"Returning boundary solution at Te={boundary_te:.4g} eV, "
            f"ne={boundary_ne:.3e} 1/m^3. "
            f"Final bracket: Te=({te_low:.4g}, {te_high:.4g}), "
            f"ne=({ne_low:.3e}, {ne_high:.3e})",
            RuntimeWarning,
        )
        return boundary_state, boundary_te, boundary_ne

    # 2) Bisection in Te with log-space error metric.
    log_tol = np.log10(1 + rtol)
    best = (None, None, np.inf)  # (state, Te, abs_log_error)

    for _ in range(max_iter):
        te_mid = 0.5 * (te_low + te_high)
        state_mid, ne_mid, log_mid = solve_and_get_ne(te_mid)
        abs_log_err = abs(log_mid - target_log)

        if abs_log_err < best[2]:
            best = (state_mid, te_mid, abs_log_err)

        if abs_log_err <= log_tol:
            return state_mid, te_mid, ne_mid

        if (log_low - target_log) * (log_mid - target_log) <= 0:
            te_high, state_high, ne_high, log_high = te_mid, state_mid, ne_mid, log_mid
        else:
            te_low, state_low, ne_low, log_low = te_mid, state_mid, ne_mid, log_mid

    # Return best point even if strict tolerance was not reached.
    best_state, best_te, _ = best
    return best_state, best_te, electron_density(best_state)
