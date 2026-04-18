"""
OpenMEP Standards Adapter Base Module
--------------------------------------
This is the core architectural pattern for OpenMEP.
Every regional adapter inherits from BaseAdapter and implements
the same interface — allowing calculation engines to swap
standards tables and limits without changing the calculation logic.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import json
import numpy as np


STANDARDS_DATA_DIR = Path(__file__).parent.parent / "standards_data"


class BaseElectricalAdapter(ABC):
    """Abstract base for all regional electrical standards adapters."""

    region: str = ""
    standard_name: str = ""

    # ── Fundamental electrical parameters ────────────────────────────────────
    @property
    @abstractmethod
    def voltage_lv(self) -> int:
        """Line voltage (V) e.g. 400"""

    @property
    @abstractmethod
    def voltage_phase(self) -> int:
        """Phase voltage (V) e.g. 230"""

    @property
    @abstractmethod
    def frequency_hz(self) -> int:
        """Frequency in Hz (50 or 60)"""

    @property
    @abstractmethod
    def design_ambient_temp_air(self) -> float:
        """Design ambient temperature in air (°C)"""

    @property
    @abstractmethod
    def design_ambient_temp_ground(self) -> float:
        """Design ambient temperature in ground (°C)"""

    # ── Voltage drop limits ───────────────────────────────────────────────────
    @property
    @abstractmethod
    def voltage_drop_limit_lighting(self) -> float:
        """Maximum voltage drop % for lighting circuits"""

    @property
    @abstractmethod
    def voltage_drop_limit_power(self) -> float:
        """Maximum voltage drop % for power circuits"""

    # ── Standards references ──────────────────────────────────────────────────
    @property
    @abstractmethod
    def cable_sizing_standard(self) -> str:
        """Standard used for cable current ratings"""

    @property
    @abstractmethod
    def wiring_standard(self) -> str:
        """Primary wiring standard"""

    @property
    @abstractmethod
    def protection_standard(self) -> str:
        """Standard for overcurrent protection devices"""

    # ── Cable data loading ────────────────────────────────────────────────────
    @abstractmethod
    def load_cable_tables(self) -> dict:
        """Load the regional cable current rating tables"""

    def _load_json(self, relative_path: str) -> dict:
        """Helper to load a standards data JSON file."""
        full_path = STANDARDS_DATA_DIR / relative_path
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── Core calculation helpers ──────────────────────────────────────────────
    @abstractmethod
    def get_cable_types(self) -> dict:
        """Return dict of available cable types for this region"""

    @abstractmethod
    def get_installation_methods(self) -> dict:
        """Return dict of cable installation methods for this region"""

    @abstractmethod
    def get_current_rating(
        self,
        cable_type: str,
        installation_method: str,
        conductor_size_mm2: float,
    ) -> float:
        """Get the tabulated current rating Iz (A) for given cable & method"""

    @abstractmethod
    def get_ambient_temp_correction(
        self,
        cable_type: str,
        ambient_temp: float,
    ) -> float:
        """Get derating factor Ca for ambient temperature"""

    @abstractmethod
    def get_grouping_correction(
        self,
        num_circuits: int,
        touching: bool = True,
    ) -> float:
        """Get derating factor Cg for grouping/bunching"""

    @abstractmethod
    def get_voltage_drop_mv_am(
        self,
        cable_type: str,
        conductor_size_mm2: float,
        phases: int = 3,
    ) -> float:
        """Get voltage drop in mV per ampere per metre"""

    @abstractmethod
    def get_voltage_drop_limit(self, circuit_type: str) -> float:
        """Get voltage drop limit % for circuit type: 'lighting' or 'power'"""

    @abstractmethod
    def get_earthing_conductor_size(self, phase_conductor_mm2: float) -> float:
        """Get minimum protective conductor size for given phase conductor"""

    @abstractmethod
    def get_next_cable_size(self, min_size_mm2: float) -> float:
        """Get the next standard cable size at or above min_size_mm2"""

    @abstractmethod
    def get_next_protection_rating(self, min_rating_a: float) -> float:
        """Get next available MCB/MCCB rating at or above min_rating_a"""

    @abstractmethod
    def format_compliance_statement(self, check_name: str, passed: bool, details: str) -> str:
        """Format a compliance statement with region-specific standard reference"""

    # ── Shared utility methods ────────────────────────────────────────────────
    def interpolate_correction_factor(
        self, temperatures: list, factors: list, target_temp: float
    ) -> float:
        """Linearly interpolate a correction factor for a given temperature."""
        temps = np.array(temperatures, dtype=float)
        facs = np.array(factors, dtype=float)
        if target_temp <= temps[0]:
            return float(facs[0])
        if target_temp >= temps[-1]:
            return float(facs[-1])
        return float(np.interp(target_temp, temps, facs))

    def interpolate_grouping_factor(
        self, num_circuits_list: list, factors: list, num_circuits: int
    ) -> float:
        """Get grouping factor, interpolating for intermediate values."""
        nc = np.array(num_circuits_list, dtype=float)
        facs = np.array(factors, dtype=float)
        return float(np.interp(float(num_circuits), nc, facs))

    def get_standard_cable_sizes(self) -> list:
        """Return the standard cable sizes in mm²."""
        return [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 630]


class BaseMechanicalAdapter(ABC):
    """Abstract base for regional HVAC/mechanical standards adapters."""

    region: str = ""

    @property
    @abstractmethod
    def outdoor_db_summer(self) -> float:
        """Design outdoor dry-bulb temperature, summer (°C)"""

    @property
    @abstractmethod
    def outdoor_wb_summer(self) -> float:
        """Design outdoor wet-bulb temperature, summer (°C)"""

    @property
    @abstractmethod
    def indoor_db_cooling(self) -> float:
        """Indoor design dry-bulb temperature for cooling (°C)"""

    @property
    @abstractmethod
    def indoor_rh_cooling(self) -> float:
        """Indoor design relative humidity for cooling (%)"""

    @property
    @abstractmethod
    def load_calculation_method(self) -> str:
        """Method used: 'ASHRAE_RTS', 'CIBSE_Admittance', 'ECBC', 'NCC'"""

    @property
    @abstractmethod
    def load_output_unit(self) -> str:
        """Output unit: 'TR' (tons of refrigeration) or 'kW'"""

    @property
    @abstractmethod
    def ventilation_standard(self) -> str:
        """Ventilation standard: 'ASHRAE 62.1', 'EN 16798', 'AS 1668.2', etc."""

    @property
    @abstractmethod
    def energy_code(self) -> str:
        """Energy code: 'ASHRAE 90.1', 'Part L', 'ECBC 2017', 'NCC Section J'"""


class BasePlumbingAdapter(ABC):
    """Abstract base for regional plumbing standards adapters."""

    region: str = ""

    @property
    @abstractmethod
    def pipe_sizing_standard(self) -> str:
        """Pipe sizing standard reference"""

    @property
    @abstractmethod
    def drainage_standard(self) -> str:
        """Drainage sizing standard reference"""

    @property
    @abstractmethod
    def pressure_unit(self) -> str:
        """Pressure unit: 'bar', 'kPa', 'kg/cm2'"""


class BaseFireAdapter(ABC):
    """Abstract base for regional fire protection standards adapters."""

    region: str = ""

    @property
    @abstractmethod
    def sprinkler_standard(self) -> str:
        """Sprinkler design standard"""

    @property
    @abstractmethod
    def fire_alarm_standard(self) -> str:
        """Fire alarm standard"""

    @property
    @abstractmethod
    def fire_pump_standard(self) -> str:
        """Fire pump standard"""
