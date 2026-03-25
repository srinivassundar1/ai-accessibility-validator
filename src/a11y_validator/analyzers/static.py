"""Static DOM-based WCAG 2.1 and Section 508 accessibility analyzer."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from a11y_validator.models import A11yFinding, Severity


def analyze_html(html: str, source_url: str = "") -> tuple[list[A11yFinding], int]:
    """Analyze HTML content for accessibility violations. Returns (findings, elements_checked)."""
    soup = BeautifulSoup(html, "lxml")
    findings: list[A11yFinding] = []
    elements_checked = 0

    # ─── 1.1.1 Non-text Content ──────────────────────────────────
    for img in soup.find_all("img"):
        elements_checked += 1
        alt = img.get("alt")
        if alt is None:
            findings.append(A11yFinding(
                rule_id="WCAG-1.1.1-img-alt",
                severity=Severity.CRITICAL,
                description="Image missing alt attribute. Screen readers cannot describe this image.",
                remediation="Add an alt attribute describing the image content, or alt=\"\" for decorative images.",
                wcag_criterion="1.1.1 Non-text Content",
                section_508_ref="1194.22(a)",
                element=str(img)[:200],
                selector=_build_selector(img),
            ))
        elif alt.strip() == "" and not _is_decorative(img):
            findings.append(A11yFinding(
                rule_id="WCAG-1.1.1-img-alt-empty",
                severity=Severity.MODERATE,
                description="Image has empty alt text but may not be decorative.",
                remediation="Add descriptive alt text if the image conveys information.",
                wcag_criterion="1.1.1 Non-text Content",
                section_508_ref="1194.22(a)",
                element=str(img)[:200],
                selector=_build_selector(img),
            ))

    # ─── 1.3.1 Info and Relationships ────────────────────────────
    # Check for proper heading hierarchy
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    prev_level = 0
    for heading in headings:
        elements_checked += 1
        level = int(heading.name[1])
        if level > prev_level + 1 and prev_level > 0:
            findings.append(A11yFinding(
                rule_id="WCAG-1.3.1-heading-order",
                severity=Severity.MODERATE,
                description=f"Heading level skipped: h{prev_level} → h{level}. Headings should not skip levels.",
                remediation=f"Use h{prev_level + 1} instead of h{level}, or restructure the heading hierarchy.",
                wcag_criterion="1.3.1 Info and Relationships",
                element=str(heading)[:200],
                selector=_build_selector(heading),
            ))
        prev_level = level

    # ─── 1.4.3 Contrast (Minimum) ────────────────────────────────
    # Check for inline styles with potentially low contrast
    for el in soup.find_all(style=True):
        elements_checked += 1
        style = el.get("style", "")
        if "color" in style and "background" not in style:
            findings.append(A11yFinding(
                rule_id="WCAG-1.4.3-contrast-check",
                severity=Severity.MINOR,
                description="Element has inline text color without explicit background — contrast may be insufficient.",
                remediation="Ensure text color has at least 4.5:1 contrast ratio against its background.",
                wcag_criterion="1.4.3 Contrast (Minimum)",
                section_508_ref="1194.22(c)",
                element=str(el)[:200],
                selector=_build_selector(el),
            ))

    # ─── 2.4.1 Bypass Blocks ─────────────────────────────────────
    elements_checked += 1
    skip_link = soup.find("a", href=re.compile(r"^#"))
    main_landmark = soup.find("main") or soup.find(role="main")
    if not skip_link and not main_landmark:
        findings.append(A11yFinding(
            rule_id="WCAG-2.4.1-bypass",
            severity=Severity.SERIOUS,
            description="No skip navigation link or main landmark found.",
            remediation="Add a 'Skip to main content' link or use <main> landmark.",
            wcag_criterion="2.4.1 Bypass Blocks",
            section_508_ref="1194.22(o)",
        ))

    # ─── 2.4.2 Page Titled ───────────────────────────────────────
    elements_checked += 1
    title = soup.find("title")
    if not title or not title.string or not title.string.strip():
        findings.append(A11yFinding(
            rule_id="WCAG-2.4.2-page-title",
            severity=Severity.SERIOUS,
            description="Page is missing a <title> element or title is empty.",
            remediation="Add a descriptive <title> that identifies the page purpose.",
            wcag_criterion="2.4.2 Page Titled",
        ))

    # ─── 3.1.1 Language of Page ───────────────────────────────────
    elements_checked += 1
    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        findings.append(A11yFinding(
            rule_id="WCAG-3.1.1-html-lang",
            severity=Severity.SERIOUS,
            description="<html> element missing lang attribute.",
            remediation='Add lang attribute: <html lang="en">',
            wcag_criterion="3.1.1 Language of Page",
            section_508_ref="1194.22(a)",
        ))

    # ─── 4.1.2 Name, Role, Value ─────────────────────────────────
    # Check form inputs have labels
    for input_el in soup.find_all(["input", "select", "textarea"]):
        elements_checked += 1
        input_type = input_el.get("type", "text")
        if input_type in ("hidden", "submit", "button", "reset"):
            continue

        has_label = bool(
            input_el.get("aria-label")
            or input_el.get("aria-labelledby")
            or input_el.get("title")
            or (input_el.get("id") and soup.find("label", attrs={"for": input_el.get("id")}))
        )

        if not has_label:
            findings.append(A11yFinding(
                rule_id="WCAG-4.1.2-input-label",
                severity=Severity.CRITICAL,
                description=f"Form input ({input_type}) has no accessible label.",
                remediation="Add a <label for=\"id\">, aria-label, or aria-labelledby attribute.",
                wcag_criterion="4.1.2 Name, Role, Value",
                section_508_ref="1194.22(n)",
                element=str(input_el)[:200],
                selector=_build_selector(input_el),
            ))

    # ─── 2.4.4 Link Purpose ──────────────────────────────────────
    for link in soup.find_all("a"):
        elements_checked += 1
        text = link.get_text(strip=True)
        aria_label = link.get("aria-label", "")
        if not text and not aria_label and not link.find("img", alt=True):
            findings.append(A11yFinding(
                rule_id="WCAG-2.4.4-link-name",
                severity=Severity.SERIOUS,
                description="Link has no discernible text for screen readers.",
                remediation="Add link text, aria-label, or an image with alt text inside the link.",
                wcag_criterion="2.4.4 Link Purpose (In Context)",
                element=str(link)[:200],
                selector=_build_selector(link),
            ))
        elif text.lower() in ("click here", "here", "read more", "more", "link"):
            findings.append(A11yFinding(
                rule_id="WCAG-2.4.4-link-generic",
                severity=Severity.MODERATE,
                description=f'Link text "{text}" is generic and not descriptive.',
                remediation="Use descriptive link text that explains the destination.",
                wcag_criterion="2.4.4 Link Purpose (In Context)",
                element=str(link)[:200],
                selector=_build_selector(link),
            ))

    return findings, elements_checked


def _build_selector(tag: Tag) -> str:
    """Build a simple CSS selector for an element."""
    parts = [tag.name]
    if tag.get("id"):
        parts.append(f"#{tag['id']}")
    elif tag.get("class"):
        classes = tag["class"] if isinstance(tag["class"], list) else [tag["class"]]
        parts.append("." + ".".join(classes[:2]))
    return "".join(parts)


def _is_decorative(img: Tag) -> bool:
    """Heuristic: image is likely decorative if it has role=presentation or is inside a link with text."""
    if img.get("role") in ("presentation", "none"):
        return True
    parent = img.parent
    if parent and parent.name == "a" and parent.get_text(strip=True):
        return True
    return False
