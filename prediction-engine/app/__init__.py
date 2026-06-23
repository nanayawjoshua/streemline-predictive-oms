"""
Prediction Engine — Streemline Predictive OMS.

Two-tier outage prediction for ECG:
- Tier A: Zone-level risk (6-hour window, weather + outage density)
- Tier B: Transformer-level risk (48-hour window, asset data + load)
"""

__version__ = "0.1.0"
