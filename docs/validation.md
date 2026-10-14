# Validation and literature traceability

The source files carry no comments and no docstrings. Names say what the code does; this
document says where each formula comes from and which test proves it is still being applied.
A reviewer who wants to check the physics should read this table next to the textbook, not
the source.

## Primary source

Sadık Kakaç, Hongtan Liu, Anchasa Pramuanjaroenkij, *Heat Exchangers: Selection, Rating and
Thermal Design*. Every correlation below is taken from this book. Standards limits come from
TEMA (9th edition, 2007) and the FINA swimming pool certificate guide (February 2020).

**Chapter and section references are given at the level the author is confident of.
Equation numbers are marked `verify` where they should be checked against the specific
edition in use before this document is published as final.**

## Correlations

| Implementation | Quantity | Form as implemented | Source | Validity | Test |
|---|---|---|---|---|---|
| `tube_side_correlations.petukhov_smooth_tube_fanning_friction_factor` | Fanning friction factor, smooth tube | `f = (1.58 ln Re − 3.28)^−2` | Petukhov, via Kakaç ch. 3 `verify` | turbulent, smooth wall | `test_the_petukhov_friction_factor_falls_as_the_reynolds_number_rises` |
| `tube_side_correlations.gnielinski_nusselt_number` | tube side Nusselt number | `Nu = (f/2)(Re−1000)Pr / [1 + 12.7 (f/2)^½ (Pr^⅔ − 1)]` | Gnielinski, via Kakaç ch. 3 `verify` | `Re ≥ 1e4`, `0.5 ≤ Pr ≤ 2000` | `test_the_gnielinski_validity_window_is_reported_rather_than_enforced` |
| `tube_side_correlations.pressure_drop_pascal` | tube side pressure drop | `Δp = 4 f (L·Nₚ/dᵢ) · G²/(2ρ)` | Kakaç ch. 4 `verify` | same as the friction factor | `test_the_tube_side_pressure_drop_grew_because_the_original_used_the_shell_side_mass_flux` |
| `shell_side_correlations.equivalent_diameter_meters` | shell side equivalent diameter | square: `4(P² − πd²/4)/(πd)`; triangular: `4(P²√3/4 − πd²/8)/(πd/2)` | Kakaç ch. 8 `verify` | square and triangular layouts only | `test_the_two_pitch_layouts_give_different_equivalent_diameters` |
| `shell_side_correlations.crossflow_area_square_meters` | shell side crossflow area | `Aₛ = Dₛ · C · B / P` | Kakaç ch. 8 `verify` | single shell pass | regression suite |
| `shell_side_correlations.kern_heat_transfer_coefficient_watts_per_square_meter_kelvin` | shell side coefficient, Kern method | `h = 0.36 (k/Dₑ) Re^0.55 Pr^⅓ (μ/μ_w)^0.14` | Kern, via Kakaç ch. 8 `verify` | `2e3 ≤ Re ≤ 1e6` | `test_the_kern_validity_window_is_reported_rather_than_enforced` |
| `shell_side_correlations.kern_friction_factor` | shell side friction factor | `f = exp(0.576 − 0.19 ln Re)` | Kern, via Kakaç ch. 8 `verify` | as above | regression suite |
| `shell_side_correlations.kern_pressure_drop_pascal` | shell side pressure drop | `Δp = f G² (N_b + 1) Dₛ / (2 ρ Dₑ φ)` | Kern, via Kakaç ch. 8 `verify` | as above | `test_the_shell_side_pressure_drop_is_exactly_half_the_original_which_omitted_the_factor_two` |
| `thermal.referred_to_outside_area` | overall coefficient on the outside area | `U_o = [1/h_o + (r_o/r_i)/h_i + R_f + r_o ln(r_o/r_i)/k]^−1` | Kakaç ch. 2 `verify` | clean and fouled variants | `test_the_overall_coefficient_is_not_symmetric_in_the_two_film_coefficients` |
| `log_mean_temperature_difference.counterflow_log_mean_temperature_difference_kelvin` | counterflow LMTD | `ΔT_lm = (ΔT₁ − ΔT₂)/ln(ΔT₁/ΔT₂)` | Kakaç ch. 2 | both terminal differences positive | `test_the_log_mean_temperature_difference_lies_between_the_two_terminal_differences` |
| `thermal.shell_inner_diameter_meters` | preliminary shell diameter | `Dₛ = 0.637 √(CL/CTP) · √(A · PR² · d_o / L)` | Kakaç ch. 8 `verify` | preliminary sizing only | regression suite |
| `thermal.tube_count` | preliminary tube count | `N_t = 0.785 (CTP/CL) Dₛ² / (PR² d_o²)` | Kakaç ch. 8 `verify` | preliminary sizing only | regression suite |

## Constants that the author chose rather than derived

These are design inputs, not physics. A reviewer should challenge them, and the author should
confirm them against the course material and TEMA tables before treating this tool as final.

