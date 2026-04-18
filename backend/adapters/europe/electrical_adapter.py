"""
Europe Regional Electrical Adapter
Standards: BS 7671:2018+A2:2022 (UK) / IEC 60364 (EU)
Design conditions: 30°C air ambient, 20°C ground
"""

import numpy as np
from ..base_adapter import BaseElectricalAdapter

SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630]
MCB_RATINGS = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63]
MCCB_RATINGS = [63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600]

XLPE_CU_RATINGS = {
    "A1": [17.5, 24, 32, 40, 54, 73, 95, 117, 141, 179, 216, 249, 285, 324, 380, 435, 510, 680],
    "A2": [16.5, 23, 30, 38, 51, 69, 90, 111, 133, 168, 203, 234, 268, 305, 358, 410, 481, 640],
    "B1": [20, 27, 36, 46, 63, 85, 110, 135, 163, 207, 250, 288, 330, 376, 442, 507, 594, 792],
    "B2": [22, 30, 40, 50, 67, 89, 116, 143, 173, 220, 267, 308, 354, 404, 474, 543, 637, 849],
    "C":  [26, 34, 46, 57, 77, 102, 133, 163, 198, 253, 306, 354, 407, 464, 546, 628, 754, 1005],
    "D1": [22, 29, 38, 47, 63, 83, 107, 130, 154, 194, 233, 269, 306, 349, 408, 466, 551, 741],
    "D2": [26, 35, 46, 57, 76, 99, 128, 157, 188, 237, 285, 330, 376, 430, 505, 580, 686, 924],
    "E":  [29, 39, 52, 65, 88, 117, 152, 187, 227, 290, 352, 406, 464, 530, 624, 717, 856, 1151],
    "F":  [33, 44, 59, 73, 99, 132, 171, 210, 255, 326, 395, 456, 521, 595, 700, 804, 960, 1289],
}

PVC_CU_RATINGS = {
    "A1": [13.5, 18, 24, 31, 42, 56, 73, 89, 108, 136, 164, 188, 216, 245, 286, 328, 382, 508],
    "B1": [15.5, 21, 28, 36, 50, 68, 89, 110, 134, 171, 207, 239, 275, 314, 370, 424, 500, 668],
    "B2": [17.5, 24, 32, 40, 54, 73, 95, 117, 141, 179, 216, 249, 285, 324, 380, 435, 511, 681],
    "C":  [19.5, 27, 36, 46, 63, 85, 110, 135, 163, 207, 250, 288, 330, 376, 442, 507, 600, 800],
    "D1": [22, 29, 38, 47, 63, 83, 107, 130, 154, 194, 233, 269, 306, 349, 408, 466, 551, 741],
    "E":  [22, 30, 40, 51, 70, 94, 119, 147, 179, 229, 278, 322, 371, 424, 500, 576, 690, 930],
}

XLPE_CA_TEMPS = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
XLPE_CA_FACTORS = [1.15, 1.12, 1.08, 1.04, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76, 0.71, 0.65, 0.58, 0.50, 0.41]
PVC_CA_TEMPS = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
PVC_CA_FACTORS = [1.22, 1.17, 1.12, 1.06, 1.00, 0.94, 0.87, 0.79, 0.71, 0.61, 0.50]

CG_NUM = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 20]
CG_TOUCH = [1.00, 0.80, 0.70, 0.65, 0.60, 0.57, 0.54, 0.52, 0.50, 0.45, 0.41, 0.38]
CG_SPACED = [1.00, 0.88, 0.82, 0.77, 0.73, 0.72, 0.72, 0.71, 0.70, 0.70, 0.70, 0.70]

VD_XLPE = [29, 18, 11, 7.3, 4.4, 2.8, 1.75, 1.25, 0.93, 0.63, 0.47, 0.37, 0.30, 0.24, 0.19, 0.15, 0.12, 0.077]
VD_PVC  = [31, 19, 12, 7.9, 4.7, 3.0, 1.85, 1.32, 0.98, 0.67, 0.49, 0.39, 0.31, 0.25, 0.20, 0.16, 0.12, 0.079]

