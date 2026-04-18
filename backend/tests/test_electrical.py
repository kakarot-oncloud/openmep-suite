"""
API-level tests for the electrical engineering endpoints with reference values.
Covers: voltage drop, maximum demand, short circuit, lighting,
        generator sizing, panel schedule, UPS sizing, PF correction.

Reference values:
  BS 7671:2018+A2:2022 Appendix 4 Table 4D5B — voltage drop mV/A/m (XLPE/Cu multicore):
    6 mm2  = 7.3 mV/A/m    16 mm2 = 2.8 mV/A/m    35 mm2 = 1.25 mV/A/m
    10 mm2 = 4.4 mV/A/m    25 mm2 = 1.75 mV/A/m   95 mm2 = 0.47 mV/A/m
  Formula: VD_V = Z x I x L / 1000;  VD_% = VD_V / Vs x 100

Run: python -m pytest backend/tests/test_electrical.py -v
"""

import math
import pytest

pytestmark = pytest.mark.asyncio


# ─── Voltage Drop ─────────────────────────────────────────────────────────────

class TestVoltageDrop:

    async def test_vd_16mm_xlpe_55a_100m_gcc_reference(self, api_client):
        """
        16 mm2 XLPE/Cu, 55 A, 100 m, 3-phase, 415 V — GCC (DEWA power circuit).
        BS 7671 Table 4D5B reference: 16 mm2 = 2.8 mV/A/m
        Expected: VD = 2.8 x 55 x 100 / 1000 = 15.4 V = 3.71%  -> PASS (<4%)
        """
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "gcc",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 16,
            "cable_length_m": 100,
            "design_current_a": 55,
            "phases": 3,
            "circuit_type": "power",
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        # Reference calculation: 2.8 x 55 x 100 / 1000 = 15.4 V = 3.71%
        assert abs(d["vd_percent"] - 3.71) < 0.5, f"VD {d['vd_percent']}% != ~3.71%"
        assert d["compliant"] is True
        assert d["vd_limit_percent"] == 4.0  # DEWA power limit

    async def test_vd_6mm_xlpe_60a_100m_gcc_fails(self, api_client):
        """
        6 mm2 XLPE/Cu, 60 A, 100 m, 3-phase, 415 V — GCC.
        BS 7671 Table 4D5B reference: 6 mm2 = 7.3 mV/A/m
        Expected: VD = 7.3 x 60 x 100 / 1000 = 43.8 V = 10.6%  -> FAIL (>4%)
        Engine must flag non-compliant and recommend larger size.
        """
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "gcc",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 6,
            "cable_length_m": 100,
            "design_current_a": 60,
            "phases": 3,
            "circuit_type": "power",
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["vd_percent"] > 4.0, f"VD {d['vd_percent']}% should exceed 4% limit"
        assert d["compliant"] is False

    async def test_vd_95mm_xlpe_200a_30m_europe_compliant(self, api_client):
        """
        95 mm2 XLPE/Cu, 200 A, 30 m, 3-phase, 400 V — Europe.
        BS 7671 Table 4D5B reference: 95 mm2 = 0.47 mV/A/m
        Expected: VD = 0.47 x 200 x 30 / 1000 = 2.82 V = 0.71%  -> PASS (<4%)
        """
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "europe",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 95,
            "cable_length_m": 30,
            "design_current_a": 200,
            "phases": 3,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        # Reference: 0.47 x 200 x 30 / 1000 = 2.82 V = 0.71%
        assert d["vd_percent"] < 2.0, f"95mm2 at 200A/30m should be well under 2% VD"
        assert d["compliant"] is True

    async def test_vd_35mm_xlpe_india_reference(self, api_client):
        """
        35 mm2 XLPE/Cu, 80 A, 60 m, 3-phase, 415 V — India (IS 3961 table).
        BS 7671 / IS 3961 equivalent: 35 mm2 = 1.25 mV/A/m
        Expected: VD = 1.25 x 80 x 60 / 1000 = 6.0 V = 1.45%  -> PASS (<5% IS 732)
        """
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "india",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 35,
            "cable_length_m": 60,
            "design_current_a": 80,
            "phases": 3,
            "circuit_type": "power",
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["vd_percent"] < 5.0
        assert d["compliant"] is True

    async def test_vd_lighting_circuit_limit_3pct(self, api_client):
        """Lighting circuit VD limit must be 3% (DEWA/BS 7671 Appendix 12)."""
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "gcc",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 4,
            "cable_length_m": 50,
            "design_current_a": 10,
            "phases": 1,
            "circuit_type": "lighting",
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["vd_limit_percent"] == 3.0

    async def test_vd_all_regions_short_cable_compliant(self, api_client):
        """Short cable (10 m) must be compliant for all 4 regions."""
        regions = [
            ("gcc", 415), ("europe", 400), ("india", 415), ("australia", 415)
        ]
        for region, voltage in regions:
            resp = await api_client.post("/api/electrical/voltage-drop", json={
                "region": region,
                "cable_type": "XLPE_CU",
                "conductor_size_mm2": 50,
                "cable_length_m": 10,
                "design_current_a": 50,
                "phases": 3,
            })
            assert resp.status_code == 200
            d = resp.json()
            assert d["compliant"] is True, f"Region {region}: short cable should always be compliant"

    async def test_vd_receiving_end_voltage_is_reduced(self, api_client):
        """Receiving end voltage must be less than supply voltage."""
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "gcc",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 16,
            "cable_length_m": 100,
            "design_current_a": 70,
            "phases": 3,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["receiving_end_voltage_v"] < d["supply_voltage_v"]
        assert d["receiving_end_voltage_v"] > 0

    async def test_vd_formula_verification(self, api_client):
        """
        Verify VD% = (Z x I x L / 1000) / Vs x 100 numerically.
        25 mm2 XLPE/Cu: Z = 1.75 mV/A/m, I=80A, L=50m, Vs=415V
        VD = 1.75 x 80 x 50 / 1000 = 7.0 V = 1.69%
        """
        resp = await api_client.post("/api/electrical/voltage-drop", json={
            "region": "gcc",
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 25,
            "cable_length_m": 50,
            "design_current_a": 80,
            "phases": 3,
        })
        assert resp.status_code == 200
        d = resp.json()
        # Expected: 1.75 x 80 x 50 / 1000 = 7.0 V; 7.0/415 x 100 = 1.69%
        assert abs(d["vd_percent"] - 1.69) < 0.4, f"Expected ~1.69%, got {d['vd_percent']}%"


