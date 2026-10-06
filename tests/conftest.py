"""Global pytest configuration for medical_cv."""
from __future__ import annotations

import os

# Prevent Windows OpenBLAS thread allocation exhaustion
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
