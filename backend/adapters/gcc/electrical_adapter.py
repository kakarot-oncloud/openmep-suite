"""
GCC Regional Electrical Adapter
Standards: BS 7671:2018+A2:2022 / IEC 60364
Design conditions: 50°C air ambient, 35°C ground
Authorities: DEWA (Dubai), ADDC (Abu Dhabi), KAHRAMAA (Qatar), SEC (Saudi Arabia)
"""

import numpy as np
from ..base_adapter import BaseElectricalAdapter

SIZES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630]
MCB_RATINGS = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63]
MCCB_RATINGS = [63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600]

# BS 7671 Table 4D5A — Multicore XLPE/Cu (90°C), amperes
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

# BS 7671 Table 4D2A — Multicore PVC/Cu (70°C), amperes
PVC_CU_RATINGS = {
    "A1": [13.5, 18, 24, 31, 42, 56, 73, 89, 108, 136, 164, 188, 216, 245, 286, 328, 382, 508],
    "A2": [13, 17.5, 23, 29, 39, 52, 68, 83, 99, 125, 150, 172, 196, 223, 261, 298, 346, 461],
    "B1": [15.5, 21, 28, 36, 50, 68, 89, 110, 134, 171, 207, 239, 275, 314, 370, 424, 500, 668],
    "B2": [17.5, 24, 32, 40, 54, 73, 95, 117, 141, 179, 216, 249, 285, 324, 380, 435, 511, 681],
    "C":  [19.5, 27, 36, 46, 63, 85, 110, 135, 163, 207, 250, 288, 330, 376, 442, 507, 600, 800],
    "D1": [22, 29, 38, 47, 63, 83, 107, 130, 154, 194, 233, 269, 306, 349, 408, 466, 551, 741],
    "D2": [26, 34, 44, 55, 73, 95, 121, 148, 175, 222, 265, 307, 349, 393, 460, 530, 622, 838],
    "E":  [22, 30, 40, 51, 70, 94, 119, 147, 179, 229, 278, 322, 371, 424, 500, 576, 690, 930],
    "F":  [26, 35, 46, 59, 80, 107, 138, 169, 207, 268, 328, 382, 441, 506, 599, 693, 829, 1116],
}

# Ambient temp correction (Table 4B1) — XLPE reference 30°C
XLPE_CA_TEMPS = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
XLPE_CA_FACTORS = [1.15, 1.12, 1.08, 1.04, 1.00, 0.96, 0.91, 0.87, 0.82, 0.76, 0.71, 0.65, 0.58, 0.50, 0.41]

# Ambient temp correction — PVC reference 30°C
PVC_CA_TEMPS = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
PVC_CA_FACTORS = [1.22, 1.17, 1.12, 1.06, 1.00, 0.94, 0.87, 0.79, 0.71, 0.61, 0.50]

# Grouping factors (Table 4C1) — cables touching
CG_NUM = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 16, 20]
CG_TOUCH = [1.00, 0.80, 0.70, 0.65, 0.60, 0.57, 0.54, 0.52, 0.50, 0.45, 0.41, 0.38]
CG_SPACED = [1.00, 0.88, 0.82, 0.77, 0.73, 0.72, 0.72, 0.71, 0.70, 0.70, 0.70, 0.70]

# Voltage drop mV/A/m (XLPE Cu multicore, 3-phase)
VD_XLPE = [29, 18, 11, 7.3, 4.4, 2.8, 1.75, 1.25, 0.93, 0.63, 0.47, 0.37, 0.30, 0.24, 0.19, 0.15, 0.12, 0.077]
VD_PVC  = [31, 19, 12, 7.9, 4.7, 3.0, 1.85, 1.32, 0.98, 0.67, 0.49, 0.39, 0.31, 0.25, 0.20, 0.16, 0.12, 0.079]

