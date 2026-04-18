"""
OpenMEP Reports Route
======================
Generates structured engineering calculation reports in JSON format,
suitable for rendering as PDF, Excel, or HTML documents.

For PDF export, use /api/reports/pdf-data to get formatted data.
"""

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Engineering Reports"])

limiter = Limiter(key_func=get_remote_address)


# ─── Request models ───────────────────────────────────────────────────────────

class ReportMetadata(BaseModel):
    project_name: str = ""
    project_number: str = ""
    client: str = ""
    location: str = ""
    prepared_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    revision: str = "P1"
    date: Optional[str] = None
    discipline: str = "MEP"
    region: str = "gcc"
    report_title: str = "Engineering Calculation Report"


class CalculationEntry(BaseModel):
    section: str = ""
    reference: str = ""
    description: str = ""
    result_summary: dict = {}   # Key-value pairs from any calculation endpoint
    standard: str = ""
    compliant: bool = True
    notes: str = ""


class CalculationReportRequest(BaseModel):
    metadata: ReportMetadata
    calculations: List[CalculationEntry] = []
    include_appendix: bool = True


REGIONAL_STANDARDS_HEADER = {
    "gcc": {
        "authority": "Gulf Cooperation Council — UAE / Saudi Arabia / Qatar / Kuwait",
        "primary_standard": "BS 7671:2018+A2:2022 / IEC 60364",
        "energy_code": "DEWA Green Building Regulations / Estidama Pearl Rating",
    },
    "europe": {
        "authority": "United Kingdom & Europe",
        "primary_standard": "BS 7671:2018+A2:2022 / EN 60204",
        "energy_code": "Building Regulations Part L / EN ISO 52016",
    },
    "india": {
        "authority": "India — Bureau of Indian Standards",
        "primary_standard": "IS 732:2019 / IS 3961 / NBC 2016",
        "energy_code": "ECBC 2017 / BEE Star Rating",
    },
    "australia": {
        "authority": "Australia / New Zealand",
        "primary_standard": "AS/NZS 3000:2018 / AS/NZS 3008.1.1:2017",
        "energy_code": "NCC 2022 Section J / NatHERS",
    },
}

DISCLAIMER = (
    "This calculation report has been prepared using OpenMEP — an open-source MEP engineering "
    "calculation suite. All calculations are based on the regional standards identified herein. "
    "The engineer of record is responsible for verifying all inputs, assumptions, and results "
    "against project-specific conditions and applicable standards. This report does not constitute "
    "a substitute for professional engineering judgement."
)


