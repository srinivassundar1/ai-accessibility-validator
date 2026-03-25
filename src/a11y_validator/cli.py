"""CLI entry point for the accessibility validator."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from a11y_validator.analyzers.static import analyze_html
from a11y_validator.models import A11yReport, Severity
from a11y_validator.reports.generator import generate_report

console = Console()


@click.group()
def main():
    """AI Accessibility Validator — WCAG 2.1 and Section 508 compliance."""
    pass


@main.command()
@click.argument("source")
@click.option("--output", "-o", default=None, help="Output report file path.")
@click.option("--format", "fmt", default="terminal", type=click.Choice(["terminal", "html", "json"]))
@click.option("--use-ai/--no-ai", default=False, help="Enable AI vision analysis.")
def scan(source: str, output: str | None, fmt: str, use_ai: bool):
    """Scan an HTML file or URL for accessibility issues."""
    console.print("\n[bold]♿ AI Accessibility Validator[/bold]")
    console.print(f"   Source: {source}")
    console.print(f"   AI Analysis: {'enabled' if use_ai else 'disabled'}\n")

    start = time.time()

    # Load HTML
    source_path = Path(source)
    if source_path.exists():
        html = source_path.read_text(encoding="utf-8", errors="ignore")
    else:
        console.print(f"   [red]Error: File not found: {source}[/red]")
        sys.exit(1)

    # Run static analysis
    with console.status("Running static WCAG analysis..."):
        findings, elements_checked = analyze_html(html, source)
    console.print(f"   Checked {elements_checked} elements, found {len(findings)} issues")

    duration = time.time() - start

    report = A11yReport(
        url_or_file=source,
        total_elements_checked=elements_checked,
        findings=findings,
        duration_seconds=duration,
    )

    if fmt == "terminal" or output is None:
        _print_terminal(report)
    if output:
        file_fmt = fmt if fmt != "terminal" else "html"
        generate_report(report, output, file_fmt)
        console.print(f"\n   Report saved: {output}")

    console.print(f"\n   Scan completed in {duration:.1f}s")

    if report.critical_count > 0:
        sys.exit(2)
    elif report.serious_count > 0:
        sys.exit(1)


def _print_terminal(report: A11yReport) -> None:
    if not report.findings:
        console.print("\n   [green]✓ No accessibility issues found![/green]")
        return

    table = Table(title=f"Accessibility Issues ({len(report.findings)} found)")
    table.add_column("Severity", width=10)
    table.add_column("Rule", width=28)
    table.add_column("WCAG", width=24)
    table.add_column("Description", width=50)

    styles = {
        Severity.CRITICAL: "red bold",
        Severity.SERIOUS: "red",
        Severity.MODERATE: "yellow",
        Severity.MINOR: "blue",
    }

    for f in sorted(report.findings, key=lambda x: list(Severity).index(x.severity)):
        style = styles.get(f.severity, "")
        table.add_row(
            f"[{style}]{f.severity.value.upper()}[/{style}]",
            f.rule_id,
            f.wcag_criterion,
            f.description[:70],
        )

    console.print(table)
    console.print(f"\n   Pass rate: {report.pass_rate:.0%}")
    console.print(f"   [red bold]Critical: {report.critical_count}[/red bold]  "
                  f"[red]Serious: {report.serious_count}[/red]  "
                  f"[yellow]Moderate: {sum(1 for f in report.findings if f.severity == Severity.MODERATE)}[/yellow]  "
                  f"[blue]Minor: {sum(1 for f in report.findings if f.severity == Severity.MINOR)}[/blue]")


if __name__ == "__main__":
    main()
