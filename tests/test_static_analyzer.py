"""Tests for the static accessibility analyzer."""

from pathlib import Path

import pytest

from a11y_validator.analyzers.static import analyze_html
from a11y_validator.models import Severity

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def bad_html():
    return (FIXTURES / "bad_page.html").read_text()


@pytest.fixture
def good_html():
    return (FIXTURES / "good_page.html").read_text()


class TestImageAlt:
    def test_detects_missing_alt(self, bad_html):
        findings, _ = analyze_html(bad_html)
        alt_findings = [f for f in findings if f.rule_id == "WCAG-1.1.1-img-alt"]
        assert len(alt_findings) >= 1
        assert alt_findings[0].severity == Severity.CRITICAL

    def test_good_alt_no_finding(self, good_html):
        findings, _ = analyze_html(good_html)
        alt_findings = [f for f in findings if f.rule_id == "WCAG-1.1.1-img-alt"]
        assert len(alt_findings) == 0


class TestHeadingOrder:
    def test_detects_skipped_heading(self, bad_html):
        findings, _ = analyze_html(bad_html)
        heading_findings = [f for f in findings if f.rule_id == "WCAG-1.3.1-heading-order"]
        assert len(heading_findings) >= 1

    def test_proper_heading_order(self, good_html):
        findings, _ = analyze_html(good_html)
        heading_findings = [f for f in findings if f.rule_id == "WCAG-1.3.1-heading-order"]
        assert len(heading_findings) == 0


class TestPageTitle:
    def test_detects_empty_title(self, bad_html):
        findings, _ = analyze_html(bad_html)
        title_findings = [f for f in findings if f.rule_id == "WCAG-2.4.2-page-title"]
        assert len(title_findings) >= 1

    def test_good_title(self, good_html):
        findings, _ = analyze_html(good_html)
        title_findings = [f for f in findings if f.rule_id == "WCAG-2.4.2-page-title"]
        assert len(title_findings) == 0


class TestLanguage:
    def test_detects_missing_lang(self, bad_html):
        findings, _ = analyze_html(bad_html)
        lang_findings = [f for f in findings if f.rule_id == "WCAG-3.1.1-html-lang"]
        assert len(lang_findings) >= 1

    def test_has_lang(self, good_html):
        findings, _ = analyze_html(good_html)
        lang_findings = [f for f in findings if f.rule_id == "WCAG-3.1.1-html-lang"]
        assert len(lang_findings) == 0


class TestFormLabels:
    def test_detects_unlabeled_input(self, bad_html):
        findings, _ = analyze_html(bad_html)
        label_findings = [f for f in findings if f.rule_id == "WCAG-4.1.2-input-label"]
        assert len(label_findings) >= 1

    def test_labeled_input_ok(self, good_html):
        findings, _ = analyze_html(good_html)
        label_findings = [f for f in findings if f.rule_id == "WCAG-4.1.2-input-label"]
        assert len(label_findings) == 0


class TestLinks:
    def test_detects_empty_link(self, bad_html):
        findings, _ = analyze_html(bad_html)
        link_findings = [f for f in findings if f.rule_id == "WCAG-2.4.4-link-name"]
        assert len(link_findings) >= 1

    def test_detects_generic_link_text(self, bad_html):
        findings, _ = analyze_html(bad_html)
        generic_findings = [f for f in findings if f.rule_id == "WCAG-2.4.4-link-generic"]
        assert len(generic_findings) >= 1

    def test_descriptive_link_ok(self, good_html):
        findings, _ = analyze_html(good_html)
        link_findings = [f for f in findings if "2.4.4" in f.rule_id]
        assert len(link_findings) == 0


class TestBypassBlocks:
    def test_detects_no_skip_link(self, bad_html):
        findings, _ = analyze_html(bad_html)
        bypass_findings = [f for f in findings if f.rule_id == "WCAG-2.4.1-bypass"]
        # bad_page has no skip link and no <main>
        assert len(bypass_findings) >= 1

    def test_skip_link_present(self, good_html):
        findings, _ = analyze_html(good_html)
        bypass_findings = [f for f in findings if f.rule_id == "WCAG-2.4.1-bypass"]
        assert len(bypass_findings) == 0


class TestElementsCounted:
    def test_counts_elements(self, bad_html):
        _, count = analyze_html(bad_html)
        assert count > 0

    def test_good_page_counts(self, good_html):
        findings, count = analyze_html(good_html)
        assert count > 0


class TestBadVsGood:
    def test_bad_page_has_more_issues(self, bad_html, good_html):
        bad_findings, _ = analyze_html(bad_html)
        good_findings, _ = analyze_html(good_html)
        assert len(bad_findings) > len(good_findings)
