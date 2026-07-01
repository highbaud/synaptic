"""Classify content by privacy level and redact unsafe material before output.

This layer is deliberately conservative and fully local. It NEVER calls an
external model. The rule: a note's privacy is the MOST restrictive of (a) its
declared frontmatter level and (b) what the content scanner detects. Better to
hide something professional than to surface something private.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Ordered from least to most restrictive.
PRIVACY_ORDER = ["public", "professional", "personal_sensitive", "nsfw", "excluded"]
_RANK = {level: i for i, level in enumerate(PRIVACY_ORDER)}

# Keyword signals. Intentionally simple + auditable; an LLM pass can refine later.
_NSFW_PATTERNS = [
    r"\bnsfw\b", r"\bporn\w*", r"\bsexual\b", r"\bsex\b", r"\bnude\b", r"\bnudes?\b",
    r"\bescort\b", r"\bxxx\b", r"\bonlyfans\b", r"\bhookup\b", r"\bgenital\w*",
]
_SENSITIVE_PATTERNS = [
    r"\bdivorce\b", r"\baffair\b", r"\bcheat(?:ing|ed)?\b", r"\brehab\b",
    r"\baddict\w*", r"\balcoholic\b", r"\bdrunk\b", r"\bhigh on\b", r"\bcocaine\b",
    r"\bdepress\w*", r"\bsuicid\w*", r"\btherapy\b", r"\bmedication\b", r"\bdiagnos\w*",
    r"\bbankrupt\w*", r"\bfired\b", r"\blawsuit\b", r"\barrest\w*", r"\bprison\b",
    r"\bgossip\b", r"\bembarrass\w*", r"\bsecret\b", r"\bconfidential\b",
    r"\bmistress\b", r"\bex-?wife\b", r"\bex-?husband\b", r"\bhates? his\b",
]
# Lines that look like raw secrets — always stripped from any output.
_SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{16,}", r"\bAKIA[0-9A-Z]{16}\b",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"\bpassword\s*[:=]\s*\S+",
]

_NSFW_RE = re.compile("|".join(_NSFW_PATTERNS), re.IGNORECASE)
_SENSITIVE_RE = re.compile("|".join(_SENSITIVE_PATTERNS), re.IGNORECASE)
_SECRET_RE = re.compile("|".join(_SECRET_PATTERNS), re.IGNORECASE)


def _max_restrictive(a: str, b: str) -> str:
    return a if _RANK.get(a, 1) >= _RANK.get(b, 1) else b


@dataclass
class PrivacyVerdict:
    level: str
    detected_level: str            # what the scanner alone concluded
    declared_level: str | None     # frontmatter value, if any
    reasons: list[str] = field(default_factory=list)

    @property
    def safe_for_brief(self) -> bool:
        return self.level in ("public", "professional")


class PrivacyClassifier:
    def __init__(self, default_level: str = "professional",
                 allowed_levels: list[str] | None = None):
        self.default_level = default_level
        self.allowed_levels = allowed_levels or ["public", "professional"]

    def classify(self, text: str, declared: str | None = None) -> PrivacyVerdict:
        reasons: list[str] = []
        detected = self.default_level

        if _NSFW_RE.search(text):
            detected = "nsfw"
            reasons.append("matched NSFW content signal")
        elif _SENSITIVE_RE.search(text):
            detected = "personal_sensitive"
            reasons.append("matched personal-sensitive content signal")

        declared_norm = declared.lower() if declared else None
        if declared_norm and declared_norm not in _RANK:
            reasons.append(f"ignored unknown declared level '{declared}'")
            declared_norm = None

        # Final = most restrictive of declared and detected.
        level = detected
        if declared_norm:
            level = _max_restrictive(declared_norm, detected)
            if level != detected:
                reasons.append(f"frontmatter declared '{declared_norm}'")

        return PrivacyVerdict(
            level=level,
            detected_level=detected,
            declared_level=declared_norm,
            reasons=reasons,
        )

    def is_allowed_for_brief(self, level: str) -> bool:
        return level in self.allowed_levels

    def redact(self, text: str) -> str:
        """Strip secrets and any line carrying an NSFW/sensitive signal.

        Used as a final safety pass on text headed into a professional brief,
        even after note-level filtering — defense in depth.
        """
        out: list[str] = []
        for line in text.splitlines():
            if _SECRET_RE.search(line):
                out.append("[redacted: secret]")
                continue
            if _NSFW_RE.search(line) or _SENSITIVE_RE.search(line):
                out.append("[redacted: sensitive]")
                continue
            out.append(line)
        return "\n".join(out)


def is_brief_safe(verdict: PrivacyVerdict, allowed_levels: list[str]) -> bool:
    return verdict.level in allowed_levels
