# Chemistry set of the plasma model (Figure 10)

`H2_Ar.yaml` defines the H2/Ar plasma phase of the model in `src/h2_plasma_size/plasma_model.py`
(15 species, 68 reactions). It combines:

| File | Content | Source |
|------|---------|--------|
| `H2_Ar.yaml` | Phase definition; placeholder thermo of e, Arm, Arr, Ar(4p) | this work |
| `nasa_gas.yaml` (included with Cantera) | Thermo of Ar, Ar+, H, H+, H2, H2+, H- | McBride et al., NASA TM-4513 (1993) |
| `burcat_species.yaml` | Thermo of H3+, ArH+, ArH | Burcat and Ruscic, Third Millennium Thermochemical Database |
| `kemaneci/table3.yaml` | Argon ion and excited-state chemistry, incl. Ar2+ | Kemaneci et al., J. Phys. D 50, 245203 (2017), table III |
| `hjartarson/table3.yaml`, `hjartarson/table4.yaml` | H2/Ar interaction and hydrogen ion chemistry | Hjartarson et al., PSST 19, 065008 (2010), tables 3 and 4 |
| `togai2016_H_plasma.yaml` | Hydrogen/electron chemistry | Togai et al., Combust. Flame 164, 239 (2016) |
| `DLR_3.yaml` (not included, see below) | Neutral chemistry: of the declared species only `2 H + M <=> H2 + M` | Wang et al., Fuel 387, 134407 (2025) |

The rate coefficients were transcribed from the cited papers; see the description at the top
of each file.

## Neutral chemistry (DLR_3.yaml)

The results in the paper were obtained with the CH4 pyrolysis chemistry set of Wang et al.,
Fuel 387, 134407 (2025), https://doi.org/10.1016/j.fuel.2025.134407. Its license does not allow
redistribution, so it is not included in this repository. Of this set, the model uses only the
reactions among its declared species, which is the H recombination `2 H + M <=> H2 + M`.

Without it, the model uses the reactions of GRI-Mech 3.0 (`gri30.yaml`, included with Cantera)
among the declared species instead: `2 H + M <=> H2 + M` and `2 H + H2 <=> H2 + H2`. The model
then runs, but its results differ from those in the paper. Output files are labeled with the
chemistry set used (`_DLR_3` or `_gri30`).

To use the chemistry set of the paper, obtain the Cantera YAML file `DLR_3.yaml` from its
authors and place it in this directory. The results in the paper were obtained with the
version with SHA-1 checksum `26318d5a6e98414d136c8e930b8ceadcc77b5153` (`shasum DLR_3.yaml`).
(This is a different version than the one used for the CH4 coupling paper,
https://github.com/mruijzendaal/CH4-coupling-temperature-performance.)

Figure 4 does not use these files: it uses GRI-Mech 3.0 with high-temperature thermo
(`gri30_highT.yaml`, included with Cantera).
