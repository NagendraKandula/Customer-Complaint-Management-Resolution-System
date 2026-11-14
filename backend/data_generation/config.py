
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"

# Reproducibility
SEED = 20261022

# Dataset scale
# 1.0 = full dataset
# 0.1 = approximately 10% of transactional data
SCALE = 1.0

DATASET_SIZE = {
    "teams": 8,
    "agents": 40,
    "categories": 10,
    "priority_rules": 12,
    "sla_policies": 4,
    "customers": 5000,
    "products": 100,
    "orders": 8000,
    "complaints": 2000,
    "messages": 6000,
}

# Synthetic data date range
START_DATE = "2025-01-01"
END_DATE = "2026-10-31"

# Priority distribution (initial target)
PRIORITY_DISTRIBUTION = {
    "P1": 0.05,
    "P2": 0.15,
    "P3": 0.35,
    "P4": 0.45,
}

# Anomaly generation
GENERATE_ANOMALIES = True

# Database insertion
BATCH_SIZE = 500