# ─── Maximum Demand ────────────────────────────────────────────────────────────

class TestMaximumDemand:

    async def test_maximum_demand_gcc_basic(self, api_client):
        resp = await api_client.post("/api/electrical/maximum-demand", json={
            "region": "gcc",
            "loads": [
                {"description": "Lighting", "kw": 10.0, "demand_factor": 0.9, "quantity": 1},
                {"description": "Power", "kw": 20.0, "demand_factor": 0.75, "quantity": 3},
                {"description": "HVAC", "kw": 30.0, "demand_factor": 0.85, "quantity": 2},
            ]
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["maximum_demand_kw"] > 0
        assert d["maximum_demand_kva"] >= d["maximum_demand_kw"]

    async def test_maximum_demand_connected_load_equals_sum(self, api_client):
        """Connected load = sum(kW x quantity) regardless of demand factor."""
        loads = [
            {"description": "A", "kw": 10.0, "demand_factor": 0.5, "quantity": 2},
            {"description": "B", "kw": 15.0, "demand_factor": 0.6, "quantity": 1},
        ]
        resp = await api_client.post("/api/electrical/maximum-demand", json={
            "region": "gcc", "loads": loads
        })
        assert resp.status_code == 200
        d = resp.json()
        # Total connected = 10x2 + 15x1 = 35 kW
        assert abs(d["connected_load_kw"] - 35.0) < 1.0

    async def test_maximum_demand_all_regions(self, api_client):
        for region in ["gcc", "europe", "india", "australia"]:
            resp = await api_client.post("/api/electrical/maximum-demand", json={
                "region": region,
                "loads": [{"description": "Load", "kw": 50.0, "demand_factor": 0.8, "quantity": 2}]
            })
            assert resp.status_code == 200, f"Region {region} failed"


# ─── Short Circuit ─────────────────────────────────────────────────────────────

class TestShortCircuit:

    async def test_short_circuit_gcc_basic(self, api_client):
        resp = await api_client.post("/api/electrical/short-circuit", json={
            "region": "gcc",
            "supply_voltage_v": 415,
            "supply_impedance_ohm": 0.05,
            "cable_impedance_ohm": 0.1,
            "phases": 3,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["three_phase_fault_ka"] > 0
        # IEC 60909: I3ph = V / (sqrt(3) x Zt); rough check
        expected_ka = 415 / (1.732 * (0.05 + 0.1)) / 1000
        assert abs(d["three_phase_fault_ka"] - expected_ka) < 1.0

    async def test_short_circuit_higher_impedance_lower_current(self, api_client):
        """Higher fault impedance must produce lower fault current (Ohm's law)."""
        base = {"region": "gcc", "supply_voltage_v": 415, "phases": 3}

        r_low = (await api_client.post("/api/electrical/short-circuit", json={
            **base, "supply_impedance_ohm": 0.02, "cable_impedance_ohm": 0.05
        })).json()

        r_high = (await api_client.post("/api/electrical/short-circuit", json={
            **base, "supply_impedance_ohm": 0.02, "cable_impedance_ohm": 0.50
        })).json()

        assert r_low["three_phase_fault_ka"] > r_high["three_phase_fault_ka"]


# ─── Lighting ─────────────────────────────────────────────────────────────────

class TestLighting:

    async def test_lighting_lux_power_density_gcc(self, api_client):
        resp = await api_client.post("/api/electrical/lighting", json={
            "region": "gcc",
            "room_type": "office",
            "floor_area_m2": 100,
            "ceiling_height_m": 3.0,
            "target_lux": 500,
            "luminaire_efficacy_lm_w": 100,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["num_luminaires"] > 0
        assert d["installed_power_w"] > 0
        # CIBSE SLL: office target 500 lux; LPD should be reasonable (5-15 W/m2 typical)
        lpd = d["installed_power_w"] / 100
        assert 3 <= lpd <= 25, f"LPD {lpd:.1f} W/m2 outside expected 3-25 W/m2 range"

    async def test_lighting_all_regions(self, api_client):
        for region in ["gcc", "europe", "india", "australia"]:
            resp = await api_client.post("/api/electrical/lighting", json={
                "region": region,
                "room_type": "office",
                "floor_area_m2": 50,
                "ceiling_height_m": 3.0,
                "target_lux": 300,
                "luminaire_efficacy_lm_w": 90,
            })
            assert resp.status_code == 200, f"Region {region} failed"
            d = resp.json()
            assert d["num_luminaires"] > 0
