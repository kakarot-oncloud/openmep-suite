"""
Australia Regional Electrical Adapter
Standards: AS/NZS 3008.1.1:2017 (Cable Selection) / AS/NZS 3000:2018 (Wiring Rules)
Design conditions: 40°C air ambient, 25°C ground (AS/NZS reference)
Earthing: MEN (Multiple Earthed Neutral) — TN-CS system
"""

import numpy as np
from ..base_adapter import BaseElectricalAdapter

SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630]
MCB_RATINGS = [6, 10, 16, 20, 25, 32, 40, 50, 63]
MCCB_RATINGS = [63, 80, 100, 125, 160, 200, 250, 320, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200]

# AS/NZS 3008 Table 3 & 7 — X-90 XLPE Cu multicore, 40°C air / 25°C ground
X90_RATINGS = {
    "col_6":  [14, 19, 26, 33, 45, 61, 79, 97, 117, 149, 181, 210, 240, 276, 326, 376, 443, 595],   # conduit in wall
    "col_9":  [26, 35, 46, 57, 77, 101, 130, 159, 193, 247, 298, 345, 393, 449, 529, 608, 712, 950], # direct buried
    "col_13": [22, 30, 39, 49, 66, 86, 110, 135, 164, 210, 253, 293, 333, 380, 447, 514, 604, 808], # buried in conduit
    "col_22": [22, 30, 39, 49, 65, 87, 111, 136, 165, 211, 256, 296, 338, 388, 459, 529, 622, 834], # clipped flat
    "col_23": [24, 33, 43, 54, 73, 98, 126, 155, 187, 240, 290, 337, 385, 442, 522, 602, 708, 949], # on tray
    "col_24": [24, 33, 44, 55, 74, 99, 128, 157, 190, 244, 295, 342, 391, 449, 530, 610, 718, 963], # free air touching
}

# V-75 PVC Cu multicore
V75_RATINGS = {
    "col_6":  [12, 17, 22, 29, 39, 53, 68, 83, 100, 127, 153, 177, 202, 230, 272, 313, 368, 492],
    "col_9":  [23, 31, 41, 51, 68, 89, 114, 139, 167, 213, 256, 296, 337, 386, 454, 522, 611, 818],
    "col_13": [19, 26, 34, 43, 58, 76, 97, 118, 142, 181, 218, 252, 287, 328, 386, 444, 521, 697],
    "col_22": [19, 26, 34, 43, 58, 77, 99, 121, 147, 187, 226, 262, 300, 344, 407, 469, 551, 739],
    "col_23": [21, 28, 38, 47, 63, 84, 108, 132, 160, 205, 247, 286, 327, 375, 444, 511, 601, 805],
}

# Ambient temp correction X-90 (reference 40°C air)
X90_CA_TEMPS = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
X90_CA_FACTORS = [1.15, 1.11, 1.07, 1.03, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76]
X90_CA_TEMPS_GND = [10, 15, 20, 25, 30, 35, 40, 45, 50]
X90_CA_FACTORS_GND = [1.10, 1.07, 1.04, 1.00, 0.96, 0.92, 0.87, 0.82, 0.77]

V75_CA_TEMPS = [20, 25, 30, 35, 40, 45, 50, 55]
V75_CA_FACTORS = [1.20, 1.15, 1.10, 1.05, 1.00, 0.94, 0.87, 0.79]

# Route spacing factors (Table 22) — cables flat touching
CG_NUM = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 20]
CG_FLAT_TOUCH = [1.00, 0.80, 0.70, 0.65, 0.60, 0.57, 0.54, 0.52, 0.50, 0.45, 0.41, 0.38]
CG_TREFOIL = [1.00, 0.80, 0.72, 0.68, 0.66, 0.64, 0.63, 0.62, 0.61, 0.59, 0.57, 0.56]

VD_X90_3PH = [28.3, 17.0, 10.7, 7.15, 4.25, 2.7, 1.70, 1.22, 0.90, 0.61, 0.45, 0.36, 0.29, 0.23, 0.183, 0.147, 0.115, 0.074]
VD_X90_1PH = [49.0, 29.4, 18.5, 12.4, 7.35, 4.67, 2.94, 2.11, 1.56, 1.06, 0.78, 0.62, 0.50, 0.40, 0.317, 0.255, 0.199, 0.128]
VD_V75_3PH = [30.3, 18.2, 11.4, 7.64, 4.55, 2.89, 1.82, 1.30, 0.96, 0.66, 0.48, 0.38, 0.31, 0.25, 0.196, 0.157, 0.122, 0.079]