CPC_LINE = [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
CPC_MIN  = [1.0, 1.0, 1.0, 1.5, 2.5, 4.0, 6.0, 10, 16, 16, 35, 50, 70, 70, 95, 120, 150]


class EuropeElectricalAdapter(BaseElectricalAdapter):
    """
    Electrical Standards Adapter for Europe (UK primary).
    BS 7671:2018+A2:2022 — 30°C reference ambient.
    """

    region = "europe"
    standard_name = "BS 7671:2018+A2:2022 (18th Edition)"

    def __init__(self, country: str = "uk"):
        self.country = country.lower()
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
        return 30.0

    @property
    def design_ambient_temp_ground(self) -> float:
        return 20.0

    @property
    def voltage_drop_limit_lighting(self) -> float:
        return 3.0

    @property
    def voltage_drop_limit_power(self) -> float:
        return 5.0

    @property
    def cable_sizing_standard(self) -> str:
        return "BS 7671:2018+A2:2022 Appendix 4 (Table 4D5A XLPE / 4D2A PVC)"

    @property
    def wiring_standard(self) -> str:
        return "BS 7671:2018+A2:2022 (IEE Wiring Regulations 18th Edition)"

    @property
    def protection_standard(self) -> str:
        return "BS EN 60898 (MCB) / BS EN 60947-2 (MCCB)"

    def load_cable_tables(self) -> dict:
        if self._cable_tables is None:
            self._cable_tables = self._load_json("europe/electrical/bs7671_18th_tables.json")
        return self._cable_tables

    def get_cable_types(self) -> dict:
        return {
            "XLPE_CU": "XLPE/SWA/PVC Copper — BS 5467 / BS 6724 / BS 7846",
            "PVC_CU": "PVC/SWA/PVC Copper — BS 6346",
            "FP200": "Fire Performance Cable — BS 7629-1 / BS EN 50200",
        }

    def get_installation_methods(self) -> dict:
        return {
            "A1": "In conduit in thermally insulating wall (worst case)",
            "A2": "In conduit in masonry",
            "B1": "In conduit on wall / ceiling (surface conduit)",
            "B2": "In trunking on wall",
            "C": "Clipped direct to surface",
            "D1": "Underground in conduit/duct",
            "D2": "Direct burial",
            "E": "In free air / cable tray (horizontal)",
            "F": "On cable tray (vertical)",
        }

    def get_current_rating(self, cable_type: str, installation_method: str, conductor_size_mm2: float) -> float:
        method = installation_method.upper()
        ratings = XLPE_CU_RATINGS if "XLPE" in cable_type.upper() else PVC_CU_RATINGS
        if method not in ratings:
            raise ValueError(f"Installation method '{method}' not recognised. Options: {list(ratings.keys())}")
        idx = SIZES.index(conductor_size_mm2)
        return float(ratings[method][idx])

    def get_ambient_temp_correction(self, cable_type: str, ambient_temp: float) -> float:
        if "XLPE" in cable_type.upper():
            return self.interpolate_correction_factor(XLPE_CA_TEMPS, XLPE_CA_FACTORS, ambient_temp)
        return self.interpolate_correction_factor(PVC_CA_TEMPS, PVC_CA_FACTORS, ambient_temp)

    def get_grouping_correction(self, num_circuits: int, touching: bool = True) -> float:
        factors = CG_TOUCH if touching else CG_SPACED
        return self.interpolate_grouping_factor(CG_NUM, factors, num_circuits)

    def get_voltage_drop_mv_am(self, cable_type: str, conductor_size_mm2: float, phases: int = 3) -> float:
        vd_table = VD_XLPE if "XLPE" in cable_type.upper() else VD_PVC
        vd_mv = float(np.interp(conductor_size_mm2, SIZES, vd_table))
        if phases == 1:
            vd_mv = vd_mv * (2 / np.sqrt(3))
        return vd_mv

    def get_voltage_drop_limit(self, circuit_type: str) -> float:
        return self.voltage_drop_limit_lighting if circuit_type.lower() == "lighting" else self.voltage_drop_limit_power

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
        status = "✅ COMPLIANT" if passed else "❌ NON-COMPLIANT"
        return (
            f"{status} | {check_name}\n"
            f"  Standard: {self.wiring_standard}\n"
            f"  Country: {self.country.upper()}\n"
            f"  Details: {details}"
        )
