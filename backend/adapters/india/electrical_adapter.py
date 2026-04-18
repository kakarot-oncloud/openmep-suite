"""
India Regional Electrical Adapter
Standards: IS 3961:2011 / IS 732:2019 / IS 7098 Part 1 (XLPE)
Design conditions: 45°C air ambient, 30°C ground (IS reference)
Cable: 3.5 core (neutral = 50% of phase); FRLS mandatory per NBC 2016 Part 4
"""

import numpy as np
from ..base_adapter import BaseElectricalAdapter

SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630]
MCB_RATINGS = [6, 10, 16, 20, 25, 32, 40, 50, 63]
MCCB_RATINGS = [63, 100, 125, 160, 200, 250, 320, 400, 500, 630, 800, 1000, 1250, 1600]

# IS 3961 / IS 7098 Pt1 — XLPE FRLS Cu 3.5-core, ambient reference
XLPE_CU_IN_GROUND_30C = [26, 35, 46, 57, 77, 101, 130, 159, 193, 247, 298, 345, 393, 449, 529, 608, 710, 946]
XLPE_CU_ON_TRAY_45C   = [19, 26, 34, 43, 58, 77, 100, 123, 149, 190, 230, 266, 304, 347, 409, 470, 549, 732]
XLPE_CU_CLIPPED_45C   = [17, 23, 30, 38, 52, 69, 90, 111, 134, 171, 207, 239, 275, 314, 370, 424, 495, 660]
XLPE_CU_IN_CONDUIT_45C = [14, 19, 25, 32, 43, 58, 75, 92, 112, 143, 172, 198, 228, 260, 305, 350, 409, 545]

# PVC FRLS Cu 3.5-core
PVC_CU_IN_GROUND_30C = [22, 30, 40, 50, 67, 88, 112, 136, 163, 207, 249, 289, 328, 374, 438, 503, 587, 782]
PVC_CU_ON_TRAY_45C   = [16, 22, 29, 37, 49, 64, 83, 101, 122, 155, 187, 217, 248, 283, 333, 382, 446, 594]

_XLPE_RATINGS = {
    "D": XLPE_CU_IN_GROUND_30C,
    "B": XLPE_CU_ON_TRAY_45C,
    "C": XLPE_CU_CLIPPED_45C,
    "A": XLPE_CU_IN_CONDUIT_45C,
}
_PVC_RATINGS = {
    "D": PVC_CU_IN_GROUND_30C,
    "B": PVC_CU_ON_TRAY_45C,
}

# Ambient temp correction — XLPE, reference 45°C
XLPE_CA_TEMPS = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
XLPE_CA_FACTORS = [1.13, 1.09, 1.05, 1.02, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76]

PVC_CA_TEMPS = [25, 30, 35, 40, 45, 50, 55]
PVC_CA_FACTORS = [1.19, 1.14, 1.09, 1.04, 1.00, 0.94, 0.87]

CG_NUM = [1, 2, 3, 4, 5, 6, 8, 10, 12]
CG_TOUCH = [1.00, 0.80, 0.70, 0.65, 0.60, 0.57, 0.52, 0.49, 0.46]
CG_ON_TRAY = [1.00, 0.88, 0.77, 0.70, 0.66, 0.62, 0.58, 0.55, 0.52]

VD_XLPE_3PH = [29, 18, 11, 7.5, 4.5, 2.85, 1.80, 1.28, 0.95, 0.65, 0.48, 0.38, 0.31, 0.25, 0.19, 0.15, 0.12, 0.077]
VD_XLPE_1PH = [50, 31, 19, 13, 7.8, 4.9, 3.1, 2.2, 1.65, 1.12, 0.83, 0.65, 0.54, 0.43, 0.33, 0.26, 0.20, 0.13]

