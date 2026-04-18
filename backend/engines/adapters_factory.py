"""
Adapter Factory — resolves region string → correct regional adapter instance.
"""

from backend.adapters.base_adapter import BaseElectricalAdapter


def get_electrical_adapter(region: str, sub_region: str = "") -> BaseElectricalAdapter:
    """Return the correct electrical adapter for a region."""
    r = region.lower().strip()
    if r == "gcc":
        from backend.adapters.gcc.electrical_adapter import GCCElectricalAdapter
        return GCCElectricalAdapter(sub_authority=sub_region or "general")
    elif r == "europe":
        from backend.adapters.europe.electrical_adapter import EuropeElectricalAdapter
        return EuropeElectricalAdapter(country=sub_region or "uk")
    elif r == "india":
        from backend.adapters.india.electrical_adapter import IndiaElectricalAdapter
        return IndiaElectricalAdapter(state=sub_region or "maharashtra")
    elif r == "australia":
        from backend.adapters.australia.electrical_adapter import AustraliaElectricalAdapter
        return AustraliaElectricalAdapter(state=sub_region or "nsw")
    else:
        raise ValueError(
            f"Unknown region '{region}'. Supported: 'gcc', 'europe', 'india', 'australia'"
        )
