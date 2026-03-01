"""Datetime normalization helpers for deterministic astronomy calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class TimeInput:
    """Input timestamp in local time with explicit timezone info."""

    value: datetime


class TimeNormalizationError(ValueError):
    """Raised when a datetime value is not timezone-aware."""


def normalize_to_utc(time_input: TimeInput | datetime) -> datetime:
    """Normalize a timezone-aware datetime to UTC with millisecond fidelity.

    Args:
        time_input: Either `TimeInput` or a timezone-aware `datetime`.

    Returns:
        UTC normalized `datetime`.

    Raises:
        TimeNormalizationError: If datetime is timezone naive.
    """

    value = time_input.value if isinstance(time_input, TimeInput) else time_input
    if value.tzinfo is None or value.utcoffset() is None:
        raise TimeNormalizationError("Datetime must be timezone-aware.")
    return value.astimezone(timezone.utc)
