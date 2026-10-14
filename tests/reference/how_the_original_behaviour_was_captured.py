import json
import os
import pathlib
import sys
import tkinter
import tkinter.ttk

ORIGINAL_IMPLEMENTATION_DIRECTORY = (
    pathlib.Path(__file__).resolve().parents[2] / "docs" / "legacy-2022-implementation"
)
sys.path.insert(0, str(ORIGINAL_IMPLEMENTATION_DIRECTORY))
os.chdir(ORIGINAL_IMPLEMENTATION_DIRECTORY)

tkinter.Tk.mainloop = lambda self, *a, **k: None

CAPTURED_LABELS = []


class RecordingLabel:
    def __init__(self, *args, **kwargs):
        if "text" in kwargs:
            CAPTURED_LABELS.append(kwargs["text"])

    def pack(self, *args, **kwargs):
        return self


from tkinter import messagebox

import main

main.ttk.Label = RecordingLabel

DIALOGS = []


def _capture(kind):
    def handler(title=None, message=None, *args, **kwargs):
        DIALOGS.append({"kind": kind, "title": title, "message": str(message)})
        return "ok"

    return handler


for module in (messagebox, main.messagebox, main.tk.messagebox):
    module.showinfo = _capture("info")
    module.showwarning = _capture("warning")
    module.showerror = _capture("error")


def set_entry(entry, value):
    entry.delete(0, "end")
    entry.insert(0, str(value))


CASES = [
    {
        "name": "olimpik_havuz_titanyum_tek_gecis",
        "tube_inlet": 13.0,
        "tube_outlet": 28.0,
        "shell_inlet": 80.0,
        "tube_flow": 40.0,
        "shell_flow": 20.0,
        "outer_diameter_mm": 19.0,
        "inner_diameter_mm": 16.0,
        "length_m": 6.0,
        "material": "Titanium Alloy",
        "passes": "One Pass",
        "layout_value": 2,
        "pitch_ratio": "1.25",
        "h_tube_assumed": "3000",
        "h_shell_assumed": "3000",
        "shell_diameter_m": 0.9,
        "tube_count": 700,
        "baffle_spacing_m": 0.45,
        "pitch_layout": "Triangular Pitch",
        "tube_friction_factor": 0.005,
    },
    {
        "name": "yuksek_debi_paslanmaz_iki_gecis",
        "tube_inlet": 20.0,
        "tube_outlet": 30.0,
        "shell_inlet": 70.0,
        "tube_flow": 60.0,
        "shell_flow": 25.0,
        "outer_diameter_mm": 25.0,
        "inner_diameter_mm": 21.0,
        "length_m": 8.0,
        "material": "Stainless Steel",
        "passes": "Two Pass",
        "layout_value": 1,
        "pitch_ratio": "1.50",
        "h_tube_assumed": "4000",
        "h_shell_assumed": "2500",
        "shell_diameter_m": 1.2,
        "tube_count": 500,
        "baffle_spacing_m": 0.6,
        "pitch_layout": "Square Pitch",
        "tube_friction_factor": 0.006,
    },
    {
        "name": "kucuk_boru_dusuk_debi",
        "tube_inlet": 25.0,
        "tube_outlet": 28.0,
        "shell_inlet": 60.0,
        "tube_flow": 15.0,
        "shell_flow": 5.0,
        "outer_diameter_mm": 12.0,
        "inner_diameter_mm": 10.0,
        "length_m": 4.0,
        "material": "Titanium Alloy",
        "passes": "One Pass",
        "layout_value": 1,
        "pitch_ratio": "1.30",
        "h_tube_assumed": "5000",
        "h_shell_assumed": "5000",
        "shell_diameter_m": 0.5,
        "tube_count": 300,
        "baffle_spacing_m": 0.3,
        "pitch_layout": "Square Pitch",
        "tube_friction_factor": 0.004,
    },
    {
        "name": "sinir_yuz_derece_sicak_taraf",
        "tube_inlet": 15.0,
        "tube_outlet": 27.0,
        "shell_inlet": 95.0,
        "tube_flow": 35.0,
        "shell_flow": 12.0,
        "outer_diameter_mm": 19.0,
        "inner_diameter_mm": 15.0,
        "length_m": 7.0,
        "material": "Stainless Steel",
        "passes": "One Pass",
        "layout_value": 2,
        "pitch_ratio": "1.25",
        "h_tube_assumed": "2000",
        "h_shell_assumed": "6000",
        "shell_diameter_m": 1.0,
        "tube_count": 850,
        "baffle_spacing_m": 0.5,
        "pitch_layout": "Triangular Pitch",
        "tube_friction_factor": 0.005,
    },
]

PROPERTY_FIELDS = ("Density", "Cp", "Viscosity", "K", "Pr", "Alpha")


