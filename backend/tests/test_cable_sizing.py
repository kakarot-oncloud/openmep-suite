"""
Comprehensive unit tests for the cable sizing calculation engine.
All reference values are traceable to published standards:

  BS 7671:2018+A2:2022
    - Table 4D5A: XLPE/Cu multicore current ratings (A), reference 30 deg C
    - Table 4D2A: PVC/Cu multicore current ratings (A), reference 30 deg C
    - Table 4B1:  Ambient temperature correction factor Ca (XLPE and PVC)
    - Table 4C1:  Grouping correction factor Cg (cables touching / spaced)
    - Appendix 4: Voltage drop mV/A/m for multicore XLPE/Cu and PVC/Cu

  IS 3961 (Part 5):2004 / IS 732:2019 — India region
  AS/NZS 3008.1.1:2017              — Australia region

Cable sizing selection rule (BS 7671 Sec 523 / Clause 6):
  Iz_required = Ib / (Ca x Cg x Cc)
  Voltage drop check: VD% = (Z x Ib x L / 1000) / Vs x 100
  Where Z is mV/A/m from the applicable standard table.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from backend.engines.electrical.cable_sizing import CableSizingInput, calculate_cable_sizing


# ─── GCC Region — BS 7671:2018+A2:2022 + GCC design conditions ───────────────

class TestGCCCableSizingReferenceValues:
    """
    GCC region: 50 deg C air ambient, 35 deg C ground.
    Supply voltage: 415 V three-phase, 240 V single-phase.
    VD limits: 4% power, 3% lighting (DEWA/ADDC/KAHRAMAA).
    """

    def test_gcc_45kw_3ph_method_c_50degc_100m(self):
        """
        45 kW, 3-phase, 415 V, PF=0.85, XLPE/Cu, method C, 50 deg C, 100 m.

        Hand calculation traceable to BS 7671:
          Ib = 45000 / (sqrt(3) x 415 x 0.85)           = 73.53 A
          Ca (50 deg C, XLPE, Table 4B1)                 = 0.82
          Cg (1 circuit)                                  = 1.00
          Iz_req = 73.53 / (0.82 x 1.00)                 = 89.67 A

          16 mm2 method C (Table 4D5A) = 102 A -> derated = 83.6 A  (<89.67: FAIL)
          25 mm2 method C              = 133 A -> derated = 109.1 A (>89.67: PASS)
          VD check 16 mm2: 2.8 mV/A/m x 73.53 x 100/1000 = 20.6 V = 4.97% -> FAIL >4%
          VD check 25 mm2: 1.75 x 73.53 x 100/1000       = 12.9 V = 3.10% -> PASS
          SELECTED: 25 mm2  (voltage drop is the governing criterion)
        """
        inp = CableSizingInput(
            region="gcc", sub_region="dewa",
            load_kw=45, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=100, ambient_temp_c=50,
            num_grouped_circuits=1, circuit_type="power",
        )
        r = calculate_cable_sizing(inp)
        # Design current
        assert abs(r.design_current_ib_a - 73.53) < 0.5, f"Ib {r.design_current_ib_a} != ~73.5 A"
        # Ca factor — BS 7671 Table 4B1 at 50 deg C XLPE
        assert abs(r.ca_factor - 0.82) < 0.01, f"Ca {r.ca_factor} != 0.82"
        # No grouping derating
        assert r.cg_factor == 1.0
        # VD must be within 4% limit (DEWA power)
        assert r.voltage_drop_pct < 4.0, f"VD {r.voltage_drop_pct}% exceeds 4% limit"
        # Cable must be at least 25 mm2 due to VD requirement
        assert r.selected_size_mm2 >= 25, f"Selected {r.selected_size_mm2} mm2; VD forces min 25 mm2"
        # Derated capacity must cover design current
        assert r.derated_rating_iz_a >= r.design_current_ib_a

    def test_gcc_15kw_3ph_method_e_45degc_3cables_grouped(self):
        """
        15 kW, 3-phase, 415 V, PF=0.90, XLPE/Cu, method E, 45 deg C, 50 m, 3 cables grouped.

        Hand calculation:
          Ib = 15000 / (sqrt(3) x 415 x 0.90)       = 23.18 A
          Ca (45 deg C, XLPE, Table 4B1)              = 0.87
          Cg (3 cables, touching, Table 4C1)          = 0.70
          Iz_req = 23.18 / (0.87 x 0.70)             = 38.04 A

          4 mm2 method E (Table 4D5A) = 52 A -> derated = 52 x 0.87 x 0.70 = 31.7 A  FAIL
          6 mm2 method E              = 65 A -> derated = 65 x 0.87 x 0.70 = 39.6 A  PASS
          VD 6 mm2: 7.3 mV/A/m x 23.18 x 50/1000 = 8.46 V = 2.04%  PASS <4%
          SELECTED: 6 mm2
        """
        inp = CableSizingInput(
            region="gcc", load_kw=15, power_factor=0.90, phases=3,
            cable_type="XLPE_CU", installation_method="E",
            cable_length_m=50, ambient_temp_c=45,
            num_grouped_circuits=3, circuit_type="power",
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - 23.18) < 0.5
        assert abs(r.ca_factor - 0.87) < 0.01,  f"Ca {r.ca_factor} != 0.87 (Table 4B1, 45 deg C)"
        assert abs(r.cg_factor - 0.70) < 0.01,  f"Cg {r.cg_factor} != 0.70 (Table 4C1, 3 circuits)"
        assert r.selected_size_mm2 == 6
        assert r.voltage_drop_pct < 4.0

    def test_gcc_ca_factor_table_4B1_xlpe_spot_checks(self):
        """
        BS 7671 Table 4B1 — Ambient temperature correction factor Ca.
        XLPE/EPR (90 deg C rated), reference temperature 30 deg C.
        """
        from backend.adapters.gcc.electrical_adapter import GCCElectricalAdapter
        a = GCCElectricalAdapter()
        # Table 4B1 selected rows (XLPE/EPR column):
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 30) - 1.00) < 0.001  # reference temp
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 35) - 0.96) < 0.01
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 40) - 0.91) < 0.01
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 45) - 0.87) < 0.01
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 50) - 0.82) < 0.01
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 55) - 0.76) < 0.01
        assert abs(a.get_ambient_temp_correction("XLPE_CU", 60) - 0.71) < 0.01

    def test_gcc_ca_factor_table_4B1_pvc_spot_checks(self):
        """
        BS 7671 Table 4B1 — Ca for PVC/thermoplastic (70 deg C rated), reference 30 deg C.
        """
        from backend.adapters.gcc.electrical_adapter import GCCElectricalAdapter
        a = GCCElectricalAdapter()
        assert abs(a.get_ambient_temp_correction("PVC_CU", 30) - 1.00) < 0.001
        assert abs(a.get_ambient_temp_correction("PVC_CU", 40) - 0.87) < 0.01
        assert abs(a.get_ambient_temp_correction("PVC_CU", 45) - 0.79) < 0.01
        assert abs(a.get_ambient_temp_correction("PVC_CU", 50) - 0.71) < 0.01

    def test_gcc_cg_factor_table_4C1_touching_cables(self):
        """
        BS 7671 Table 4C1 — Grouping factor Cg, cables touching (bundled).
        Reference: 18th Edition Table 4C1, row 'Clipped direct or on trays'.
        """
        from backend.adapters.gcc.electrical_adapter import GCCElectricalAdapter
        a = GCCElectricalAdapter()
        assert abs(a.get_grouping_correction(1, touching=True) - 1.00) < 0.001
        assert abs(a.get_grouping_correction(2, touching=True) - 0.80) < 0.01
        assert abs(a.get_grouping_correction(3, touching=True) - 0.70) < 0.01
        assert abs(a.get_grouping_correction(4, touching=True) - 0.65) < 0.01
        assert abs(a.get_grouping_correction(5, touching=True) - 0.60) < 0.01
        assert abs(a.get_grouping_correction(6, touching=True) - 0.57) < 0.01
        assert abs(a.get_grouping_correction(9, touching=True) - 0.50) < 0.01

    def test_gcc_current_ratings_table_4D5A_method_c(self):
        """
        BS 7671 Table 4D5A col C — XLPE/Cu multicore, clipped direct, amperes at 30 deg C.
        Published values: 16=102, 25=133, 35=163, 50=198, 70=253, 95=306, 120=354 A.
        """
        from backend.adapters.gcc.electrical_adapter import GCCElectricalAdapter
        a = GCCElectricalAdapter()
        ratings_c = {16: 102, 25: 133, 35: 163, 50: 198, 70: 253, 95: 306, 120: 354}
        for size_mm2, expected_a in ratings_c.items():
            got = a.get_current_rating("XLPE_CU", "C", float(size_mm2))
            assert abs(got - expected_a) < 2, (
                f"BS 7671 Table 4D5A col C: {size_mm2} mm2 expected {expected_a} A, got {got:.1f} A"
            )

    def test_gcc_current_ratings_table_4D2A_method_c_pvc(self):
        """
        BS 7671 Table 4D2A col C — PVC/Cu multicore, clipped direct, amperes at 30 deg C.
        Published values: 16=85, 25=110, 35=135, 50=163, 95=250 A.
        """
        from backend.adapters.gcc.electrical_adapter import GCCElectricalAdapter
        a = GCCElectricalAdapter()
        ratings_pvc = {16: 85, 25: 110, 35: 135, 50: 163, 95: 250}
        for size_mm2, expected_a in ratings_pvc.items():
            got = a.get_current_rating("PVC_CU", "C", float(size_mm2))
            assert abs(got - expected_a) < 2, (
                f"BS 7671 Table 4D2A col C: {size_mm2} mm2 expected {expected_a} A, got {got:.1f} A"
            )

    def test_gcc_voltage_drop_limit_power_4pct(self):
        """DEWA/GCC power circuit VD limit must be exactly 4.0%."""
        inp = CableSizingInput(
            region="gcc", sub_region="dewa",
            load_kw=10, power_factor=0.9, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=10, ambient_temp_c=35, num_grouped_circuits=1,
            circuit_type="power",
        )
        r = calculate_cable_sizing(inp)
        assert r.voltage_drop_limit_pct == 4.0

    def test_gcc_voltage_drop_limit_lighting_3pct(self):
        """DEWA/GCC lighting circuit VD limit must be exactly 3.0%."""
        inp = CableSizingInput(
            region="gcc", sub_region="dewa",
            load_kw=2, power_factor=1.0, phases=1,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=10, ambient_temp_c=35, num_grouped_circuits=1,
            circuit_type="lighting",
        )
        r = calculate_cable_sizing(inp)
        assert r.voltage_drop_limit_pct == 3.0

    def test_gcc_supply_voltage_415v_three_phase(self):
        """GCC three-phase supply voltage is 415 V per DEWA/ADDC/KAHRAMAA/SEC specifications."""
        inp = CableSizingInput(
            region="gcc", load_kw=30, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=50, ambient_temp_c=40, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert r.supply_voltage_v == 415


# ─── Europe Region — BS 7671:2018+A2:2022 (UK/EU edition) ───────────────────

class TestEuropeCableSizingReferenceValues:
    """
    Europe region: 30 deg C reference ambient, 400 V three-phase (UK: 230/400 V).
    VD limit: 4% total from origin (BS 7671 Appendix 12).
    """

    def test_europe_small_office_circuit_5kw(self):
        """
        5 kW, 3-phase, 400 V, PF=0.95, XLPE/Cu, method C, 30 deg C, 30 m.

        Ib = 5000 / (sqrt(3) x 400 x 0.95)    = 7.60 A
        Ca = 1.00 (30 deg C reference)
        2.5 mm2 method C -> 34 A >= 7.60 A PASS
        VD 2.5 mm2: 18 mV/A/m x 7.60 x 30/1000 = 4.10 V = 1.03%  PASS
        SELECTED: 2.5 mm2 (or 4 mm2 if additional margin enforced)
        """
        inp = CableSizingInput(
            region="europe", load_kw=5, power_factor=0.95, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=30, ambient_temp_c=30, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - 7.60) < 0.3
        assert r.ca_factor == 1.0
        assert r.selected_size_mm2 in [2.5, 4]
        assert r.voltage_drop_pct < 4.0

    def test_europe_60kw_feeder_vd_drives_upsizing(self):
        """
        60 kW, 3-phase, 400 V, PF=0.92, XLPE/Cu, method C, 30 deg C, 80 m.

        Ib = 60000 / (sqrt(3) x 400 x 0.92)   = 94.3 A
        16 mm2 method C = 102 A >= 94.3 A  (current OK)
        VD 16 mm2: 2.8 x 94.3 x 80/1000 = 21.1 V = 5.27%  FAIL >4%
        25 mm2:    1.75 x 94.3 x 80/1000 = 13.2 V = 3.30%  PASS
        SELECTED: 25 mm2  (voltage drop is the governing criterion)
        """
        inp = CableSizingInput(
            region="europe", load_kw=60, power_factor=0.92, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=80, ambient_temp_c=30, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - 94.3) < 1.0
        assert r.selected_size_mm2 == 25, "VD governs: 16 mm2 gives 5.27%, must upsize to 25 mm2"
        assert r.voltage_drop_pct < 4.0

    def test_europe_vd_table_mva_per_m_spot_checks(self):
        """
        BS 7671 Appendix 4 Table 4D5B — voltage drop mV/A/m (XLPE/Cu multicore).
        Selected reference values for 3-phase circuits at 90 deg C conductor.
        """
        from backend.adapters.europe.electrical_adapter import EuropeElectricalAdapter
        a = EuropeElectricalAdapter()
        vd_refs = {
            6: 7.3, 10: 4.4, 16: 2.8, 25: 1.75,
            35: 1.25, 50: 0.93, 70: 0.63, 95: 0.47,
        }
        for size_mm2, expected_mv in vd_refs.items():
            got = a.get_voltage_drop_mv_am("XLPE_CU", float(size_mm2), phases=3)
            assert abs(got - expected_mv) < 0.15, (
                f"BS 7671 Table 4D5B: {size_mm2} mm2 expected {expected_mv} mV/A/m, got {got:.3f}"
            )


# ─── India Region — IS 3961 (Part 5):2004 / IS 732:2019 ─────────────────────

class TestIndiaCableSizingReferenceValues:
    """
    India region: 40 deg C ambient (IS 3961 reference), 415 V three-phase.
    VD limit: IS 732:2019 Cl 5.4 — 3% lighting, 5% power (from supply origin).
    """

    def test_india_20kw_3ph_method_c_40degc(self):
        """
        20 kW, 3-phase, 415 V, PF=0.85, XLPE/Cu, method C, 40 deg C, 60 m.

        Ib = 20000 / (sqrt(3) x 415 x 0.85)   = 32.68 A
        Ca (40 deg C, XLPE per IS 3961) ~= 0.91 (identical to BS 7671 Table 4B1)
        Iz_req = 32.68 / 0.91                   = 35.91 A
        6 mm2 method C -> 57 A; derated = 57 x 0.91 = 51.9 A >= 35.91 A  PASS
        VD: 7.3 x 32.68 x 60/1000 = 14.3 V = 3.45%  PASS (<5% IS 732 power limit)
        SELECTED: 6 mm2 (or 4 mm2 if exact IS table differs slightly)
        """
        inp = CableSizingInput(
            region="india", load_kw=20, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=60, ambient_temp_c=40, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - 32.68) < 0.5
        assert r.ca_factor < 1.0, "40 deg C derating must apply (ca < 1.0)"
        assert r.selected_size_mm2 in [4, 6]
        # IS 732 power VD limit is 5% (from supply origin)
        assert r.voltage_drop_pct < 5.0

    def test_india_vd_limit_is732_power_5pct(self):
        """IS 732:2019 Clause 5.4: max voltage drop 5% for power circuits."""
        inp = CableSizingInput(
            region="india", load_kw=10, power_factor=0.9, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=50, ambient_temp_c=35, num_grouped_circuits=1,
            circuit_type="power",
        )
        r = calculate_cable_sizing(inp)
        assert r.voltage_drop_limit_pct <= 5.0

    def test_india_vd_limit_is732_lighting_3pct(self):
        """IS 732:2019 Clause 5.4: max voltage drop 3% for lighting circuits."""
        inp = CableSizingInput(
            region="india", load_kw=1, power_factor=1.0, phases=1,
            cable_type="PVC_CU", installation_method="C",
            cable_length_m=20, ambient_temp_c=35, num_grouped_circuits=1,
            circuit_type="lighting",
        )
        r = calculate_cable_sizing(inp)
        assert r.voltage_drop_limit_pct <= 3.0

    def test_india_single_phase_lighting_minimum_size(self):
        """IS 732 Clause 5.1: minimum conductor size 1.5 mm2 for lighting final circuits."""
        inp = CableSizingInput(
            region="india", load_kw=0.8, power_factor=1.0, phases=1,
            cable_type="PVC_CU", installation_method="C",
            cable_length_m=15, ambient_temp_c=35, num_grouped_circuits=1,
            circuit_type="lighting",
        )
        r = calculate_cable_sizing(inp)
        assert r.selected_size_mm2 >= 1.5


# ─── Australia Region — AS/NZS 3008.1.1:2017 ─────────────────────────────────

class TestAustraliaCableSizingReferenceValues:
    """
    Australia/NZ region: AS/NZS 3008.1.1:2017.
    VD limit: AS/NZS 3008.1.1 Clause 4.6 — 5% maximum from origin.
    Supply: 415 V three-phase (AS/NZS 3000:2018 Cl 2.2.1).
    """

    def test_australia_25kw_method_c_40degc_vd_governs(self):
        """
        25 kW, 3-phase, 415 V, PF=0.88, XLPE/Cu, method C, 40 deg C, 70 m.

        Ib = 25000 / (sqrt(3) x 415 x 0.88)    = 39.55 A
        Ca (40 deg C) ~= 0.91 (AS/NZS 3008 Table 22 equivalent)
        Iz_req = 39.55 / 0.91                    = 43.46 A
        6 mm2 -> 57 A; derated = 51.9 A >= 43.46 A  PASS (current)
        VD 6 mm2: 7.3 x 39.55 x 70/1000 = 20.2 V = 4.87%  PASS (<5% AS limit)
        SELECTED: 6 mm2 (or 10 mm2 if additional margin applies)
        """
        inp = CableSizingInput(
            region="australia", load_kw=25, power_factor=0.88, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=70, ambient_temp_c=40, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - 39.55) < 0.5
        assert r.ca_factor < 1.0
        assert r.selected_size_mm2 in [6, 10]
        # AS/NZS 3008.1.1 Clause 4.6: VD <= 5%
        assert r.voltage_drop_pct < 5.0

    def test_australia_vd_limit_5pct_asnzs3008(self):
        """AS/NZS 3008.1.1:2017 Clause 4.6: maximum permitted voltage drop is 5%."""
        inp = CableSizingInput(
            region="australia", load_kw=20, power_factor=0.9, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=40, ambient_temp_c=30, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert r.voltage_drop_pct < 5.0
        assert r.voltage_drop_limit_pct <= 5.0

    def test_australia_supply_voltage_415v(self):
        """AS/NZS 3000:2018 Clause 2.2.1: nominal supply voltage 415 V three-phase."""
        inp = CableSizingInput(
            region="australia", load_kw=15, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=30, ambient_temp_c=30, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert r.supply_voltage_v == 415


# ─── Cross-region edge cases and output structure validation ──────────────────

class TestCableSizingAllRegions:
    """Parametrized smoke tests ensuring all 4 regions produce valid results."""

    @pytest.mark.parametrize("region,ambient,voltage", [
        ("gcc",       50, 415),
        ("europe",    30, 400),
        ("india",     40, 415),
        ("australia", 35, 415),
    ])
    def test_all_regions_produce_valid_output(self, region, ambient, voltage):
        """Every region must return a physically valid cable selection."""
        inp = CableSizingInput(
            region=region, load_kw=30, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=50, ambient_temp_c=ambient, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        # Physical validity checks
        assert r.design_current_ib_a > 0
        assert r.selected_size_mm2 > 0
        assert r.derated_rating_iz_a >= r.design_current_ib_a, (
            f"{region}: derated Iz ({r.derated_rating_iz_a:.1f} A) < Ib ({r.design_current_ib_a:.1f} A)"
        )
        assert 0 < r.ca_factor <= 1.0
        assert 0 < r.cg_factor <= 1.0
        assert r.voltage_drop_pct > 0
        assert r.voltage_drop_pct < r.voltage_drop_limit_pct

    def test_design_current_formula_three_phase(self):
        """Verify three-phase design current formula: Ib = kW / (sqrt(3) x V x PF)."""
        kw, pf, v = 50.0, 0.85, 415.0
        expected_ib = kw * 1000 / (math.sqrt(3) * v * pf)
        inp = CableSizingInput(
            region="gcc", load_kw=kw, power_factor=pf, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=30, ambient_temp_c=30, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - expected_ib) < 0.5

    def test_design_current_formula_single_phase(self):
        """Verify single-phase design current formula: Ib = kW / (V x PF)."""
        kw, pf, v = 5.0, 0.95, 240.0
        expected_ib = kw * 1000 / (v * pf)
        inp = CableSizingInput(
            region="gcc", load_kw=kw, power_factor=pf, phases=1,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=20, ambient_temp_c=30, num_grouped_circuits=1,
        )
        r = calculate_cable_sizing(inp)
        assert abs(r.design_current_ib_a - expected_ib) < 0.5

    def test_grouping_increases_required_cable_size(self):
        """Grouping derating (Cg < 1) must force a larger cable size than no grouping."""
        base = dict(
            region="gcc", load_kw=20, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=40, ambient_temp_c=40,
        )
        r_single = calculate_cable_sizing(CableSizingInput(**base, num_grouped_circuits=1))
        r_grouped = calculate_cable_sizing(CableSizingInput(**base, num_grouped_circuits=6))
        assert r_grouped.selected_size_mm2 >= r_single.selected_size_mm2, (
            "Grouping 6 circuits must require same or larger cable than single circuit"
        )

    def test_higher_ambient_increases_cable_size_or_equal(self):
        """Higher ambient derating must require same or larger cable size."""
        base = dict(
            region="gcc", load_kw=30, power_factor=0.85, phases=3,
            cable_type="XLPE_CU", installation_method="C",
            cable_length_m=50, num_grouped_circuits=1,
        )
        r_30 = calculate_cable_sizing(CableSizingInput(**base, ambient_temp_c=30))
        r_50 = calculate_cable_sizing(CableSizingInput(**base, ambient_temp_c=50))
        assert r_50.selected_size_mm2 >= r_30.selected_size_mm2
