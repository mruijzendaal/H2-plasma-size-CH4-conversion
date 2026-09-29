"""Shared plotting helpers, using the `wedme-plots` paper style."""

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import numpy as np
import wedme

from h2_plasma_size import DIR_OUTPUT

# Most figures are half the single-column width of the journal
SIZE_HALF_COLUMN = (wedme.PAPER_HSCW, wedme.PAPER_DH * 0.8)
# Half the single-column width in golden ratio. Equivalent to `wedme.figure.paper_hscw_hsch()`
# in later versions of wedme-plots.
SIZE_HALF_COLUMN_GOLDEN = (wedme.PAPER_HSCW, wedme.PAPER_HSCW / wedme.GOLDEN_RATIO)


def new_figure(figsize=SIZE_HALF_COLUMN, labelpad=1.0):
    """A new figure in the paper style.

    The label padding of the paper style was changed several times in the (unreleased) version
    of wedme-plots that made the figures: `axes.labelpad` was 3 in December 2025, the
    matplotlib default of 4 in spring 2026, and 1 from 16 June 2026 on. Each figure script
    passes the value that was in use when the figure in the paper was made.
    """
    fig = wedme.figure.paper(figsize=figsize)
    plt.rcParams["axes.labelpad"] = labelpad
    return fig


def savefig(name: str, **kwargs):
    """Save the current figure as `output/<name>.pdf` and `.png`, like `wedme.savefig` in the
    original analysis. Note that `wedme.savefig` ignores extra keyword arguments (such as
    `bbox_inches`) when saving to more than one format; this is kept for identical output."""
    wedme.savefig(DIR_OUTPUT / name, **kwargs)


def plot_double_axis(ax1, ax2, x1, x2):
    """Show a second x axis `ax2` (on top) that maps `x1` on `ax1` linearly to `x2`."""
    forward = lambda x: np.interp(x, x1, x2)
    backward = lambda x: np.interp(x, x2, x1)

    xlims = [np.min(x1), np.max(x1)]

    ax1.set_xlim(*xlims)
    ax1.xaxis.set_tick_params(top=False)
    ax1.grid(True)

    ax2.set_xlim([forward(xi) for xi in xlims])
    ax2.grid(False)
    ax2.set_xscale(wedme.scale.CustomFuncScale(functions=[forward, backward][::-1], max_ticks=7))


def twiny(x1, x2, ax1=None, ax2=None, **kwargs):
    """Like `plot_double_axis`, but with at most 4 ticks on the second axis. Copied from
    `wedme.util.twiny` in later versions of wedme-plots."""
    if ax1 is None:
        ax1 = plt.gca()
    if ax2 is None:
        ax2 = ax1.twiny(**kwargs)

    forward = lambda x: np.interp(x, x1, x2)
    backward = lambda x: np.interp(x, x2, x1)

    xlims = [np.min(x1), np.max(x1)]

    ax1.set_xlim(*xlims)
    ax1.xaxis.set_tick_params(top=False)

    ax2.set_xlim([forward(xi) for xi in xlims])
    ax2.grid(False)
    ax2.set_xscale(wedme.scale.CustomFuncScale(functions=[forward, backward][::-1], max_ticks=4))

    plt.sca(ax1)

    return ax1, ax2


def lighten_color(color, amount=0.5):
    """Lighten `color` by moving it a fraction `amount` towards white."""
    c = mc.cnames.get(color, color)
    c = mc.to_rgb(c)
    return [x + (1 - x) * amount for x in c]
