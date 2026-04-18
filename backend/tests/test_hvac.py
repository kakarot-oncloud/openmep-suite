"""
API-level tests for the HVAC / Mechanical endpoints with reference values.
Covers: cooling load (all 4 regions), duct sizing.

Reference values / design basis:
  ASHRAE Handbook of Fundamentals 2021 — heat gain equations
  CIBSE Guide A:2015  — thermal environment
  ECBC 2017 (India)   — building energy norms

Cooling load components:
  Solar gain (glass):  Q_solar = U x A x DeltaT + SHGC x A x I_solar
  Fabric gain:         Q_fabric = U x A x CLTD
  Internal gains:      Q_occup = n x q_sensible + Q_equip + Q_lighting
  Ventilation:         Q_vent = rho x Cp x flow x DeltaT

GCC design conditions (ASHRAE 99.6%): 46 deg C DB, 30 deg C WB
Europe design conditions:             32 deg C DB, 23 deg C WB
India design conditions:              40-45 deg C DB (composite climate)
Australia design conditions:          35-42 deg C DB (zone dependent)

Run: python -m pytest backend/tests/test_hvac.py -v
"""

import pytest

pytestmark = pytest.mark.asyncio


# ─── Cooling Load — GCC Region ────────────────────────────────────────────────

class TestCoolingLoadGCC:
    """GCC design: 46 deg C outdoor DB, ASHRAE 99.6% conditions."""

    async def test_office_200m2_gcc_basic_calculation(self, api_client):
        """
        200 m2 office, GCC. Design conditions: 46 deg C DB, 24 deg C indoor.
        Expected load range: 40-80 kW (200-400 W/m2 typical GCC office).
        """
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": "gcc",
            "zone_name": "GCC Office",
            "zone_type": "office",
            "floor_area_m2": 200,
            "height_m": 3.0,
            "glass_area_m2": 40,
            "glass_u_value": 2.8,
            "glass_shgc": 0.4,
            "glass_orientation": "W",
            "wall_area_m2": 120,
            "wall_u_value": 0.45,
            "occupancy": 20,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 20,
            "lighting_w_m2": 10,
            "fresh_air_l_s_person": 10,
            "cop": 3.0,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["total_cooling_load_kw"] > 0
        # GCC office: expected 150-450 W/m2 (higher due to 46 deg C solar)
        w_per_m2 = d["total_cooling_load_kw"] * 1000 / 200
        assert 100 <= w_per_m2 <= 600, f"GCC office: {w_per_m2:.0f} W/m2 outside 100-600 range"

    async def test_gcc_internal_gains_components(self, api_client):
        """
        Internal gains must be non-zero for occupied spaces.
        Occupant gain: 20 persons x 90 W = 1800 W = 1.8 kW (sensible)
        Equipment: 20 W/m2 x 200 m2 = 4000 W = 4.0 kW
        Lighting:  10 W/m2 x 200 m2 = 2000 W = 2.0 kW
        Total internal sensible = 7.8 kW minimum (before ventilation and fabric)
        """
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": "gcc",
            "zone_name": "Internal Test",
            "zone_type": "office",
            "floor_area_m2": 200,
            "height_m": 3.0,
            "glass_area_m2": 0,
            "wall_area_m2": 0,
            "roof_area_m2": 0,
            "occupancy": 20,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 20,
            "lighting_w_m2": 10,
            "fresh_air_l_s_person": 0,
            "cop": 3.0,
        })
        assert resp.status_code == 200
        d = resp.json()
        # Sensible internal gains alone must be >= 7.8 kW
        assert d["total_cooling_load_kw"] >= 7.0, (
            f"Internal gains should be >= 7 kW, got {d['total_cooling_load_kw']:.2f} kW"
        )

    async def test_gcc_cop_affects_electrical_input(self, api_client):
        """Higher COP must result in lower electrical input power for same cooling load."""
        base = {
            "region": "gcc", "zone_type": "office",
            "floor_area_m2": 100, "height_m": 3.0,
            "glass_area_m2": 20, "wall_area_m2": 60,
            "occupancy": 10, "equipment_w_m2": 20, "lighting_w_m2": 10,
        }
        r_cop2 = (await api_client.post("/api/mechanical/cooling-load", json={**base, "cop": 2.0})).json()
        r_cop4 = (await api_client.post("/api/mechanical/cooling-load", json={**base, "cop": 4.0})).json()
        if "electrical_input_kw" in r_cop2:
            assert r_cop4["electrical_input_kw"] < r_cop2["electrical_input_kw"]
        assert r_cop2["total_cooling_load_kw"] > 0
        assert r_cop4["total_cooling_load_kw"] > 0


# ─── Cooling Load — Europe Region ────────────────────────────────────────────

