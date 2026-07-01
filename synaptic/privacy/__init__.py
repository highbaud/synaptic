"""Privacy classification and redaction. Runs locally, always."""

from .classifier import (
    PRIVACY_ORDER,
    PrivacyClassifier,
    PrivacyVerdict,
    is_brief_safe,
)

__all__ = [
    "PRIVACY_ORDER",
    "PrivacyClassifier",
    "PrivacyVerdict",
    "is_brief_safe",
]