CPC_LINE = [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
CPC_MIN  = [1.5, 1.5, 1.5, 2.5, 4.0, 4.0, 6.0, 10, 16, 25, 35, 50, 70, 70, 95, 120, 150]


class AustraliaElectricalAdapter(BaseElectricalAdapter):
    """
    Electrical Standards Adapter for Australia / New Zealand.
    AS/NZS 3008.1.1:2017 — 40°C air / 25°C ground reference.
    MEN earthing system.
    """

    region = "australia"
    standard_name = "AS/NZS 3008.1.1:2017 / AS/NZS 3000:2018"

    def __init__(self, state: str = "nsw"):
        self.state = state.lower()
        self._cable_tables = None

    @property
    def voltage_lv(self) -> int:
        return 400

    @property
    def voltage_phase(self) -> int:
        return 230

    @property
    def frequency_hz(self) -> int:
        return 50

    @property
    def design_ambient_temp_air(self) -> float:
        return 40.0

    @property
    def design_ambient_temp_ground(self) -> float:
        return 25.0

    @property
    def voltage_drop_limit_lighting(self) -> float:
        return 5.0  # AS/NZS 3000 total 5% — no separate lighting limit

    @property
    def voltage_drop_limit_power(self) -> float:
        return 5.0

    @property
    def cable_sizing_standard(self) -> str:
        return "AS/NZS 3008.1.1:2017 (Electrical Installations — Selection of Cables)"

    @property
    def wiring_standard(self) -> str:
        return "AS/NZS 3000:2018 (Wiring Rules)"

    @property
    def protection_standard(self) -> str:
        return "AS/NZS 3111 (MCB) / AS 60947-2 (MCCB)"

    def load_cable_tables(self) -> dict:
        if self._cable_tables is None:
            self._cable_tables = self._load_json("australia/electrical/as3008_cable_tables.json")
        return self._cable_tables

    def get_cable_types(self) -> dict:
        return {
            "X90_CU": "X-90 XLPE Copper Multicore — AS/NZS 5000.1 (preferred for LV distribution)",
            "V75_CU": "V-75 PVC Copper Multicore — AS/NZS 5000.1",
            "X90_AL": "X-90 XLPE Aluminium — AS/NZS 5000.1",
        }

    def get_installation_methods(self) -> dict:
        return {
            "col_6": "In conduit in wall/ceiling (Table 1, Col 6)",
            "col_9": "Direct buried in ground (Table 3, Col 9)",
            "col_13": "Buried in conduit (Table 3, Col 13)",
            "col_22": "Clipped to flat surface, horizontal (Table 7, Col 22)",
            "col_23": "On perforated tray, single layer (Table 7, Col 23)",
            "col_24": "In free air, cables touching (Table 7, Col 24)",
        }

    def get_current_rating(self, cable_type: str, installation_method: str, conductor_size_mm2: float) -> float:
        method = installation_method.lower()
        ratings = X90_RATINGS if "X90" in cable_type.upper() or "XLPE" in cable_type.upper() else V75_RATINGS
        if method not in ratings:
            raise ValueError(f"Method '{method}' not found. Options: {list(ratings.keys())}")
        try:
            idx = SIZES.index(conductor_size_mm2)
        except ValueError:
            raise ValueError(f"Size {conductor_size_mm2}mm² not standard.")
        return float(ratings[method][idx])

    def get_ambient_temp_correction(self, cable_type: str, ambient_temp: float, ground: bool = False) -> float:
        if "X90" in cable_type.upper() or "XLPE" in cable_type.upper():
            if ground:
                return self.interpolate_correction_factor(X90_CA_TEMPS_GND, X90_CA_FACTORS_GND, ambient_temp)
            return self.interpolate_correction_factor(X90_CA_TEMPS, X90_CA_FACTORS, ambient_temp)
        return self.interpolate_correction_factor(V75_CA_TEMPS, V75_CA_FACTORS, ambient_temp)

    def get_grouping_correction(self, num_circuits: int, touching: bool = True, trefoil: bool = False) -> float:
        factors = CG_TREFOIL if trefoil else CG_FLAT_TOUCH
        return self.interpolate_grouping_factor(CG_NUM, factors, num_circuits)

    def get_voltage_drop_mv_am(self, cable_type: str, conductor_size_mm2: float, phases: int = 3) -> float:
        if "X90" in cable_type.upper() or "XLPE" in cable_type.upper():
            table = VD_X90_3PH if phases == 3 else VD_X90_1PH
        else:
            table = VD_V75_3PH
        return float(np.interp(conductor_size_mm2, SIZES, table))

    def get_voltage_drop_limit(self, circuit_type: str) -> float:
        return 5.0  # AS/NZS 3000 uniform 5% total

    def get_earthing_conductor_size(self, phase_conductor_mm2: float) -> float:
        return float(np.interp(phase_conductor_mm2, CPC_LINE, CPC_MIN))

    def get_next_cable_size(self, min_size_mm2: float) -> float:
        for s in SIZES:
            if s >= min_size_mm2:
                return s
        return SIZES[-1]

    def get_next_protection_rating(self, min_rating_a: float) -> float:
        all_ratings = sorted(MCB_RATINGS + MCCB_RATINGS)
        for r in all_ratings:
            if r >= min_rating_a:
                return float(r)
        return float(all_ratings[-1])

    def format_compliance_statement(self, check_name: str, passed: bool, details: str) -> str:
        state_names = {"nsw": "NSW", "vic": "VIC", "qld": "QLD", "sa": "SA", "wa": "WA", "tas": "TAS"}
        status = "✅ COMPLIANT" if passed else "❌ NON-COMPLIANT"
        return (
            f"{status} | {check_name}\n"
            f"  Standard: {self.wiring_standard}\n"
            f"  Cable Selection: {self.cable_sizing_standard}\n"
            f"  State: {state_names.get(self.state, self.state.upper())}\n"
            f"  Details: {details}"
        )