# CPC minimum sizes (Table 54.7)
CPC_LINE = [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
CPC_MIN  = [1.0, 1.0, 1.0, 1.5, 2.5, 4.0, 6.0, 10, 16, 16, 35, 50, 70, 70, 95, 120, 150]


class GCCElectricalAdapter(BaseElectricalAdapter):
    """
    Electrical Standards Adapter for the GCC Region.
    Implements BS 7671 + IEC 60364 with GCC-specific design conditions.
    Sub-authority can be specified for precise voltage drop limits.
    """

    region = "gcc"
    standard_name = "BS 7671:2018+A2:2022 / IEC 60364"

    def __init__(self, sub_authority: str = "general"):
        """
        sub_authority options: 'dewa', 'addc', 'kahramaa', 'sec', 'mew', 'general'
        """
        self.sub_authority = sub_authority.lower()
        self._cable_tables = None

    # ── Fundamental electrical parameters ─────────────────────────────────────
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
        return 50.0  # GCC summer extreme

    @property
    def design_ambient_temp_ground(self) -> float:
        return 35.0

    # ── Voltage drop limits ────────────────────────────────────────────────────
    @property
    def voltage_drop_limit_lighting(self) -> float:
        return {"dewa": 3.0, "sec": 2.5}.get(self.sub_authority, 3.0)

    @property
    def voltage_drop_limit_power(self) -> float:
        return {"dewa": 4.0, "sec": 4.0, "addc": 5.0, "kahramaa": 5.0}.get(self.sub_authority, 5.0)

    # ── Standards references ───────────────────────────────────────────────────
    @property
    def cable_sizing_standard(self) -> str:
        return "BS 7671:2018+A2:2022 Table 4D5A (XLPE) / 4D2A (PVC)"

    @property
    def wiring_standard(self) -> str:
        return "BS 7671:2018 (IEE Wiring Regulations 18th Edition)"

    @property
    def protection_standard(self) -> str:
        return "BS EN 60898 (MCB) / BS EN 60947-2 (MCCB) / IEC 60947"

    @property
    def authority_name(self) -> str:
        names = {
            "dewa": "DEWA (Dubai Electricity and Water Authority)",
            "addc": "ADDC (Abu Dhabi Distribution Company)",
            "kahramaa": "KAHRAMAA (Qatar General Electricity & Water Corporation)",
            "sec": "SEC (Saudi Electricity Company) / SBC",
            "mew": "MEW (Ministry of Electricity & Water, Kuwait)",
        }
        return names.get(self.sub_authority, "GCC Authority")

    # ── Cable data loading ─────────────────────────────────────────────────────
    def load_cable_tables(self) -> dict:
        if self._cable_tables is None:
            self._cable_tables = self._load_json("gcc/electrical/bs7671_cable_tables.json")
        return self._cable_tables

    def get_cable_types(self) -> dict:
        return {
            "XLPE_CU": "XLPE/SWA/PVC Copper — BS 5467 (preferred for GCC, armoured)",
            "PVC_CU": "PVC/SWA/PVC Copper — BS 6346",
            "XLPE_AL": "XLPE/SWA/PVC Aluminium — BS 5467 (HV feeders only)",
        }

    def get_installation_methods(self) -> dict:
        return {
            "A1": "Enclosed in conduit in thermally insulating wall",
            "A2": "Enclosed in conduit in masonry",
            "B1": "Enclosed in conduit on wall or ceiling (surface conduit)",
            "B2": "Enclosed in trunking on wall",
            "C": "Clipped direct (on cable ladder/tray clipped)",
            "D1": "In duct in ground (underground in pipe/conduit)",
            "D2": "Direct burial in ground",
            "E": "On perforated cable tray (horizontal, single layer)",
            "F": "On cable tray (vertical)",
        }

    def get_current_rating(self, cable_type: str, installation_method: str, conductor_size_mm2: float) -> float:
        """
        Load current ratings from the regional JSON standards file (primary source).
        The JSON file contains BS 7671 tables keyed as 'method_A1', 'method_C', etc.
        Falls back to hardcoded tables if JSON read fails.
        """
        method = installation_method.upper()
        tables = self.load_cable_tables()
        try:
            if "XLPE" in cable_type.upper():
                ratings_data = tables.get("current_ratings_xlpe_cu_multicore", {})
            else:
                ratings_data = tables.get("current_ratings_pvc_cu_multicore", {})

            json_key = f"method_{method}"   # JSON uses 'method_C', 'method_A1' etc.
            if json_key in ratings_data:
                method_list = ratings_data[json_key]        # list of amps
                sizes_list = ratings_data.get("sizes_mm2", SIZES)
                if isinstance(method_list, list) and isinstance(sizes_list, list):
                    return float(np.interp(conductor_size_mm2, sizes_list, method_list))
        except (KeyError, TypeError, ValueError):
            pass  # Fall through to hardcoded tables

        # Fallback to hardcoded tables (identical data source, ensures reliability)
        ratings = XLPE_CU_RATINGS if "XLPE" in cable_type.upper() else PVC_CU_RATINGS
        if method not in ratings:
            raise ValueError(f"Unknown installation method '{method}'. Choose from: {list(ratings.keys())}")
        try:
            idx = SIZES.index(conductor_size_mm2)
        except ValueError:
            return float(np.interp(conductor_size_mm2, SIZES, ratings.get(method, ratings["C"])))
        return float(ratings[method][idx])

    def get_ambient_temp_correction(self, cable_type: str, ambient_temp: float) -> float:
        """Load ambient temp correction from JSON; fall back to hardcoded factors."""
        tables = self.load_cable_tables()
        try:
            if "XLPE" in cable_type.upper():
                ca_data = tables.get("ambient_temp_correction_xlpe", {})
            else:
                ca_data = tables.get("ambient_temp_correction_pvc", {})
            if ca_data and "temperatures" in ca_data and "factors" in ca_data:
                return self.interpolate_correction_factor(
                    ca_data["temperatures"], ca_data["factors"], ambient_temp
                )
        except (KeyError, TypeError):
            pass
        # Fallback
        if "XLPE" in cable_type.upper():
            return self.interpolate_correction_factor(XLPE_CA_TEMPS, XLPE_CA_FACTORS, ambient_temp)
        return self.interpolate_correction_factor(PVC_CA_TEMPS, PVC_CA_FACTORS, ambient_temp)

    def get_grouping_correction(self, num_circuits: int, touching: bool = True) -> float:
        """Load grouping correction from JSON (primary); fall back to hardcoded factors."""
        tables = self.load_cable_tables()
        try:
            cg_data = tables.get("grouping_correction_factors", {})
            # JSON uses 'factors_touching' and 'factors_spaced'
            json_key = "factors_touching" if touching else "factors_spaced"
            if cg_data and "num_circuits" in cg_data and json_key in cg_data:
                return self.interpolate_grouping_factor(
                    cg_data["num_circuits"], cg_data[json_key], num_circuits
                )
        except (KeyError, TypeError):
            pass
        # Fallback
        factors = CG_TOUCH if touching else CG_SPACED
        return self.interpolate_grouping_factor(CG_NUM, factors, num_circuits)

    def get_voltage_drop_mv_am(self, cable_type: str, conductor_size_mm2: float, phases: int = 3) -> float:
        """Load voltage drop mV/A/m from JSON (primary); fall back to hardcoded table.
        JSON key: voltage_drop_xlpe_cu_mv_per_am.total_mv_am_3ph (list aligned to sizes_mm2).
        """
        tables = self.load_cable_tables()
        try:
            if "XLPE" in cable_type.upper():
                vd_data = tables.get("voltage_drop_xlpe_cu_mv_per_am", {})
            else:
                vd_data = tables.get("voltage_drop_pvc_cu_mv_per_am", {})

            if vd_data and "sizes_mm2" in vd_data and "total_mv_am_3ph" in vd_data:
                sizes_list = vd_data["sizes_mm2"]
                vd_3ph = vd_data["total_mv_am_3ph"]
                vd_mv = float(np.interp(conductor_size_mm2, sizes_list, vd_3ph))
                if phases == 1:
                    vd_mv = vd_mv * (2.0 / np.sqrt(3))
                return vd_mv
        except (KeyError, TypeError, ValueError):
            pass
        # Fallback to hardcoded
        vd_table = VD_XLPE if "XLPE" in cable_type.upper() else VD_PVC
        vd_mv = float(np.interp(conductor_size_mm2, SIZES, vd_table))
        if phases == 1:
            vd_mv = vd_mv * (2.0 / np.sqrt(3))
        return vd_mv

    def get_voltage_drop_limit(self, circuit_type: str) -> float:
        """Load VD limit from JSON (primary); fall back to regional constants.
        JSON structure: voltage_drop_limits.gcc_dewa.lighting / .power
        """
        tables = self.load_cable_tables()
        try:
            vd_limits = tables.get("voltage_drop_limits", {})
            # Build key: sub_authority mapped to JSON key (e.g. 'dewa' -> 'gcc_dewa')
            sub = self.sub_authority
            json_key = f"gcc_{sub}" if sub not in ("general", "") else "general_bs7671"
            if json_key in vd_limits:
                limits_for_auth = vd_limits[json_key]
            elif "general_bs7671" in vd_limits:
                limits_for_auth = vd_limits["general_bs7671"]
            else:
                limits_for_auth = {}
            ct = circuit_type.lower()
            if ct == "lighting" and "lighting" in limits_for_auth:
                return float(limits_for_auth["lighting"])
            if ct in ("power", "general") and "power" in limits_for_auth:
                return float(limits_for_auth["power"])
        except (KeyError, TypeError):
            pass
        if circuit_type.lower() == "lighting":
            return self.voltage_drop_limit_lighting
        return self.voltage_drop_limit_power

    def get_earthing_conductor_size(self, phase_conductor_mm2: float) -> float:
        """Load CPC sizes from JSON (primary); fall back to hardcoded table.
        JSON key: earthing_conductor_sizes.line_conductor_mm2 / .min_cpc_mm2
        """
        tables = self.load_cable_tables()
        try:
            earth_data = tables.get("earthing_conductor_sizes", {})
            if earth_data and "line_conductor_mm2" in earth_data and "min_cpc_mm2" in earth_data:
                return float(np.interp(phase_conductor_mm2,
                                       earth_data["line_conductor_mm2"],
                                       earth_data["min_cpc_mm2"]))
        except (KeyError, TypeError):
            pass
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
            f"  Authority: {self.authority_name}\n"
            f"  Details: {details}"
        )
