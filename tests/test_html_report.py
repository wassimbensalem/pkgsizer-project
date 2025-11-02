"""Tests for HTML report generation."""

from pathlib import Path

from pkgsizer.dist_metadata import DistributionInfo
from pkgsizer.graph import DependencyNode
from pkgsizer.html_report import render_html_report, write_html_report
from pkgsizer.scanner import PackageResult, ScanResults


def _make_results() -> ScanResults:
    results = ScanResults()
    results.site_packages_path = Path("/fake/site-packages")

    def add_pkg(name: str, size: int, depth: int = 0, direct: bool = True) -> None:
        dist = DistributionInfo(name=name, version="1.0.0", location=Path(f"/fake/{name}"))
        node = DependencyNode(dist, depth=depth, direct=direct)
        pkg = PackageResult(dist, node, total_size=size, file_count=10)
        results.add_package(pkg)

    add_pkg("alpha", 8_000_000)
    add_pkg("beta", 4_000_000, depth=1, direct=False)
    add_pkg("gamma", 2_000_000)
    return results


def test_render_html_report_contains_expected_content(tmp_path):
    results = _make_results()

    html = render_html_report(results, top=5, sort_by="size", include_dependencies=False)

    assert "pkgsizer Report" in html
    assert "alpha" in html
    assert "beta" in html
    assert "Size (MB)" in html

    output_path = tmp_path / "report.html"
    write_html_report(results, output_path, top=5)

    assert output_path.exists()
    saved = output_path.read_text(encoding="utf-8")
    assert "pkgsizer Report" in saved
    assert "alpha" in saved