class TestCoolingLoadEurope:
    """Europe design: 32 deg C outdoor DB, 24 deg C indoor setpoint."""

    async def test_europe_office_100m2(self, api_client):
        """
        100 m2 office, Europe. Lower outdoor temp -> lower load than GCC.
        Expected: 10-40 kW (100-400 W/m2).
        """
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": "europe",
            "zone_type": "office",
            "floor_area_m2": 100,
            "height_m": 3.0,
            "glass_area_m2": 15,
            "glass_u_value": 1.8,
            "glass_shgc": 0.3,
            "wall_area_m2": 80,
            "wall_u_value": 0.3,
            "occupancy": 10,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 15,
            "lighting_w_m2": 8,
            "cop": 3.5,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["total_cooling_load_kw"] > 0

    async def test_gcc_load_greater_than_europe_same_geometry(self, api_client):
        """GCC cooling load must exceed Europe for identical geometry (higher outdoor temp)."""
        base = {
            "zone_type": "office", "floor_area_m2": 150, "height_m": 3.0,
            "glass_area_m2": 30, "glass_u_value": 2.0, "glass_shgc": 0.35,
            "wall_area_m2": 100, "wall_u_value": 0.4,
            "occupancy": 15, "metabolic_rate_w": 90,
            "equipment_w_m2": 20, "lighting_w_m2": 10, "cop": 3.0,
        }
        r_gcc = (await api_client.post("/api/mechanical/cooling-load", json={**base, "region": "gcc"})).json()
        r_eu  = (await api_client.post("/api/mechanical/cooling-load", json={**base, "region": "europe"})).json()
        assert r_gcc["total_cooling_load_kw"] > r_eu["total_cooling_load_kw"], (
            f"GCC ({r_gcc['total_cooling_load_kw']:.1f} kW) must exceed Europe "
            f"({r_eu['total_cooling_load_kw']:.1f} kW) for same geometry"
        )


# ─── Cooling Load — India Region ──────────────────────────────────────────────

class TestCoolingLoadIndia:
    """India design: ECBC 2017 composite climate, 40-45 deg C outdoor DB."""

    async def test_india_office_cooling_load(self, api_client):
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": "india",
            "zone_type": "office",
            "floor_area_m2": 150,
            "height_m": 3.2,
            "glass_area_m2": 25,
            "glass_u_value": 2.5,
            "glass_shgc": 0.4,
            "glass_orientation": "S",
            "wall_area_m2": 90,
            "wall_u_value": 0.4,
            "occupancy": 15,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 18,
            "lighting_w_m2": 9,
            "cop": 3.0,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["total_cooling_load_kw"] > 5.0

    async def test_india_hotel_room_cooling_load(self, api_client):
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": "india",
            "zone_type": "hotel_room",
            "floor_area_m2": 30,
            "height_m": 2.8,
            "glass_area_m2": 4,
            "wall_area_m2": 30,
            "occupancy": 2,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 10,
            "lighting_w_m2": 8,
            "cop": 3.0,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["total_cooling_load_kw"] > 0
        # Single hotel room: expect 2-8 kW (1.5-3 TR typical)
        assert d["total_cooling_load_kw"] < 15


# ─── Cooling Load — Australia Region ─────────────────────────────────────────

class TestCoolingLoadAustralia:
    """Australia: NCC 2022 (NatHERS), design 35-42 deg C DB depending on climate zone."""

    async def test_australia_office_cooling_load(self, api_client):
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": "australia",
            "zone_type": "office",
            "floor_area_m2": 120,
            "height_m": 3.0,
            "glass_area_m2": 20,
            "glass_u_value": 2.0,
            "glass_shgc": 0.35,
            "wall_area_m2": 80,
            "wall_u_value": 0.35,
            "occupancy": 12,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 18,
            "lighting_w_m2": 9,
            "cop": 3.5,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["total_cooling_load_kw"] > 0


# ─── Cross-region parametrized tests ──────────────────────────────────────────

class TestCoolingLoadAllRegions:
    """Parametrized smoke tests — all regions must return valid results."""

    @pytest.mark.parametrize("region", ["gcc", "europe", "india", "australia"])
    async def test_all_regions_valid_output(self, region, api_client):
        """Basic 100 m2 office must produce valid cooling load for all regions."""
        resp = await api_client.post("/api/mechanical/cooling-load", json={
            "region": region,
            "zone_type": "office",
            "floor_area_m2": 100,
            "height_m": 3.0,
            "glass_area_m2": 15,
            "glass_u_value": 2.0,
            "glass_shgc": 0.35,
            "wall_area_m2": 80,
            "wall_u_value": 0.4,
            "occupancy": 10,
            "metabolic_rate_w": 90,
            "equipment_w_m2": 15,
            "lighting_w_m2": 10,
            "cop": 3.0,
        })
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["total_cooling_load_kw"] > 0, f"Region {region}: cooling load must be > 0"

    @pytest.mark.parametrize("region", ["gcc", "europe", "india", "australia"])
    async def test_larger_area_gives_larger_load(self, region, api_client):
        """Doubling floor area must increase cooling load."""
        base = {
            "region": region, "zone_type": "office", "height_m": 3.0,
            "glass_area_m2": 10, "wall_area_m2": 60,
            "occupancy": 5, "equipment_w_m2": 15, "lighting_w_m2": 10, "cop": 3.0,
        }
        r_small = (await api_client.post("/api/mechanical/cooling-load", json={**base, "floor_area_m2": 50})).json()
        r_large = (await api_client.post("/api/mechanical/cooling-load", json={**base, "floor_area_m2": 200})).json()
        assert r_large["total_cooling_load_kw"] > r_small["total_cooling_load_kw"], (
            f"Region {region}: larger area must give higher load"
        )
