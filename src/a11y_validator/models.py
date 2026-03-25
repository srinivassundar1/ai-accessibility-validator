"""Core data models for accessibility findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"  # Blocks access entirely
    SERIOUS = "serious"    # Major barrier
    MODERATE = "moderate"  # Significant difficulty
    MINOR = "minor"        # Inconvenience


class Standard(str, Enum):
    WCAG21 = "wcag21"
    SECTION508 = "section508"


@dataclass
class A11yFinding:
    rule_id: str
    severity: Severity
    description: str
    remediation: str
    wcag_criterion: str  # e.g., "1.1.1 Non-text Content"
    section_508_ref: str | None = None  # e.g., "1194.22(a)"
    element: str | None = None  # HTML snippet
    selector: str | None = None  # CSS selector
    source: str = "static"  # "static" or "ai"
    suggested_fix: str | None = None  # AI-generated fix


@dataclass
class A11yReport:
    url_or_file: str
    total_elements_checked: int
    findings: list[A11yFinding] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def serious_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.SERIOUS)

    @property
    def pass_rate(self) -> float:
        if self.total_elements_checked == 0:
            return 1.0
        return 1.0 - (len(self.findings) / self.total_elements_checked)
