"""Deterministic decay logic for memories."""
from __future__ import annotations

import math


def decay_rate(emotion_score: float) -> float:
    """Return a deterministic decay rate based on emotion score.

    Emotional memories decay slower; neutral memories decay faster.
    """
    return 0.02 if emotion_score >= 0.6 else 0.06


def apply_decay(importance: float, emotion_score: float, age_days: float) -> float:
    """Apply exponential decay to importance for a given age in days."""
    rate = decay_rate(emotion_score)
    return max(importance * math.exp(-rate * age_days), 0.0)
