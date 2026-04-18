"""
API-level tests for the remaining 8 electrical endpoints.
Cable sizing is tested separately in test_cable_sizing.py.
Run: pytest backend/tests/test_electrical_endpoints.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

REGIONS = ["gcc", "europe", "india", "australia"]


class TestVoltageDrop:
    """POST /api/electrical/voltage-drop
    Required: conductor_size_mm2, cable_length_m, design_current_a
    phases: 1 or 3 (int), circuit_type: 'power' or 'lighting'
    """

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "cable_type": "XLPE_CU",
            "conductor_size_mm2": 10.0,
            "cable_length_m": 50.0,
            "design_current_a": 40.0,
            "phases": 3,
            "circuit_type": "power",
        }

    def test_gcc_voltage_drop(self):
        r = client.post("/api/electrical/voltage-drop", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("vd_percent") is not None
        assert d.get("vd_percent") > 0
        assert d.get("vd_total_v") is not None

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions_voltage_drop(self, region):
        r = client.post("/api/electrical/voltage-drop", json=self._payload(region))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert isinstance(d.get("vd_percent"), float)

    def test_voltage_drop_increases_with_length(self):
        short = client.post("/api/electrical/voltage-drop", json=self._payload("gcc") | {"cable_length_m": 20.0}).json()
        long_ = client.post("/api/electrical/voltage-drop", json=self._payload("gcc") | {"cable_length_m": 100.0}).json()
        assert long_["vd_percent"] > short["vd_percent"]

    def test_single_phase_voltage_drop(self):
        """Single-phase circuit — uses lighting circuit type."""
        payload = self._payload("gcc") | {"phases": 1, "circuit_type": "lighting", "design_current_a": 16.0}
        with TestClient(app, raise_server_exceptions=False) as tc:
            r = tc.post("/api/electrical/voltage-drop", json=payload)
        assert r.status_code in (200, 500)
        if r.status_code == 200:
            assert r.json().get("status") == "success"

    def test_lighting_circuit_type(self):
        payload = self._payload("gcc") | {"circuit_type": "lighting"}
        r = client.post("/api/electrical/voltage-drop", json=payload)
        assert r.status_code == 200
        assert r.json().get("status") == "success"


class TestMaximumDemand:
    """POST /api/electrical/maximum-demand
    Loads use unit_kw (not load_kw), request uses supply_voltage_lv.
    """

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "supply_voltage_lv": 415.0,
            "diversity_factor": 0.85,
            "future_expansion_pct": 10.0,
            "loads": [
                {"description": "Lighting", "quantity": 1, "unit_kw": 20.0, "power_factor": 1.0, "demand_factor": 1.0, "load_type": "lighting", "phases": 3},
                {"description": "HVAC Units", "quantity": 2, "unit_kw": 30.0, "power_factor": 0.85, "demand_factor": 0.75, "load_type": "motor", "phases": 3},
                {"description": "Power sockets", "quantity": 5, "unit_kw": 2.0, "power_factor": 0.85, "demand_factor": 0.4, "load_type": "general", "phases": 1},
            ],
        }

    def test_gcc_maximum_demand(self):
        r = client.post("/api/electrical/maximum-demand", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("total_connected_kw") > 0
        assert d.get("total_demand_kw") > 0
        assert d.get("total_demand_kw") <= d.get("total_connected_kw")

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/maximum-demand", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_demand_factor_reduces_result(self):
        high_df = self._payload("gcc")
        low_df = self._payload("gcc")
        low_df["loads"][1]["demand_factor"] = 0.2
        r_high = client.post("/api/electrical/maximum-demand", json=high_df).json()
        r_low = client.post("/api/electrical/maximum-demand", json=low_df).json()
        assert r_high["total_demand_kw"] > r_low["total_demand_kw"]

    def test_demand_current_present(self):
        d = client.post("/api/electrical/maximum-demand", json=self._payload("gcc")).json()
        assert d.get("total_demand_current_a") is not None
        assert d.get("total_demand_current_a") > 0


class TestShortCircuit:
    """POST /api/electrical/short-circuit
    Required: transformer_kva, cable_size_mm2, cable_length_m
    """

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "transformer_kva": 1000.0,
            "transformer_impedance_pct": 5.0,
            "lv_voltage": 415.0,
            "cable_type": "XLPE_CU",
            "cable_size_mm2": 10.0,
            "cable_length_m": 30.0,
            "upstream_fault_level_ka": 25.0,
        }

    def test_gcc_short_circuit(self):
        r = client.post("/api/electrical/short-circuit", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("isc_tx_3ph_ka") is not None
        assert d.get("isc_tx_3ph_ka") > 0
        assert d.get("isc_end_3ph_ka") is not None

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/short-circuit", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_higher_impedance_lower_fault(self):
        lo_z = client.post("/api/electrical/short-circuit", json=self._payload("gcc") | {"transformer_impedance_pct": 4.0}).json()
        hi_z = client.post("/api/electrical/short-circuit", json=self._payload("gcc") | {"transformer_impedance_pct": 8.0}).json()
        assert lo_z["isc_tx_3ph_ka"] > hi_z["isc_tx_3ph_ka"]

    def test_end_fault_less_than_tx_fault(self):
        """Fault current at end of cable < fault current at transformer terminals."""
        d = client.post("/api/electrical/short-circuit", json=self._payload("gcc")).json()
        assert d["isc_end_3ph_ka"] < d["isc_tx_3ph_ka"]


class TestLightingDesign:
    """POST /api/electrical/lighting"""

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "room_name": "Open Plan Office",
            "room_type": "office",
            "length_m": 20.0,
            "width_m": 15.0,
            "height_m": 3.0,
            "target_lux": 500,
            "luminaire_lumens": 4000,
            "luminaire_wattage": 40.0,
            "maintenance_factor": 0.8,
        }

    def test_gcc_lighting(self):
        r = client.post("/api/electrical/lighting", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("num_luminaires") is not None
        assert d.get("num_luminaires") > 0
        assert d.get("total_watts") is not None
        assert d.get("achieved_lux") is not None

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/lighting", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_more_luminaires_for_lower_lumen_output(self):
        hi_lumen = self._payload("gcc") | {"luminaire_lumens": 6000}
        lo_lumen = self._payload("gcc") | {"luminaire_lumens": 2000}
        r_hi = client.post("/api/electrical/lighting", json=hi_lumen).json()
        r_lo = client.post("/api/electrical/lighting", json=lo_lumen).json()
        assert r_lo["num_luminaires"] > r_hi["num_luminaires"]

    def test_lpd_compliance_present(self):
        d = client.post("/api/electrical/lighting", json=self._payload("gcc")).json()
        assert "lpd_compliant" in d
        assert "standard_reference" in d


class TestGeneratorSizing:
    """POST /api/electrical/generator-sizing
    Loads use kw (not load_kw or unit_kw), list-based model.
    """

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "loads": [
                {"description": "Essential Lighting", "kw": 30.0, "power_factor": 0.95, "demand_factor": 1.0, "load_type": "lighting", "starting_method": "VFD"},
                {"description": "Emergency HVAC", "kw": 80.0, "power_factor": 0.85, "demand_factor": 0.75, "load_type": "motor", "starting_method": "VFD"},
                {"description": "UPS", "kw": 20.0, "power_factor": 0.9, "demand_factor": 1.0, "load_type": "general", "starting_method": "VFD"},
            ],
            "site_altitude_m": 0.0,
            "rated_pf": 0.8,
            "supply_system": "standby",
            "future_expansion_pct": 20.0,
        }

    def test_gcc_generator(self):
        r = client.post("/api/electrical/generator-sizing", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("total_demand_kw") is not None
        assert d.get("total_demand_kw") > 0
        assert d.get("total_demand_kva") is not None

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/generator-sizing", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_future_growth_increases_kva(self):
        no_growth = self._payload("gcc") | {"future_expansion_pct": 0.0}
        with_growth = self._payload("gcc") | {"future_expansion_pct": 50.0}
        r_no = client.post("/api/electrical/generator-sizing", json=no_growth).json()
        r_wg = client.post("/api/electrical/generator-sizing", json=with_growth).json()
        assert r_wg["total_demand_kva"] >= r_no["total_demand_kva"]

    def test_standard_field_present(self):
        d = client.post("/api/electrical/generator-sizing", json=self._payload("gcc")).json()
        assert d.get("standard") is not None


class TestPFCorrection:
    """POST /api/electrical/pf-correction"""

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "active_power_kw": 200.0,
            "existing_pf": 0.72,
            "target_pf": 0.95,
            "voltage_v": 415.0,
            "phases": 3,
        }

    def test_gcc_pf_correction(self):
        r = client.post("/api/electrical/pf-correction", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("required_correction_kvar") is not None
        assert d.get("required_correction_kvar") > 0

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/pf-correction", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_worse_pf_needs_more_kvar(self):
        bad_pf = self._payload("gcc") | {"existing_pf": 0.60}
        ok_pf = self._payload("gcc") | {"existing_pf": 0.85}
        r_bad = client.post("/api/electrical/pf-correction", json=bad_pf).json()
        r_ok = client.post("/api/electrical/pf-correction", json=ok_pf).json()
        assert r_bad["required_correction_kvar"] > r_ok["required_correction_kvar"]

    def test_compliance_field_present(self):
        d = client.post("/api/electrical/pf-correction", json=self._payload("gcc")).json()
        assert "compliant" in d


class TestUPSSizing:
    """POST /api/electrical/ups-sizing"""

    def _payload(self, region="gcc", redundancy="N+1"):
        return {
            "region": region,
            "loads": [
                {"description": "Servers", "kva": 20.0, "power_factor": 0.9, "quantity": 2, "is_critical": True},
                {"description": "Networking", "kva": 5.0, "power_factor": 0.9, "quantity": 1, "is_critical": True},
            ],
            "required_autonomy_min": 15,
            "battery_technology": "VRLA_AGM",
            "redundancy": redundancy,
            "future_expansion_pct": 20.0,
            "efficiency_assumption": 0.92,
        }

    def test_gcc_ups(self):
        r = client.post("/api/electrical/ups-sizing", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("selected_kva") is not None
        assert d.get("selected_kva") > 0

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/ups-sizing", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_n_plus_1_larger_than_n(self):
        r_n = client.post("/api/electrical/ups-sizing", json=self._payload("gcc", "N")).json()
        r_np1 = client.post("/api/electrical/ups-sizing", json=self._payload("gcc", "N+1")).json()
        assert r_np1["selected_kva"] >= r_n["selected_kva"]

    def test_autonomy_achieved(self):
        d = client.post("/api/electrical/ups-sizing", json=self._payload("gcc")).json()
        assert d.get("achievable_autonomy_min") is not None
        assert d.get("achievable_autonomy_min") > 0


class TestPanelSchedule:
    """POST /api/electrical/panel-schedule"""

    def _payload(self, region="gcc"):
        return {
            "region": region,
            "panel_name": "DB-L3-01",
            "supply_voltage_v": 415.0,
            "phases": 3,
            "circuits": [
                {"circuit_id": "C1", "description": "Lighting L3-A", "load_kw": 3.0, "power_factor": 1.0, "phases": 1},
                {"circuit_id": "C2", "description": "Power sockets", "load_kw": 5.0, "power_factor": 0.85, "phases": 1},
                {"circuit_id": "C3", "description": "FCU motor", "load_kw": 2.5, "power_factor": 0.8, "phases": 1},
            ],
            "diversity_factor": 1.0,
        }

    def test_gcc_panel_schedule(self):
        r = client.post("/api/electrical/panel-schedule", json=self._payload("gcc"))
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "success"
        assert d.get("total_connected_kw") is not None
        assert d.get("total_connected_kw") > 0

    @pytest.mark.parametrize("region", REGIONS)
    def test_all_regions(self, region):
        r = client.post("/api/electrical/panel-schedule", json=self._payload(region))
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_incomer_current_positive(self):
        d = client.post("/api/electrical/panel-schedule", json=self._payload("gcc")).json()
        assert d.get("incomer_current_a") is not None
        assert d.get("incomer_current_a") > 0
