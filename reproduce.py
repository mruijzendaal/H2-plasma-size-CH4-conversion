"""Reproduce all figures of the paper.

    uv run reproduce.py            Figures 2-11, from the data in `data/` (about 30 s)
    uv run reproduce.py --model    Also re-run the plasma chemistry model behind Figure 10
                                   (about 1 min on a 12-core laptop). Uses GRI-Mech 3.0 for
                                   the neutral H/H2 chemistry unless the chemistry set of the
                                   paper is provided (see README.md).

Results are written to `output/`.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FIGURES = [
    "figures/fig02_raman_spectra.py",
    "figures/fig03_conversion_pure_h2.py",
    "figures/fig04_reaction_rates.py",
    "figures/fig05_fig09_2d_maps.py",
    "figures/fig07_argon_dilution.py",
    "figures/fig08_selectivity.py",
    "figures/fig10_neutral_vs_charged_chemistry.py",
    "figures/fig11_helium_dilution.py",
]
MODEL = [
    "model/neutral_vs_charged_chemistry.py",
]


def run(script):
    print(f"Running {script}...", flush=True)
    t0 = time.time()
    # Render without a display; `plt.show()` in the scripts is then a no-op
    env = os.environ | {"MPLBACKEND": "Agg", "PYTHONWARNINGS": "ignore:FigureCanvasAgg is non-interactive:UserWarning"}
    subprocess.run([sys.executable, ROOT / script], cwd=ROOT, env=env, check=True)
    print(f"  done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    for script in FIGURES + (MODEL if "--model" in sys.argv else []):
        run(script)
    print(f"All results are in {ROOT / 'output'}")