@router.post("/calculation-report", summary="Generate Calculation Report Data")
@limiter.limit("10/minute")
async def calculation_report(request: Request, req: CalculationReportRequest) -> Any:
    """
    Compile all calculation entries into a structured report payload.
    The response can be rendered as PDF, Excel, or HTML.
    """
    try:
        now = req.metadata.date or datetime.now().strftime("%d %B %Y")
        region_info = REGIONAL_STANDARDS_HEADER.get(req.metadata.region, REGIONAL_STANDARDS_HEADER["gcc"])

        # Summary statistics
        total = len(req.calculations)
        passed = sum(1 for c in req.calculations if c.compliant)
        failed = total - passed

        # Group by section
        sections = {}
        for calc in req.calculations:
            sec = calc.section or "General"
            if sec not in sections:
                sections[sec] = []
            sections[sec].append({
                "reference": calc.reference,
                "description": calc.description,
                "standard": calc.standard,
                "compliant": calc.compliant,
                "result_summary": calc.result_summary,
                "notes": calc.notes,
            })

        appendix = None
        if req.include_appendix:
            appendix = {
                "standards_references": region_info,
                "calculation_methodology": {
                    "cable_sizing": "IEC 60364-5-52 / BS 7671 Appendix 4 — current rating selection with ambient temperature and grouping correction factors applied",
                    "voltage_drop": "BS 7671 Appendix 12 / IEC 60364-5-52 — mV/A/m method",
                    "short_circuit": "IEC 60909-0:2016 — symmetrical components impedance method",
                    "lighting": "CIE 97:2005 Lumen Method — maintained illuminance Em with utilisation factor UF and light loss factor LLF",
                    "cooling_load": "ASHRAE Handbook Fundamentals — Heat Balance Method with solar gain, conduction, and internal load components",
                    "duct_sizing": "ASHRAE HVAC Systems and Equipment — Equal Friction Method",
                    "pipe_sizing": "BS EN 806-3 — Discharge Unit (Loading Unit) probabilistic method",
                    "sprinkler": "BS EN 12845 / NFPA 13 — hydraulic calculation with design area method",
                    "generator": "ISO 8528-1 — site derating for altitude and ambient temperature",
                    "ups": "IEC 62040-1/3 — battery autonomy from Peukert equation",
                    "pf_correction": "IEC 60831-1 — capacitive reactive power Q_c = P(tan φ₁ − tan φ₂)",
                },
                "software": {
                    "name": "OpenMEP",
                    "version": "0.1.0",
                    "url": "https://github.com/openmep/openmep",
                    "license": "MIT",
                },
                "disclaimer": DISCLAIMER,
            }

        return {
            "status": "success",
            "report": {
                "metadata": {
                    "project_name": req.metadata.project_name,
                    "project_number": req.metadata.project_number,
                    "client": req.metadata.client,
                    "location": req.metadata.location,
                    "prepared_by": req.metadata.prepared_by,
                    "checked_by": req.metadata.checked_by,
                    "approved_by": req.metadata.approved_by,
                    "revision": req.metadata.revision,
                    "date": now,
                    "discipline": req.metadata.discipline,
                    "region": req.metadata.region,
                    "report_title": req.metadata.report_title,
                },
                "region_info": region_info,
                "summary": {
                    "total_calculations": total,
                    "calculations_passed": passed,
                    "calculations_failed": failed,
                    "overall_compliant": failed == 0,
                },
                "sections": sections,
                "appendix": appendix,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", summary="List Report Templates (GET)")
async def list_templates() -> Any:
    """Return available report templates."""
    return {
        "templates": [
            {
                "id": "electrical_full",
                "name": "Full Electrical Calculation Report",
                "sections": ["Cable Sizing", "Voltage Drop", "Maximum Demand", "Short Circuit",
                             "Lighting", "Power Factor Correction", "Generator Sizing",
                             "UPS Sizing", "Panel Schedule"],
                "standards": ["BS 7671", "IEC 60364", "IS 732", "AS/NZS 3000"],
            },
            {
                "id": "mechanical_full",
                "name": "Full HVAC/Mechanical Calculation Report",
                "sections": ["Cooling Load", "Duct Sizing", "Ventilation"],
                "standards": ["ASHRAE 62.1", "CIBSE Guide A", "NBC 2016 Part 8", "AS 1668.2"],
            },
            {
                "id": "plumbing_fire",
                "name": "Plumbing & Fire Protection Report",
                "sections": ["Pipe Sizing", "Sprinkler System", "Fire Pump"],
                "standards": ["BS EN 806", "BS EN 12845", "NFPA 13", "AS 3500", "AS 2118"],
            },
            {
                "id": "mep_summary",
                "name": "MEP Design Summary (All Disciplines)",
                "sections": ["Electrical Summary", "HVAC Summary", "Plumbing Summary",
                             "Fire Protection Summary", "BOQ Summary"],
                "standards": ["Regional composite — see appendix"],
            },
        ],
        "output_formats": ["json", "pdf", "excel", "html"],
        "note": "Use POST /api/reports/calculation-report to generate a report with your calculation data.",
    }


@router.get("/standards-data", summary="Embedded Standards Data Reference (GET)")
async def standards_data() -> Any:
    """Return key engineering data tables embedded in OpenMEP."""
    return {
        "cable_standards": {
            "gcc_europe": {
                "standard": "BS 7671:2018+A2:2022",
                "table": "4D5A (XLPE Cu) / 4D2A (PVC Cu)",
                "correction_factors": "Table 4B1 (temp) / Table 4C1 (grouping)",
                "reference_temp_air": "30°C (XLPE), 30°C (PVC)",
                "reference_temp_ground": "20°C",
            },
            "india": {
                "standard": "IS 3961:2011 Part 2 / IS 7098:2011 Part 1",
                "cable_type": "FRLS XLPE mandatory per NBC 2016 Part 4 Cl. 4.2",
                "reference_temp_air": "30°C",
            },
            "australia": {
                "standard": "AS/NZS 3008.1.1:2017",
                "cable_type": "X-90 XLPE preferred (90°C)",
                "reference_temp_air": "25°C",
                "earthing": "MEN (TN-CS)",
            },
        },
        "voltage_drop_limits": {
            "gcc_dewa": {"lighting": "3%", "power": "4%"},
            "gcc_addc": {"lighting": "3%", "power": "5%"},
            "gcc_kahramaa": {"lighting": "3%", "power": "5%"},
            "gcc_sec": {"lighting": "2.5%", "power": "4%"},
            "europe": {"lighting": "3%", "power": "5%"},
            "india": {"lighting": "2.5%", "power": "5%"},
            "australia": {"total": "5%"},
            "standard_ref": "BS 7671 Appendix 12 / IS 732 Sec 6 / AS/NZS 3000 Cl. 3.6",
        },
        "sprinkler_design_densities": {
            "LH": {"density_mm_min": 2.25, "design_area_m2": 84, "standard": "BS EN 12845 Table 3"},
            "OH1": {"density_mm_min": 5.0, "design_area_m2": 72, "standard": "BS EN 12845 Table 3"},
            "OH2": {"density_mm_min": 5.0, "design_area_m2": 144, "standard": "BS EN 12845 Table 3"},
            "EH1": {"density_mm_min": 7.5, "design_area_m2": 260, "standard": "BS EN 12845 Table 3"},
            "EH2": {"density_mm_min": 12.5, "design_area_m2": 260, "standard": "BS EN 12845 Table 3"},
        },
        "transformer_standard_ratings_kva": [
            25, 50, 100, 160, 200, 250, 315, 400, 500, 630, 800,
            1000, 1250, 1600, 2000, 2500, 3150, 4000
        ],
    }