| Constant | Value | Where | Status |
|---|---|---|---|
| tube layout constant `CL`, square (90° / 45°) | 1.0 | `geometry.PitchLayout` | matches Kakaç |
| tube layout constant `CL`, triangular (30° / 60°) | 0.87 | `geometry.PitchLayout` | matches Kakaç |
| tube count calculation constant `CTP`, one pass | 0.93 | `geometry` | matches Kakaç |
| tube count calculation constant `CTP`, two pass | 0.90 | `geometry` | matches Kakaç |
| titanium alloy thermal conductivity | 25 W/m·K | `properties` | plausible; literature values for titanium alloys cluster near 7–22 W/m·K, so **this one deserves a second look** |
| stainless steel thermal conductivity | 15 W/m·K | `properties` | consistent with austenitic stainless steel, roughly 14–16 W/m·K |
| titanium alloy fouling resistance | 5.0e-05 m²·K/W | `properties` | author's choice; **confirm against the TEMA fouling table** |
| stainless steel fouling resistance | 9.0e-05 m²·K/W | `properties` | author's choice; **confirm against the TEMA fouling table** |
| LMTD correction factor `F` | 0.9 by default | `thermal` | was hard coded in the 2022 version; now an explicit, overridable input. For a single tube pass in pure counterflow `F = 1`; for multi pass it should be read from the `F` chart or computed. **Leaving it at 0.9 is an assumption, not a result.** |
| saturation temperature at 6 bar | 158.8 °C | `standards` | steam table value, used only for the single phase check |

## Standards limits

| Limit | Value | Source | Implementation |
|---|---|---|---|
| shell inner diameter / tube length | 0.0666 – 0.2 | TEMA | `standards.shell_diameter_to_tube_length_ratio_check` |
| pitch / tube outer diameter | 1.25 – 1.5 | TEMA | `standards.pitch_ratio_check` |
| pool water temperature | 25 – 28 °C | FINA | `standards.pool_temperature_check` |
| maximum working pressure, both sides | 6 bar | author's design envelope | `standards.pressure_drop_check` |

## Property data

`liquid_water_properties_table.csv` holds 33 rows of liquid water properties from 0 °C to
300 °C. The temperature spacing is deliberately non uniform: 5 K up to 100 °C, 10 K up to
200 °C, then 250 °C and 300 °C. Interpolation is linear between the two neighbouring rows,
found with `bisect`, so the non uniform spacing needs no special handling.

The table's `prandtl_number` column is not recomputed from `specific_heat · viscosity /
thermal_conductivity`; the tabulated value is used as given, because it is what the source
table states. The two agree to within 0.8 % across the whole table, and
`test_the_tabulated_prandtl_number_agrees_with_the_other_tabulated_columns` fails if a future
edit to the data file breaks that agreement by more than 1 %.

## Deliberate numerical differences from the 2022 implementation

The rewrite reproduces the 2022 results exactly except for the four items below. Each one is a
correction, each one is proven by a named test, and the 2022 behaviour is preserved in
`tests/reference/original_implementation_behaviour.json` so the comparison stays checkable.
The JSON was captured by `tests/reference/how_the_original_behaviour_was_captured.py`; the 2022
source it drives lives in git history at commit `067f66e`, so re-running the capture means
restoring `main.py` and `Water.csv` from that commit first.

### 1. The two film coefficients were swapped in the preliminary design

The 2022 code read the assumed tube side coefficient from the tube widget and then used it as
the **outside** film coefficient, and used the shell widget value as the **inside** one. The
rating step in the same program used the correct order, so the two halves of the tool
disagreed with each other and the manual iteration converged on the wrong answer whenever the
two assumed coefficients differed.

Effect: the suggested shell diameter and tube count change whenever the assumed tube side and
shell side coefficients are not equal, and are unchanged when they are equal.
Proof: `test_the_suggested_sizing_differs_only_because_the_original_swapped_the_two_film_coefficients`,
which reproduces the 2022 numbers exactly by deliberately re-applying the swap.

### 2. The shell side pressure drop was missing a factor of two

Kern's correlation divides by `2 ρ Dₑ φ`. The 2022 code divided by `ρ Dₑ φ`.

Effect: shell side pressure drop is now exactly half the 2022 value.
Proof: `test_the_shell_side_pressure_drop_is_exactly_half_the_original_which_omitted_the_factor_two`.

### 3. The tube side pressure drop used the shell side mass flux

The 2022 expression was `4 f Nₚ G_shell² / (dᵢ ρ)`. It used the shell side mass flux instead
of the tube side one, omitted the `L/dᵢ` factor, and omitted the division by two. It also took
the friction factor from a hand entered field rather than from the friction correlation
already being computed for Gnielinski.

Effect: the tube side pressure drop is now larger, by roughly an order of magnitude for
typical pool geometries. The hand entered friction factor field is gone.
Proof: `test_the_tube_side_pressure_drop_grew_because_the_original_used_the_shell_side_mass_flux`.

### 4. The shell side Prandtl number is read from the table instead of recomputed

The 2022 code formed `Pr = c_p μ / k` from the other tabulated columns. The rewrite uses the
tabulated `Pr` column. The two differ only by the rounding of the published table, which
changes the shell side coefficient by under 0.3 %.
Proof: `test_the_shell_side_heat_transfer_coefficient_changed_only_by_the_prandtl_rounding`.

## Known limitations

- Water only, liquid only, single phase. Nothing checks for boiling beyond the single
  temperature comparison against saturation at 6 bar.
- The Kern method is a preliminary method. It does not resolve bypass and leakage streams the
  way the Bell–Delaware method does, so shell side predictions carry real uncertainty.
- Fouling is a single lumped resistance on the outside surface, not separate tube side and
  shell side resistances.
- The LMTD correction factor is an input, not a computed result.
- This is a design aid for coursework and early sizing. It is not a substitute for a rating
  package or for a pressure vessel code calculation.
