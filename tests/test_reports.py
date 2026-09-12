"""Tests for report generation."""

import json
from pathlib import Path

from a11y_validator.models import A11yFinding, A11yReport, Severity
from a11y_validator.reports.generator import generate_report


def _make_finding(**overrides) -> A11yFinding:
    defaults = {
        "rule_id": "WCAG-1.1.1-img-alt",
        "severity": Severity.CRITICAL,
        "description": "Image missing alt",
        "remediation": "Add alt attribute",
        "wcag_criterion": "1.1.1 Non-text Content",
    }
    defaults.update(overrides)
    return A11yFinding(**defaults)


class TestJsonReport:
    def test_generates_valid_json(self, tmp_path):
        output = str(tmp_path / "report.json")
        report = A11yReport(url_or_file="test.html", total_elements_checked=10,
                            findings=[_make_finding()])
        generate_report(report, output, "json")
        data = json.loads(Path(output).read_text())
        assert data["total_findings"] == 1
        assert data["summary"]["critical"] == 1

    def test_pass_rate(self, tmp_path):
        output = str(tmp_path / "report.json")
        report = A11yReport(url_or_file="test.html", total_elements_checked=10,
                            findings=[_make_finding()])
        generate_report(report, output, "json")
        data = json.loads(Path(output).read_text())
        assert data["pass_rate"] == 0.9


class TestHtmlReport:
    def test_generates_html(self, tmp_path):
        output = str(tmp_path / "report.html")
        report = A11yReport(url_or_file="test.html", total_elements_checked=5,
                            findings=[_make_finding()])
        generate_report(report, output, "html")
        html = Path(output).read_text()
        assert "<!DOCTYPE html>" in html
        assert "WCAG-1.1.1" in html
        assert "Section 508" in html
