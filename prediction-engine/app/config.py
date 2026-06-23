import os
import logging

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_BASE_URL = os.getenv("WEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
ZONE_RISK_ENABLED = os.getenv("ZONE_RISK_ENABLED", "true").lower() == "true"
TRANSFORMER_RISK_ENABLED = os.getenv("TRANSFORMER_RISK_ENABLED", "false").lower() == "true"
ZEUS_API_BASE = os.getenv("ZEUS_API_BASE", "")
ZEUS_API_KEY = os.getenv("ZEUS_API_KEY", "")
HITL_ENABLED = os.getenv("HITL_ENABLED", "true").lower() == "true"

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger("prediction-engine")
