"""
OpenMEP Bill of Quantities (BOQ) Route
=========================================
Generates a priced MEP bill of quantities from calculation results.
Supports regional measurement schemas:
  GCC       — FIDIC / NEC3 (AED)
  Europe/UK — NRM2 / SMM7 (GBP)
  India     — CPWD DSR / IS standards (INR)
  Australia — AIQS / AISC (AUD)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional

router = APIRouter(prefix="/boq", tags=["Bill of Quantities"])


# ─── Regional measurement schema metadata ─────────────────────────────────────

REGIONAL_BOQ_SCHEMA = {
    "gcc": {
        "schema": "FIDIC / NEC3",
        "currency": "AED",
        "usd_fx": 3.67,
        "measurement_standard": "CESMM4 / POMI",
        "standard_authority": "DEWA / Civil Defence / Municipality",
        "notes": "All quantities in metric units. Rates exclude VAT (5%).",
    },
    "europe": {
        "schema": "NRM2 / SMM7",
        "currency": "GBP",
        "usd_fx": 0.79,
        "measurement_standard": "RICS NRM2 (2012)",
        "standard_authority": "RICS / BS 8541",
        "notes": "Quantities measured net in accordance with NRM2. Rates exclude UK VAT (20%).",
    },
    "india": {
        "schema": "CPWD DSR",
        "currency": "INR",
        "usd_fx": 83.5,
        "measurement_standard": "CPWD DSR 2023 / IS 1200",
        "standard_authority": "CPWD / PWD / BIS",
        "notes": "Rates based on CPWD Delhi Schedule of Rates. Add 18% GST.",
    },
    "australia": {
        "schema": "AIQS / AISC",
        "currency": "AUD",
        "usd_fx": 1.53,
        "measurement_standard": "AIQS Cost Management Manual",
        "standard_authority": "AIQS / Standards Australia",
        "notes": "Rates ex-GST. Include 10% GST in final tender sum. NCC BCA compliance required.",
    },
}


# ─── Request / Response models ────────────────────────────────────────────────

class CableBoQItem(BaseModel):
    circuit_reference: str = ""
    description: str = ""
    cable_type: str = "XLPE_CU"
    cable_size_mm2: float = 0.0
    phases: int = 3
    cable_length_m: float = 0.0
    runs: int = 1
    conduit_diameter_mm: Optional[float] = None
    tray_width_mm: Optional[float] = None


class DuctBoQItem(BaseModel):
    section_id: str = ""
    description: str = ""
    width_mm: float = 0.0
    height_mm: float = 0.0
    diameter_mm: Optional[float] = None
    duct_type: str = "rectangular"
    length_m: float = 0.0
    material: str = "galvanised_steel"


class PipeBoQItem(BaseModel):
    section_id: str = ""
    description: str = ""
    nominal_dn: int = 0
    diameter_mm: float = 0.0
    length_m: float = 0.0
    material: str = "copper"
    system: str = "CWDS"
    insulation: bool = False


class MepBoQRequest(BaseModel):
    project_name: str = ""
    project_reference: str = ""
    region: str = "gcc"
    sub_region: str = ""
    currency: str = "USD"

    cables: List[CableBoQItem] = []
    ducts: List[DuctBoQItem] = []
    pipes: List[PipeBoQItem] = []


# ─── Unit rates (indicative, USD/unit) ───────────────────────────────────────

CABLE_RATES_USD_M = {
    "1.5": 0.8, "2.5": 1.0, "4": 1.4, "6": 1.9,
    "10": 3.0, "16": 4.5, "25": 6.5, "35": 9.0,
    "50": 12.0, "70": 16.0, "95": 21.0, "120": 26.0,
    "150": 32.0, "185": 39.0, "240": 50.0, "300": 62.0,
    "400": 82.0, "630": 130.0,
}

DUCT_RATES_USD_M2 = {
    "galvanised_steel": 35.0,
    "stainless_steel": 95.0,
    "aluminium": 70.0,
    "pvc": 25.0,
}

PIPE_RATES_USD_M = {
    "copper_15": 8.0, "copper_22": 12.0, "copper_28": 16.0, "copper_35": 22.0,
    "copper_42": 28.0, "copper_54": 38.0, "copper_76": 55.0, "copper_108": 80.0,
    "pvc_25": 5.0, "pvc_32": 6.5, "pvc_40": 8.0, "pvc_50": 10.0,
    "ppr_25": 7.0, "ppr_32": 9.0, "ppr_40": 12.0, "ppr_50": 15.0,
    "gi_25": 10.0, "gi_32": 14.0, "gi_40": 18.0, "gi_50": 24.0,
    "hdpe_32": 6.0, "hdpe_50": 9.5, "hdpe_75": 14.0, "hdpe_110": 21.0,
}

REGIONAL_MULTIPLIERS = {
    "gcc": 1.15,
    "europe": 1.40,
    "india": 0.65,
    "australia": 1.50,
}


def _cable_rate(size_mm2: float, phases: int) -> float:
    size_key = str(int(size_mm2)) if size_mm2 >= 1 else "1.5"
    base = CABLE_RATES_USD_M.get(size_key, size_mm2 * 0.18)
    return base * (phases / 3 * 0.85 + 0.15)


def _duct_area_m2(item: DuctBoQItem) -> float:
    import math
    if item.duct_type == "circular" and item.diameter_mm:
        perim = math.pi * item.diameter_mm / 1000
        return perim * item.length_m
    else:
        perim = 2 * (item.width_mm + item.height_mm) / 1000
        return perim * item.length_m


def _pipe_rate(material: str, dn: int) -> float:
    key = f"{material}_{dn}"
    if key in PIPE_RATES_USD_M:
        return PIPE_RATES_USD_M[key]
    return dn * 0.5 if material == "copper" else dn * 0.3


def _fmt_currency(amount_usd: float, schema: dict) -> dict:
    fx = schema["usd_fx"]
    local = amount_usd * fx
    return {
        "amount_usd": round(amount_usd, 2),
        f"amount_{schema['currency'].lower()}": round(local, 2),
    }


@router.post("/generate", summary="Generate MEP Bill of Quantities")
async def generate_boq(req: MepBoQRequest) -> Any:
    """
    Generate an itemised MEP Bill of Quantities from take-off data.
    Regional schemas applied:
      GCC → FIDIC/NEC3 (AED), Europe → NRM2/SMM7 (GBP),
      India → CPWD DSR (INR), Australia → AIQS (AUD).
    """
    try:
        multiplier = REGIONAL_MULTIPLIERS.get(req.region, 1.0)
        schema = REGIONAL_BOQ_SCHEMA.get(req.region, REGIONAL_BOQ_SCHEMA["gcc"])
        line_items = []
        grand_total = 0.0

        # ── Cables ─────────────────────────────────────────────────────────
        cable_total = 0.0
        for cab in req.cables:
            qty_m = cab.cable_length_m * cab.runs
            rate = _cable_rate(cab.cable_size_mm2, cab.phases) * multiplier
            amount = qty_m * rate
            cable_total += amount
            desc = (
                f"{cab.description or cab.circuit_reference} "
                f"— {cab.phases}C × {cab.cable_size_mm2}mm² {cab.cable_type}"
            )
            item = {
                "discipline": "Electrical",
                "category": "Cables",
                "description": desc,
                "quantity": round(qty_m, 1),
                "unit": "m",
                "unit_rate_usd": round(rate, 2),
                "amount_usd": round(amount, 2),
            }
            item.update(_fmt_currency(amount, schema))
            line_items.append(item)

        if req.cables:
            sub = {"discipline": "Electrical", "category": "Cables",
                   "description": f"Subtotal — Cables ({schema['schema']})",
                   "quantity": None, "unit": None, "unit_rate_usd": None,
                   "amount_usd": round(cable_total, 2)}
            sub.update(_fmt_currency(cable_total, schema))
            line_items.append(sub)
        grand_total += cable_total

        # ── Ductwork ───────────────────────────────────────────────────────
        duct_total = 0.0
        for duct in req.ducts:
            area = _duct_area_m2(duct)
            rate = DUCT_RATES_USD_M2.get(duct.material, 35.0) * multiplier
            amount = area * rate
            duct_total += amount
            if duct.duct_type == "circular":
                dim_str = f"⌀{duct.diameter_mm:.0f}mm"
            else:
                dim_str = f"{duct.width_mm:.0f}×{duct.height_mm:.0f}mm"
            desc = (
                f"{duct.description or duct.section_id} "
                f"— {dim_str} {duct.material.replace('_', ' ').title()}"
            )
            item = {
                "discipline": "Mechanical",
                "category": "Ductwork",
                "description": desc,
                "quantity": round(area, 2),
                "unit": "m²",
                "unit_rate_usd": round(rate, 2),
                "amount_usd": round(amount, 2),
            }
            item.update(_fmt_currency(amount, schema))
            line_items.append(item)

        if req.ducts:
            sub = {"discipline": "Mechanical", "category": "Ductwork",
                   "description": f"Subtotal — Ductwork ({schema['schema']})",
                   "quantity": None, "unit": None, "unit_rate_usd": None,
                   "amount_usd": round(duct_total, 2)}
            sub.update(_fmt_currency(duct_total, schema))
            line_items.append(sub)
        grand_total += duct_total

        # ── Pipework ───────────────────────────────────────────────────────
        pipe_total = 0.0
        for pipe in req.pipes:
            qty_m = pipe.length_m
            rate = _pipe_rate(pipe.material, pipe.nominal_dn) * multiplier
            insulation_factor = 1.35 if pipe.insulation else 1.0
            amount = qty_m * rate * insulation_factor
            pipe_total += amount
            desc = (
                f"{pipe.description or pipe.section_id} "
                f"— DN{pipe.nominal_dn} {pipe.material.upper()} {pipe.system}"
            )
            if pipe.insulation:
                desc += " (insulated)"
            item = {
                "discipline": "Plumbing",
                "category": "Pipework",
                "description": desc,
                "quantity": round(qty_m, 1),
                "unit": "m",
                "unit_rate_usd": round(rate * insulation_factor, 2),
                "amount_usd": round(amount, 2),
            }
            item.update(_fmt_currency(amount, schema))
            line_items.append(item)

        if req.pipes:
            sub = {"discipline": "Plumbing", "category": "Pipework",
                   "description": f"Subtotal — Pipework ({schema['schema']})",
                   "quantity": None, "unit": None, "unit_rate_usd": None,
                   "amount_usd": round(pipe_total, 2)}
            sub.update(_fmt_currency(pipe_total, schema))
            line_items.append(sub)
        grand_total += pipe_total

        # 10% contingency
        contingency = grand_total * 0.10
        cont_item = {
            "discipline": "General", "category": "Contingency",
            "description": "Contingency (10%)",
            "quantity": None, "unit": None, "unit_rate_usd": None,
            "amount_usd": round(contingency, 2),
        }
        cont_item.update(_fmt_currency(contingency, schema))
        line_items.append(cont_item)
        grand_total += contingency

        return {
            "status": "success",
            "project_name": req.project_name,
            "project_reference": req.project_reference,
            "region": req.region,
            "sub_region": req.sub_region,
            "currency": req.currency,
            "regional_cost_index": multiplier,
            "boq_schema": schema["schema"],
            "measurement_standard": schema["measurement_standard"],
            "standard_authority": schema["standard_authority"],
            "local_currency": schema["currency"],
            "usd_fx_rate": schema["usd_fx"],
            "line_items": line_items,
            "cable_total_usd": round(cable_total, 2),
            "duct_total_usd": round(duct_total, 2),
            "pipe_total_usd": round(pipe_total, 2),
            "contingency_usd": round(contingency, 2),
            "grand_total_usd": round(grand_total, 2),
            f"grand_total_{schema['currency'].lower()}": round(grand_total * schema["usd_fx"], 2),
            "schema_notes": schema["notes"],
            "note": "Unit rates are indicative only. Obtain competitive tenders for budget estimates.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rates", summary="Get Indicative Unit Rates (GET)")
async def get_rates() -> Any:
    """Return indicative unit rates for MEP materials by region with schema info."""
    return {
        "cable_rates_usd_per_m": CABLE_RATES_USD_M,
        "duct_rates_usd_per_m2": DUCT_RATES_USD_M2,
        "pipe_rates_usd_per_m": {k: v for k, v in list(PIPE_RATES_USD_M.items())[:15]},
        "regional_cost_indices": REGIONAL_MULTIPLIERS,
        "regional_boq_schemas": {r: s["schema"] for r, s in REGIONAL_BOQ_SCHEMA.items()},
        "measurement_standards": {r: s["measurement_standard"] for r, s in REGIONAL_BOQ_SCHEMA.items()},
        "currency": "USD (base)",
        "note": "Indicative rates only. Prices vary with market conditions and procurement.",
    }