def series_to_dict(series):
    return {field: float(series[field]) for field in PROPERTY_FIELDS}


results = {}

for case in CASES:
    DIALOGS.clear()
    CAPTURED_LABELS.clear()
    record = {"inputs": case, "dialogs": [], "outputs": {}, "errors": []}

    try:
        set_entry(main.Entry1, case["tube_inlet"])
        main.buttonfunction1()
        set_entry(main.Entry2, case["tube_outlet"])
        main.buttonfunction2()
        set_entry(main.Entry3, case["shell_inlet"])
        main.buttonfunction3()
        set_entry(main.Entry5, case["tube_flow"])
        main.buttonfunction5()
        set_entry(main.Entry6, case["shell_flow"])
        main.buttonfunction6()

        main.runprocess1()
        record["outputs"]["cold_bulk_temperature_celsius"] = float(main.Tbulk)
        record["outputs"]["cold_bulk_properties"] = series_to_dict(main.Cold_properties)

        main.runprocess2()
        record["outputs"]["heat_duty_watts"] = float(main.Qdot)
        record["outputs"]["shell_outlet_temperature_celsius"] = float(main.THotOut)
        record["outputs"]["hot_bulk_temperature_celsius"] = float(main.TbulkHot)
        record["outputs"]["hot_bulk_properties"] = series_to_dict(main.Hot_properties)

        set_entry(main.Entry8, case["outer_diameter_mm"])
        main.buttonfunction8()
        set_entry(main.Entry9, case["inner_diameter_mm"])
        main.buttonfunction9()
        set_entry(main.Entry10, case["length_m"])
        main.buttonfunction10()
        main.choose_material.set(case["material"])
        main.choose_pass.set(case["passes"])
        main.var.set(case["layout_value"])
        main.pitch_ratio.set(case["pitch_ratio"])
        main.htube_it.set(case["h_tube_assumed"])
        main.hshell_it.set(case["h_shell_assumed"])

        main.runprocess3()
        record["outputs"]["preliminary"] = {
            "fouled_overall_coefficient": float(main.Uf),
            "clean_overall_coefficient": float(main.Uc),
            "corrected_log_mean_temperature_difference": float(main.lmtd),
            "fouled_area_square_meters": float(main.Af),
            "clean_area_square_meters": float(main.Ac),
            "suggested_shell_diameter_meters": float(main.Ds),
            "suggested_tube_count": float(main.Nt),
        }

        for entry, value, button in (
            (main.Entry11, case["tube_inlet"], main.buttonfunction11),
            (main.Entry12, case["tube_outlet"], main.buttonfunction12),
            (main.Entry13, case["shell_inlet"], main.buttonfunction13),
            (main.Entry14, main.THotOut, main.buttonfunction14),
            (main.Entry15, case["tube_flow"], main.buttonfunction15),
            (main.Entry16, case["shell_flow"], main.buttonfunction16),
            (main.Entry17, case["inner_diameter_mm"], main.buttonfunction17),
            (main.Entry18, case["outer_diameter_mm"], main.buttonfunction18),
            (main.Entry19, case["length_m"], main.buttonfunction19),
            (main.Entry20, case["baffle_spacing_m"], main.buttonfunction20),
            (main.Entry21, case["shell_diameter_m"], main.buttonfunction21),
            (main.Entry22, case["tube_count"], main.buttonfunction22),
            (main.Entry23, case["tube_friction_factor"], main.buttonfunction23),
        ):
            set_entry(entry, value)
            button()

        main.choose_pitchLayout.set(case["pitch_layout"])
        main.choose_materiald.set(case["material"])
        main.choose_passd.set(case["passes"])
        main.pitch_ratiod.set(case["pitch_ratio"])

        main.runprocess4()
        record["outputs"]["rating"] = {
            "tube_side_coefficient": float(main.h_td),
            "shell_side_coefficient": float(main.h_sd),
            "shell_side_reynolds_number": float(main.Re_sd),
            "tube_flow_area_square_meters": float(main.Atpd),
            "shell_equivalent_diameter_meters": float(main.Ded),
            "shell_crossflow_area_square_meters": float(main.Asd),
            "shell_mass_flux": float(main.Gsd),
            "tube_clearance_meters": float(main.Cd),
            "pitch_size_meters": float(main.pitch_sized),
        }

        CAPTURED_LABELS.clear()
        main.runprocess5()
        record["outputs"]["final_report_text"] = CAPTURED_LABELS[-1] if CAPTURED_LABELS else None

    except Exception as exception:
        record["errors"].append(f"{type(exception).__name__}: {exception}")

    record["dialogs"] = list(DIALOGS)
    results[case["name"]] = record

print(json.dumps(results, indent=2, ensure_ascii=False))
