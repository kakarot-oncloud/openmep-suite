"""
Comprehensive tests for the fire sprinkler calculation engine.
Reference values traceable to published standards:

  BS EN 12845:2015 — Fixed firefighting systems, Automatic sprinkler systems
    Table 3: Hazard classification design parameters
      LH:  density 2.25 L/min/m2, area  84 m2, duration 30 min
      OH1: density 5.00 L/min/m2, area 216 m2, duration 60 min
      OH2: density 5.00 L/min/m2, area 360 m2, duration 60 min
      EH1: density 7.50 L/min/m2, area 260 m2, duration 90 min
      EH2: density 10.0 L/min/m2, area 260 m2, duration 90 min
    Sec 12.3: Hose allowance for OH1/OH2 = 600 L/min
    Sec 10.2: Sprinkler K-factor equation: Q = K x sqrt(P)

  AS 2118.1:2017 (Australia)
  IS 15105:2002 / NBC 2016 Part 4 (India)
  NFPA 13:2022 Edition (USA / GCC supplement)

Run: python -m pytest backend/tests/test_fire.py -v
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from backend.engines.fire.sprinkler_calc import (
    SprinklerInput, SprinklerResult, calculate_sprinkler, HAZARD_PARAMS, SPRINKLER_STANDARDS
)


class TestSprinklerHazardParamsBSEN12845:
    """
    Verify HAZARD_PARAMS table against BS EN 12845:2015 Table 3.
    These are the source-of-truth values that all calculations derive from.
    """

    def test_lh_hazard_bsen12845_table3(self):
        """LH (Light Hazard): density=2.25 L/min/m2, area=84 m2, duration=30 min."""
        p = HAZARD_PARAMS["LH"]
        assert p["density_mm_min"] == 2.25,  "LH density: BS EN 12845 Table 3 = 2.25 L/min/m2"
        assert p["area_m2"]        == 84,    "LH area:    BS EN 12845 Table 3 = 84 m2"
        assert p["duration_min"]   == 30,    "LH duration: BS EN 12845 Table 3 = 30 min"

    def test_oh1_hazard_bsen12845_table3(self):
        """OH1 (Ordinary Hazard Gp 1): density=5.0, area=216 m2, duration=60 min."""
        p = HAZARD_PARAMS["OH1"]
        assert p["density_mm_min"] == 5.0,   "OH1 density: BS EN 12845 Table 3 = 5.0 L/min/m2"
        assert p["area_m2"]        == 216,   "OH1 area:    BS EN 12845 Table 3 = 216 m2"
        assert p["duration_min"]   == 60,    "OH1 duration: BS EN 12845 Table 3 = 60 min"

    def test_oh2_hazard_bsen12845_table3(self):
        """OH2 (Ordinary Hazard Gp 2): density=5.0, area=360 m2, duration=60 min."""
        p = HAZARD_PARAMS["OH2"]
        assert p["density_mm_min"] == 5.0,   "OH2 density: BS EN 12845 Table 3 = 5.0 L/min/m2"
        assert p["area_m2"]        == 360,   "OH2 area:    BS EN 12845 Table 3 = 360 m2"
        assert p["duration_min"]   == 60,    "OH2 duration: BS EN 12845 Table 3 = 60 min"

    def test_eh1_hazard_bsen12845_table3(self):
        """EH1 (Extra High Hazard Gp 1): density=7.5, area=260 m2, duration=90 min."""
        p = HAZARD_PARAMS["EH1"]
        assert p["density_mm_min"] == 7.5,   "EH1 density: BS EN 12845 Table 3 = 7.5 L/min/m2"
        assert p["area_m2"]        == 260,   "EH1 area:    BS EN 12845 Table 3 = 260 m2"
        assert p["duration_min"]   == 90,    "EH1 duration: BS EN 12845 Table 3 = 90 min"

    def test_eh2_hazard_bsen12845_table3(self):
        """EH2 (Extra High Hazard Gp 2): density=10.0, area=260 m2, duration=90 min."""
        p = HAZARD_PARAMS["EH2"]
        assert p["density_mm_min"] == 10.0,  "EH2 density: BS EN 12845 Table 3 = 10.0 L/min/m2"
        assert p["area_m2"]        == 260,   "EH2 area:    BS EN 12845 Table 3 = 260 m2"
        assert p["duration_min"]   == 90,    "EH2 duration: BS EN 12845 Table 3 = 90 min"


class TestSprinklerFlowCalculationReferenceValues:
    """
    Reference calculation: Q_design = density x area  (BS EN 12845 Sec 11.3.1)
    All flow values are in L/min.
    """

    def test_oh1_design_flow_1080_l_min(self):
        """
        OH1: density=5.0 L/min/m2, area=216 m2
        Q_design = 5.0 x 216 = 1080 L/min  (BS EN 12845 Sec 11.3.1)
        With hose allowance 600 L/min: Q_total = 1080 + 600 = 1680 L/min
        """
        inp = SprinklerInput(
            region="europe", occupancy_hazard="OH1",
            area_protected_m2=500, ceiling_height_m=4.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        assert abs(r.design_flow_l_min - 1080.0) < 5, (
            f"OH1: Q_design expected 1080 L/min (5.0x216), got {r.design_flow_l_min}"
        )
        assert abs(r.total_system_flow_l_min - 1680.0) < 5, (
            f"OH1: Q_total expected 1680 L/min (1080+600), got {r.total_system_flow_l_min}"
        )
        assert r.hose_allowance_l_min == 600
        assert r.supply_duration_min == 60  # OH1 = 60 min per BS EN 12845 Table 3

    def test_oh2_design_flow_1800_l_min(self):
        """
        OH2: density=5.0 L/min/m2, area=360 m2
        Q_design = 5.0 x 360 = 1800 L/min
        Q_total  = 1800 + 600 = 2400 L/min
        n_sprinklers = ceil(360 / 12) = 30 heads
        q_per_sprinkler = 1800 / 30 = 60 L/min
        """
        inp = SprinklerInput(
            region="gcc", occupancy_hazard="OH2",
            area_protected_m2=800, ceiling_height_m=5.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        assert abs(r.design_flow_l_min - 1800.0) < 5, (
            f"OH2: Q_design expected 1800 L/min, got {r.design_flow_l_min}"
        )
        assert abs(r.total_system_flow_l_min - 2400.0) < 5
        assert r.num_sprinklers_design_area == 30, (
            f"OH2: n_sprinklers = ceil(360/12) = 30, got {r.num_sprinklers_design_area}"
        )

    def test_lh_design_flow_189_l_min(self):
        """
        LH: density=2.25 L/min/m2, area=84 m2
        Q_design = 2.25 x 84 = 189 L/min
        Q_total  = 189 + 600 = 789 L/min  (hose allowance added regardless of hazard)
        """
        inp = SprinklerInput(
            region="europe", occupancy_hazard="LH",
            area_protected_m2=200, ceiling_height_m=3.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        assert abs(r.design_flow_l_min - 189.0) < 5, (
            f"LH: Q_design expected 189 L/min (2.25x84), got {r.design_flow_l_min}"
        )
        assert r.supply_duration_min == 30  # LH = 30 min

    def test_eh1_design_flow_1950_l_min(self):
        """
        EH1: density=7.5 L/min/m2, area=260 m2
        Q_design = 7.5 x 260 = 1950 L/min
        """
        inp = SprinklerInput(
            region="gcc", occupancy_hazard="EH1",
            area_protected_m2=1000, ceiling_height_m=6.0,
            sprinkler_coverage_m2=9.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        assert abs(r.design_flow_l_min - 1950.0) < 10, (
            f"EH1: Q_design expected 1950 L/min (7.5x260), got {r.design_flow_l_min}"
        )
        assert r.supply_duration_min == 90  # EH1 = 90 min


class TestSprinklerKFactorAndPressure:
    """
    BS EN 12845 Sec 10.2.4 — K-factor equation: Q = K x sqrt(P)
    Therefore: P = (Q/K)^2  [bar]
    """

    def test_oh2_residual_pressure_k80(self):
        """
        OH2, K=80: q_per = 60 L/min
        P_residual = (60/80)^2 = 0.5625 bar
        """
        inp = SprinklerInput(
            region="gcc", occupancy_hazard="OH2",
            area_protected_m2=800, ceiling_height_m=5.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        # q_per = 1800/30 = 60 L/min; P = (60/80)^2 = 0.5625 bar
        assert abs(r.residual_pressure_bar - 0.5625) < 0.05, (
            f"P_residual expected 0.5625 bar (60/80)^2, got {r.residual_pressure_bar}"
        )

    def test_oh1_k115_residual_pressure(self):
        """
        OH1, K=115: n=ceil(216/12)=18, q_per=1080/18=60 L/min
        P = (60/115)^2 = 0.272 bar  -> rounded up to 0.50 bar minimum
        """
        inp = SprinklerInput(
            region="australia", occupancy_hazard="OH1",
            area_protected_m2=400, ceiling_height_m=3.5,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=115,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        expected_p = max((60.0 / 115) ** 2, 0.5)
        assert abs(r.residual_pressure_bar - expected_p) < 0.1


class TestSprinklerTankCapacity:
    """
    Tank capacity (m3) = Q_total (L/min) x duration (min) / 1000 x 1.1
    (10% safety margin per BS EN 12845 Sec 13.2)
    """

    def test_oh1_tank_capacity(self):
        """
        OH1: Q_total=1680 L/min, duration=60 min
        Tank = 1680 x 60 / 1000 x 1.1 = 110.9 m3
        """
        inp = SprinklerInput(
            region="europe", occupancy_hazard="OH1",
            area_protected_m2=500, ceiling_height_m=4.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        expected_tank = (1680 * 60 / 1000) * 1.1  # = 110.88 m3
        assert abs(r.tank_capacity_m3 - expected_tank) < 5.0, (
            f"OH1 tank: expected ~{expected_tank:.1f} m3, got {r.tank_capacity_m3}"
        )

    def test_oh2_tank_capacity(self):
        """
        OH2: Q_total=2400 L/min, duration=60 min
        Tank = 2400 x 60 / 1000 x 1.1 = 158.4 m3
        """
        inp = SprinklerInput(
            region="gcc", occupancy_hazard="OH2",
            area_protected_m2=800, ceiling_height_m=5.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        expected_tank = (2400 * 60 / 1000) * 1.1  # = 158.4 m3
        assert abs(r.tank_capacity_m3 - expected_tank) < 5.0, (
            f"OH2 tank: expected ~{expected_tank:.1f} m3, got {r.tank_capacity_m3}"
        )

    def test_eh1_tank_capacity_90_min(self):
        """
        EH1: Q_total=1950+600=2550 L/min, duration=90 min
        Tank = 2550 x 90 / 1000 x 1.1 = 252.5 m3
        """
        inp = SprinklerInput(
            region="gcc", occupancy_hazard="EH1",
            area_protected_m2=1000, ceiling_height_m=6.0,
            sprinkler_coverage_m2=9.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        expected_tank = (2550 * 90 / 1000) * 1.1  # = 252.45 m3
        assert abs(r.tank_capacity_m3 - expected_tank) < 10.0


class TestSprinklerStandardCitationsAllRegions:
    """Verify the correct design standard is cited for each region."""

    @pytest.mark.parametrize("region,expected_standard", [
        ("gcc",       "BS EN 12845:2015 / NFPA 13 (2022 Ed.) / Civil Defence"),
        ("europe",    "BS EN 12845:2015 / BS 9251"),
        ("india",     "IS 15105:2002 / NBC 2016 Part 4 / TAC"),
        ("australia", "AS 2118.1:2017 / AS 2118.6"),
    ])
    def test_standard_citation_per_region(self, region, expected_standard):
        inp = SprinklerInput(
            region=region, occupancy_hazard="OH1",
            area_protected_m2=300, ceiling_height_m=4.0,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        assert r.design_standard == expected_standard, (
            f"Region {region}: expected '{expected_standard}', got '{r.design_standard}'"
        )

    @pytest.mark.parametrize("region", ["gcc", "europe", "india", "australia"])
    def test_all_regions_produce_valid_output(self, region):
        """Every region must return a physically valid sprinkler design."""
        inp = SprinklerInput(
            region=region, occupancy_hazard="OH2",
            area_protected_m2=600, ceiling_height_m=4.5,
            sprinkler_coverage_m2=12.0, sprinkler_k_factor=80,
            hose_allowance_l_min=600,
        )
        r = calculate_sprinkler(inp)
        assert r.design_flow_l_min > 0
        assert r.total_system_flow_l_min > r.design_flow_l_min
        assert r.pump_power_kw > 0
        assert r.tank_capacity_m3 > 0
        assert r.num_sprinklers_design_area > 0
        assert r.residual_pressure_bar >= 0.5  # BS EN 12845 minimum 0.5 bar
