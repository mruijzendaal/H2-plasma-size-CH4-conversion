# %% [markdown]
# # Model results of Figure 10: neutral versus charged-particle chemistry
# H radical mole fraction in the 0D H2/Ar plasma model (src/h2_plasma_size/plasma_model.py)
# at 500 mbar, for electron densities of 0 (in practice 10 m-3) to 1e20 m-3. The gas
# temperature and argon fraction are varied together, along the trend of Figure 7b:
# from 3100 K at 0% Ar to 4600 K at 100% Ar.
#
# Output: `output/model/neutral_vs_charged_chemistry_<mechanism>.csv`, where <mechanism> is
# DLR_3 (the chemistry set of the paper) or gri30 (the fallback, see mechanism/README.md).
# The stored results in `data/model/neutral_vs_charged_chemistry.csv` were made with DLR_3.

# %%
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from tqdm import tqdm

from h2_plasma_size import DIR_OUTPUT
from h2_plasma_size.plasma_model import get_steady_state_ne, mechanism_name

ne = np.array([1e1, 1e17, 1e18, 1e19, 1e20])
Tg = np.linspace(3100, 4600, 60)
X_ar = np.linspace(0, 1, len(Tg))


def run_case(args):
    ne_i, Tg_j, X_ar_j = args
    result = {"ne_target_m3": ne_i, "Tg_K": Tg_j, "X_Ar_inlet": X_ar_j}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            state, Te, ne_found = get_steady_state_ne(ne_i, Tg=Tg_j, X_ar=X_ar_j)
    except Exception:
        # Cases that fail are left out (NaN), as in the original analysis
        return result
    return {
        **result,
        "Te_eV": Te,
        "ne_m3": ne_found,
        "production_H_kmol_m3_s": state.net_production_rates[state.species_index("H")],
        "X_H": state.X[state.species_index("H")],
        "X_H2": state.X[state.species_index("H2")],
        "density_kmol_m3": state.density_mole,
    }


if __name__ == "__main__":
    cases = [(ne_i, Tg_j, X_ar_j) for ne_i in ne for Tg_j, X_ar_j in zip(Tg, X_ar)]
    print(f"Chemistry set: {mechanism_name()}")
    with ProcessPoolExecutor() as pool:
        rows = list(tqdm(pool.map(run_case, cases), total=len(cases)))

    out = pd.DataFrame(rows)
    f = DIR_OUTPUT / "model" / f"neutral_vs_charged_chemistry_{mechanism_name()}.csv"
    f.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(f, index=False, float_format="%.8g")
    print(f"{out['X_H'].notna().sum()} of {len(out)} cases succeeded; written to {f}")
