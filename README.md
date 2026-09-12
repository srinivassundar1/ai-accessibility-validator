# AI Accessibility Validator

> AI-powered website accessibility validator that combines static DOM analysis with vision model intelligence to evaluate Section 508 and WCAG 2.1 compliance.

[![CI](https://github.com/srinivassundar1/ai-accessibility-validator/actions/workflows/ci.yml/badge.svg)]()
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)]()

## Problem

Over 61 million Americans live with disabilities. The [Americans with Disabilities Act (ADA)](https://www.ada.gov/) and [Section 508 of the Rehabilitation Act](https://www.section508.gov/) require digital accessibility, yet the DOJ reports widespread non-compliance. Existing tools like axe-core and Lighthouse catch ~30-40% of WCAG issues through static analysis alone — they miss visual layout problems, context-dependent alt text quality, and semantic structure issues that require human-like understanding.

**References:**
- [Section 508 Standards](https://www.access-board.gov/ict/)
- [WCAG 2.1 AA](https://www.w3.org/TR/WCAG21/)
- [DOJ Web Accessibility Guidance (2022)](https://www.ada.gov/resources/web-guidance/)

## Solution

This tool combines traditional DOM-based WCAG rule checking with AI vision models to catch accessibility issues that static analysis misses — including poor color contrast in complex layouts, misleading alt text, and visual hierarchy problems.

## Quick Start

```bash
pip install ai-accessibility-validator

# Scan a local HTML file
a11y scan index.html

# Scan with AI vision analysis (requires OpenAI API key)
pip install ai-accessibility-validator[ai]
export OPENAI_API_KEY=your-key
a11y scan index.html --use-ai
```

## Features

- **Static WCAG analysis**: 15+ DOM-based checks against WCAG 2.1 AA criteria
- **AI vision analysis**: GPT-4o screenshot analysis for visual accessibility issues
- **Alt text suggestions**: AI-generated alt text for images missing descriptions
- **Section 508 mapping**: Findings mapped to specific Section 508 requirements
- **Multiple formats**: Terminal, HTML, JSON output

## Architecture

```
HTML Input → DOM Parser → [Static Analyzer + AI Vision Analyzer] → Findings → Report
                ↓                    ↓                ↓
          BeautifulSoup      WCAG 2.1 Rules     OpenAI Vision
                             Section 508
```

## Standards Coverage

| Standard | Criteria Checked | Reference |
|----------|-----------------|-----------|
| WCAG 2.1 AA | 15 success criteria | W3C WCAG 2.1 |
| Section 508 | 10 requirements | 36 CFR Part 1194 |

## Related Projects

This is part of a portfolio focused on **AI for US public infrastructure**:
- [ai-compliance-auditor](../ai-compliance-auditor) — AI-powered NIST/HIPAA/SOC2 compliance scanning
- [infra-anomaly-detector](../infra-anomaly-detector) — ML-based infrastructure monitoring

## License

Apache 2.0 — Built for public benefit.
