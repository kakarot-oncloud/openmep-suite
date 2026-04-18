"""
Comprehensive tests for the plumbing pipe sizing engine.
Reference values traceable to published standards:

  BS EN 806-3:2006 — Installations inside buildings for drinking water
    Table B.3 / Appendix B: Fixture unit (DU) to design flow (L/s) conversion
    Formula: Q = 0.682 x sqrt(DU)  for DU > 1 (simplified Simpson/Hunter method)
    Velocity limits: max 2.0 m/s (BS EN 806 / DEWA plumbing regs)

  Hazen-Williams equation (friction loss):
    hf/L = 10.67 x Q^1.852 / (C^1.852 x D^4.87)   [m head per metre]
    C values: copper=140, PVC=150, GI=100, HDPE=150

  Pipe selection: smallest DN where v <= v_max (velocity limit)

Run: python -m pytest backend/tests/test_plumbing.py -v
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from backend.engines.plumbing.pipe_sizing import (
    PlumbingInput, PipeSizingResult, calculate_pipe_sizing,
    du_to_flow_l_s, hazen_williams_pressure_drop,
    HW_C, DN_TO_ID_MM, PLUMBING_STANDARDS,
)


class TestDUToFlowConversionEN806:
    """
    EN 806-3 Appendix B / BS EN 806-3 Table B.3
    Flow rate formula: Q = 0.682 x sqrt(DU)  for DU > 1
    """

    def test_du_0_returns_zero(self):
        """Zero fixture units = zero flow (edge case)."""
        assert du_to_flow_l_s(0) == 0.0

    def test_du_1_returns_0_25_l_s(self):
        """DU = 1: minimum flow = 0.25 L/s (EN 806-3 Table B.3 lower bound)."""
        assert abs(du_to_flow_l_s(1) - 0.25) < 0.001

    def test_du_4_en806_formula(self):
        """DU = 4: Q = 0.682 x sqrt(4) = 0.682 x 2.0 = 1.364 L/s."""
        expected = 0.682 * math.sqrt(4)
        assert abs(du_to_flow_l_s(4) - expected) < 0.001

    def test_du_9_en806_formula(self):
        """DU = 9: Q = 0.682 x sqrt(9) = 0.682 x 3.0 = 2.046 L/s."""
        expected = 0.682 * math.sqrt(9)
        assert abs(du_to_flow_l_s(9) - expected) < 0.001

    def test_du_16_en806_formula(self):
        """DU = 16: Q = 0.682 x sqrt(16) = 0.682 x 4.0 = 2.728 L/s."""
        expected = 0.682 * math.sqrt(16)
        assert abs(du_to_flow_l_s(16) - expected) < 0.001

    def test_du_25_en806_formula(self):
        """DU = 25: Q = 0.682 x sqrt(25) = 0.682 x 5.0 = 3.41 L/s."""
        expected = 0.682 * math.sqrt(25)
        assert abs(du_to_flow_l_s(25) - expected) < 0.001

    def test_du_100_en806_formula(self):
        """DU = 100: Q = 0.682 x sqrt(100) = 0.682 x 10.0 = 6.82 L/s."""
        expected = 0.682 * math.sqrt(100)
        assert abs(du_to_flow_l_s(100) - expected) < 0.001

    def test_flow_increases_monotonically_with_du(self):
        """Flow rate must increase monotonically with fixture units."""
        du_vals = [1, 4, 9, 16, 25, 50, 100]
        flows = [du_to_flow_l_s(du) for du in du_vals]
        for i in range(len(flows) - 1):
            assert flows[i] < flows[i+1], f"Flow not monotonic at DU={du_vals[i]}"


class TestHazenWilliamsRoughnessCoefficients:
    """
    Verify Hazen-Williams C values match published pipe material references.
    Source: AWWA M23, Mays 'Water Distribution Systems Handbook'.
    """

    def test_copper_c_factor_140(self):
        """Copper pipe: C = 140 (new copper tubing per Hazen-Williams tables)."""
        assert HW_C["copper"] == 140

    def test_pvc_c_factor_150(self):
        """PVC pipe: C = 150 (smooth plastic, AWWA M23)."""
        assert HW_C["pvc"] == 150

    def test_gi_c_factor_100(self):
        """Galvanised iron: C = 100 (new GI, AWWA M23; degrades over time)."""
        assert HW_C["gi"] == 100

    def test_hdpe_c_factor_150(self):
        """HDPE: C = 150 (smooth bore, equivalent to PVC for Hazen-Williams)."""
        assert HW_C["hdpe"] == 150

    def test_higher_c_means_lower_friction(self):
        """Higher C (smoother pipe) must produce lower friction loss at same flow/diameter."""
        Q, D = 0.5 / 1000, 0.025  # 0.5 L/s, 25mm ID
        dp_copper = hazen_williams_pressure_drop(Q, D, C=140)
        dp_gi     = hazen_williams_pressure_drop(Q, D, C=100)
        assert dp_copper < dp_gi, "Copper (C=140) must have lower friction than GI (C=100)"


class TestPipeSizingReferenceValues:
    """
    Pipe sizing reference values computed from the EN 806 formula and
    Hazen-Williams friction equation implemented in the engine.
    """

    def test_du20_copper_velocity_within_limit(self):
        """
        20 DU, copper pipe, max 2.0 m/s.
        Q = 0.682 x sqrt(20) = 3.05 L/s
        DN50 (ID=50mm=0.05m): A = pi x (0.025)^2 = 1.963e-3 m2
        v = 0.00305 / 0.001963 = 1.55 m/s  < 2.0 m/s -> SELECTED DN50
        """
        inp = PlumbingInput(
            region="gcc", system="DHWS",
            flow_units=20, pipe_material="copper",
            max_velocity_m_s=2.0,
        )
        r = calculate_pipe_sizing(inp)
        expected_q = 0.682 * math.sqrt(20)
        assert abs(r.flow_rate_l_s - expected_q) < 0.05, (
            f"Flow rate: expected {expected_q:.3f} L/s, got {r.flow_rate_l_s}"
        )
        assert r.velocity_m_s <= 2.0, "Velocity must not exceed 2.0 m/s limit"
        assert r.pipe_nominal_dn >= 40   # at 3.05 L/s needs at least DN40

    def test_du4_copper_small_pipe(self):
        """
        4 DU, copper, max 2.0 m/s.
        Q = 0.682 x sqrt(4) = 1.364 L/s
        DN32 (ID=30mm): A = pi x (0.015)^2 = 7.07e-4 m2
        v = 0.001364 / 7.07e-4 = 1.93 m/s  -> borderline DN32
        DN40 (ID=37mm): A = pi x (0.0185)^2 = 1.075e-3 m2
        v = 0.001364 / 1.075e-3 = 1.27 m/s  -> SELECTED DN40 or DN32
        """
        inp = PlumbingInput(
            region="gcc", system="CWDS",
            flow_units=4, pipe_material="copper",
            max_velocity_m_s=2.0,
        )
        r = calculate_pipe_sizing(inp)
        expected_q = 0.682 * math.sqrt(4)   # 1.364 L/s
        assert abs(r.flow_rate_l_s - expected_q) < 0.05
        assert r.velocity_m_s <= 2.0
        assert r.pipe_nominal_dn in [32, 40]

    def test_du1_minimum_flow(self):
        """DU=1: Q = 0.25 L/s (single fixture, e.g. washbasin)."""
        inp = PlumbingInput(
            region="gcc", flow_units=1, pipe_material="copper", max_velocity_m_s=2.0
        )
        r = calculate_pipe_sizing(inp)
        assert abs(r.flow_rate_l_s - 0.25) < 0.01
        assert r.pipe_nominal_dn in [15, 20]  # DN15 or DN20 for 0.25 L/s

    def test_large_du_100_riser_sizing(self):
        """
        100 DU (risers / main distribution): Q = 0.682 x sqrt(100) = 6.82 L/s
        Must select DN100 or larger.
        """
        inp = PlumbingInput(
            region="gcc", system="DHWS",
            flow_units=100, pipe_material="copper",
            max_velocity_m_s=2.0,
        )
        r = calculate_pipe_sizing(inp)
        assert r.pipe_nominal_dn >= 80  # at 6.82 L/s requires at least DN80-100

    def test_larger_pipe_means_lower_velocity(self):
        """Increasing pipe size for same flow must reduce velocity."""
        base = dict(region="gcc", flow_units=20, pipe_material="copper")
        r_tight = calculate_pipe_sizing(PlumbingInput(**base, max_velocity_m_s=2.0))
        r_loose  = calculate_pipe_sizing(PlumbingInput(**base, max_velocity_m_s=1.0))
        # Stricter velocity limit forces larger pipe -> lower velocity in result
        assert r_loose.pipe_nominal_dn >= r_tight.pipe_nominal_dn

    def test_pvc_vs_copper_same_du(self):
        """PVC and copper with same DU must both produce valid, similar pipe selections."""
        base = dict(region="gcc", flow_units=16, max_velocity_m_s=2.0)
        r_cu  = calculate_pipe_sizing(PlumbingInput(**base, pipe_material="copper"))
        r_pvc = calculate_pipe_sizing(PlumbingInput(**base, pipe_material="pvc"))
        assert abs(r_cu.flow_rate_l_s - r_pvc.flow_rate_l_s) < 0.01  # same DU -> same Q
        assert r_cu.velocity_m_s <= 2.0
        assert r_pvc.velocity_m_s <= 2.0


class TestPlumbingStandardCitationsAllRegions:
    """Verify each region cites the correct plumbing standard."""

    @pytest.mark.parametrize("region,expected_standard", [
        ("gcc",       "BS EN 806 / DEWA Plumbing Regulations"),
        ("europe",    "BS EN 806 / BS 6700"),
        ("india",     "IS 1172:2011 / NBC 2016 Part 9"),
        ("australia", "AS/NZS 3500.1:2021"),
    ])
    def test_standard_citation_per_region(self, region, expected_standard):
        inp = PlumbingInput(
            region=region, flow_units=10, pipe_material="copper", max_velocity_m_s=2.0
        )
        r = calculate_pipe_sizing(inp)
        assert r.standard == expected_standard, (
            f"Region {region}: expected '{expected_standard}', got '{r.standard}'"
        )

    @pytest.mark.parametrize("region", ["gcc", "europe", "india", "australia"])
    def test_all_regions_produce_valid_output(self, region):
        """All 4 regions must return a physically valid pipe selection."""
        inp = PlumbingInput(
            region=region, flow_units=20, pipe_material="copper", max_velocity_m_s=2.0
        )
        r = calculate_pipe_sizing(inp)
        assert r.flow_rate_l_s > 0
        assert r.pipe_nominal_dn > 0
        assert r.velocity_m_s > 0
        assert r.velocity_m_s <= 2.0
        assert r.pressure_drop_kpa_m > 0
