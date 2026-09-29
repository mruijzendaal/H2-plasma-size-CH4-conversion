"""Helpers for the reaction rate calculations with Cantera."""

import re
import tempfile
from pathlib import Path

import cantera as ct

# 1 standard liter per minute (273.15 K, 1 atm), in kmol/s
SLM_TO_KMOL_PER_S = ct.one_atm * 1e-3 / (ct.gas_constant * 273.15) / 60


def filter_mechanism(input_file: Path, output_file: Path, elements: list[str]):
    """Remove all elements except `elements` from a Cantera YAML mechanism, together with all
    species and reactions containing them. The order of the species and reactions is kept.
    Adapted from `collomech.filter.filter_yaml` (https://github.com/Brightsite-Plasmalab/collomech)."""
    import yaml
    from yamlcore import CoreDumper, CoreLoader  # YAML 1.2 support, see pyyaml issue #116

    with open(input_file) as stream:
        mechanism = yaml.load(stream, Loader=CoreLoader)

    elements_new = [k for k in mechanism["phases"][0]["elements"] if k in elements]
    mechanism["phases"][0]["elements"] = elements_new

    species_orig = mechanism["species"]
    species = [s["name"] for s in species_orig if not set(s["composition"]) - set(elements_new)]
    species_remove = {s["name"] for s in species_orig} - set(species)
    mechanism["phases"][0]["species"] = species
    mechanism["species"] = [s for s in species_orig if s["name"] in species]

    mechanism["reactions"] = [
        r for r in mechanism["reactions"] if not set(r["equation"].split()) & species_remove
    ]
    for r in mechanism["reactions"]:
        if r.get("type", "") in ["three-body", "falloff"] and "efficiencies" in r:
            r["efficiencies"] = {k: v for k, v in r["efficiencies"].items() if k in species}

    with open(output_file, "w") as f:
        yaml.dump(mechanism, f, Dumper=CoreDumper, default_flow_style=False)


def gri30_highT(*elements: str) -> ct.Solution:
    """GRI-Mech 3.0 with high-temperature thermo (`gri30_highT.yaml`, included with Cantera),
    reduced to the species and reactions that contain only `elements`."""
    input_file = Path(ct.__file__).parent / "data" / "gri30_highT.yaml"
    with tempfile.TemporaryDirectory() as d:
        output_file = Path(d) / f"gri30_highT_filtered_{''.join(sorted(elements))}.yaml"
        filter_mechanism(input_file, output_file, list(elements))
        return ct.Solution(str(output_file))


def format_reaction(reaction: str) -> str:
    """Format a Cantera reaction equation for a plot label. Copied from
    `pyreactorkit.display.format_reaction` (https://github.com/mruijzendaal/PyReactorKit)."""
    reaction_label = reaction.replace("<=>", r"\Leftrightarrow")
    reaction_label = reaction_label.replace("=>", r"\Rightarrow")
    reaction_label = reaction_label.replace("<=", r"\Leftarrow")
    # Replace electron with e^-
    reaction_label = re.sub(r"(\s|^)(e)(\s|$)", r"e^-", reaction_label)
    # Superscript charges
    reaction_label = re.sub(r"([a-zA-Z0-9]+)([-+])", r"\1^\2", reaction_label)
    # Replace numbers preceded by letters with subscripts
    reaction_label = re.sub(r"([a-zA-Z]+)([0-9]+)", r"\1_{\2}", reaction_label)
    # Replace third body + M with (+ M)
    reaction_label = re.sub(r"(\s|^)(\+)(\s|$)(M)", r"\,(+ M)", reaction_label)
    return rf"$\mathrm{{{reaction_label}}}$"


def reverse_reaction(reaction: str) -> str:
    """Swap the reactants and products of a Cantera reaction equation. Copied from
    `pyreactorkit.display.reverse_reaction`."""
    reaction = re.sub(r"(.+)\s(<=>|=>|<=)\s(.+)", r"\3 \2 \1", reaction)
    reaction = re.sub(
        r"(?<!<|>)(<=|=>)(?!<|>)",
        lambda m: "<=" if m.group(1) == "=>" else "=>",
        reaction,
    )
    return reaction
