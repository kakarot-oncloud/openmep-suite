from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent
STANDARDS_DATA_DIR = BASE_DIR / "standards_data"

SUPPORTED_REGIONS = ["gcc", "europe", "india", "australia"]

GCC_SUB_REGIONS = {
    "uae_dubai": {"name": "UAE - Dubai", "authority": "DEWA"},
    "uae_abudhabi": {"name": "UAE - Abu Dhabi", "authority": "ADDC"},
    "uae_sharjah": {"name": "UAE - Sharjah", "authority": "SEWA"},
    "saudi": {"name": "Saudi Arabia", "authority": "SEC/SBC"},
    "qatar": {"name": "Qatar", "authority": "KAHRAMAA"},
    "kuwait": {"name": "Kuwait", "authority": "MEW"},
    "bahrain": {"name": "Bahrain", "authority": "Electricity Authority"},
    "oman": {"name": "Oman", "authority": "OETC"},
}

EUROPE_SUB_REGIONS = {
    "uk": {"name": "United Kingdom", "authority": "UKPN/National Grid"},
    "germany": {"name": "Germany", "authority": "Various DNO"},
    "france": {"name": "France", "authority": "Enedis"},
    "ireland": {"name": "Ireland", "authority": "ESB Networks"},
}

INDIA_STATES = {
    "maharashtra": {"name": "Maharashtra", "discom": "MSEDCL"},
    "delhi": {"name": "Delhi", "discom": "TPDDL/BRPL"},
    "karnataka": {"name": "Karnataka", "discom": "BESCOM"},
    "gujarat": {"name": "Gujarat", "discom": "DGVCL/MGVCL"},
    "tamil_nadu": {"name": "Tamil Nadu", "discom": "TANGEDCO"},
    "telangana": {"name": "Telangana", "discom": "TSSPDCL"},
    "rajasthan": {"name": "Rajasthan", "discom": "JVVNL"},
    "west_bengal": {"name": "West Bengal", "discom": "WBSEDCL"},
}

AUSTRALIA_STATES = {
    "nsw": {"name": "New South Wales", "distributor": "Ausgrid/Endeavour"},
    "vic": {"name": "Victoria", "distributor": "CitiPower/Powercor"},
    "qld": {"name": "Queensland", "distributor": "Energex/Ergon"},
    "sa": {"name": "South Australia", "distributor": "SA Power Networks"},
    "wa": {"name": "Western Australia", "distributor": "Western Power"},
    "tas": {"name": "Tasmania", "distributor": "TasNetworks"},
}


class Settings(BaseSettings):
    app_name: str = "OpenMEP API"
    version: str = "0.2.1"
    debug: bool = False
    api_prefix: str = "/api"

    # Optional API key authentication.
    # Set API_KEY in your .env to require X-API-Key header on all API requests.
    # Leave unset (default None) for development or private-network deployments.
    # See SECURITY.md and backend/api/auth.py for details.
    api_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
