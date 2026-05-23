import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringConfig:
    alpha: float = 1.0
    beta: float = 1e-9
    gamma: float = 1.0


SCORING_CONFIG = ScoringConfig()

ADMIN_KEY = os.getenv("AQIS_ADMIN_KEY", "aqis-admin")
REFRESH_SECONDS = int(os.getenv("AQIS_REFRESH_SECONDS", "30"))