# Earthing conductor sizes (IS 3043:2018)
CPC_LINE = [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
CPC_MIN  = [1.5, 1.5, 1.5, 2.5, 4.0, 6.0, 10, 16, 16, 25, 35, 50, 70, 70, 95, 120, 150]


class IndiaElectricalAdapter(BaseElectricalAdapter):
    """
    Electrical Standards Adapter for India.
    IS 3961 / IS 732 / IS 7098 — 45°C air, 30°C ground reference.
    3.5-core cables, FRLS mandatory.
    """

    region = "india"
    standard_name = "IS 3961:2011 / IS 732:2019 / IS 7098 (XLPE)"

    def __init__(self, state: str = "maharashtra", discom: str = "MSEDCL"):
        self.state = state
        self.discom = discom
        self._cable_tables = None

    @property
    def voltage_lv(self) -> int:
        return 415

    @property
    def voltage_phase(self) -> int:
        return 240

    @property
    def frequency_hz(self) -> int:
        return 50

    @property
    def design_ambient_temp_air(self) -> float:
        return 45.0

    @property
    def design_ambient_temp_ground(self) -> float:
        return 30.0

    @property
    def voltage_drop_limit_lighting(self) -> float:
        return 2.5

    @property
    def voltage_drop_limit_power(self) -> float:
        return 5.0

    @property
    def cable_sizing_standard(self) -> str:
        return "IS 3961:2011 / IS 7098 Part 1 (XLPE FRLS)"

    @property
    def wiring_standard(self) -> str:
        return "IS 732:2019 (Code of Practice for Electrical Wiring Installations)"

    @property
    def protection_standard(self) -> str:
        return "IS 8828 (MCB) / IS 13947-2 (MCCB) / IS 2516 (ACB)"

    def load_cable_tables(self) -> dict:
        if self._cable_tables is None:
            self._cable_tables = self._load_json("india/electrical/is3961_cable_tables.json")
        return self._cable_tables

    def get_cable_types(self) -> dict:
        return {
            "XLPE_FRLS_CU": "XLPE/FRLS/SWA Copper (3.5 core) — IS 7098 Part 1 [MANDATORY in buildings]",
            "PVC_FRLS_CU": "PVC/FRLS/SWA Copper (3.5 core) — IS 1554 Part 1",
            "XLPE_AL": "XLPE/FRLS/SWA Aluminium — IS 7098 Part 2",
        }

    def get_installation_methods(self) -> dict:
        return {
            "A": "Enclosed in conduit (embedded or surface)",
            "B": "On perforated cable tray or ladder rack",
            "C": "Clipped direct to wall/structure",
            "D": "Buried in ground (direct) or in duct",
        }

    def get_current_rating(self, cable_type: str, installation_method: str, conductor_size_mm2: float) -> float:
        method = installation_method.upper()
        ratings = _XLPE_RATINGS if "XLPE" in cable_type.upper() else _PVC_RATINGS
        if method not in ratings:
            raise ValueError(f"Method '{method}' not available. Use: {list(ratings.keys())}")
        try:
            idx = SIZES.index(conductor_size_mm2)
        except ValueError:
            raise ValueError(f"Size {conductor_size_mm2}mm² not standard. Use: {SIZES}")
        return float(ratings[method][idx])

    def get_ambient_temp_correction(self, cable_type: str, ambient_temp: float) -> float:
        if "XLPE" in cable_type.upper():
            return self.interpolate_correction_factor(XLPE_CA_TEMPS, XLPE_CA_FACTORS, ambient_temp)
        return self.interpolate_correction_factor(PVC_CA_TEMPS, PVC_CA_FACTORS, ambient_temp)

    def get_grouping_correction(self, num_circuits: int, touching: bool = True) -> float:
        factors = CG_TOUCH if touching else CG_ON_TRAY
        return self.interpolate_grouping_factor(CG_NUM, factors, num_circuits)

    def get_voltage_drop_mv_am(self, cable_type: str, conductor_size_mm2: float, phases: int = 3) -> float:
        if phases == 1:
            return float(np.interp(conductor_size_mm2, SIZES, VD_XLPE_1PH))
        return float(np.interp(conductor_size_mm2, SIZES, VD_XLPE_3PH))

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
            f"  DISCOM: {self.discom} | State: {self.state.title()}\n"
            f"  Details: {details}\n"
            f"  Note: FRLS cable mandatory per NBC 2016 Part 4 Cl 4.12.1"
        )
