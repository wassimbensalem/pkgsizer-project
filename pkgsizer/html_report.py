"""Generate interactive HTML reports for pkgsizer results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import json

from pkgsizer.report import (
    format_size,
    to_json,
    _calculate_dependency_sizes,  # type: ignore[attr-defined]
)
from pkgsizer.scanner import PackageResult, ScanResults


if TYPE_CHECKING:  # pragma: no cover
    from jinja2 import Environment as JinjaEnvironment


_ENV: Optional["JinjaEnvironment"] = None


def _get_jinja_environment() -> "JinjaEnvironment":
    """Return a cached Jinja2 environment for rendering HTML templates."""
    global _ENV  # noqa: PLW0603 - cache per process
    if _ENV is None:
        try:
            from jinja2 import Environment as JinjaEnvironment
            from jinja2 import FileSystemLoader, select_autoescape
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "HTML reports require Jinja2. Install pkgsizer[html] and retry."
            ) from exc

        template_dir = resources.files("pkgsizer") / "templates"
        loader = FileSystemLoader(str(template_dir))
        env = JinjaEnvironment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=False,
        )

        def _format_number(value: Any) -> str:
            try:
                return f"{int(value):,}"
            except (ValueError, TypeError):
                return str(value)

        env.filters["format_number"] = _format_number
        _ENV = env
    return _ENV


@dataclass
class _PackageRow:
    """Table row data for HTML template."""

    name: str
    version: str
    size: str
    size_bytes: int
    size_with_deps: str
    size_with_deps_bytes: int
    file_count: int
    depth: int
    type: str
    editable: bool
    location: str


def _sort_packages(packages: list[PackageResult], sort_by: str) -> list[PackageResult]:
    if sort_by == "files":
        return sorted(packages, key=lambda p: p.file_count, reverse=True)
    return sorted(packages, key=lambda p: p.total_size, reverse=True)


def _compute_insights(
    packages: list[_PackageRow],
    include_dependencies: bool,
) -> dict[str, Any]:
    if not packages:
        return {
            "largest_package": {"name": "—", "size": "0 B"},
            "median_size": "0 B",
            "average_size": "0 B",
            "direct_packages": 0,
            "transitive_packages": 0,
            "largest_with_deps": {"name": "—", "size": "0 B"},
        }

    sizes = sorted(pkg.size_bytes for pkg in packages)
    count = len(sizes)
    median_value = sizes[count // 2] if count % 2 else int((sizes[count // 2 - 1] + sizes[count // 2]) / 2)
    average_value = sum(sizes) / count

    largest_pkg = max(packages, key=lambda p: p.size_bytes)
    direct_count = sum(1 for pkg in packages if pkg.type == "direct")
    transitive_count = count - direct_count

    insights: dict[str, Any] = {
        "largest_package": {"name": largest_pkg.name, "size": largest_pkg.size},
        "median_size": format_size(median_value),
        "average_size": format_size(int(average_value)),
        "direct_packages": direct_count,
        "transitive_packages": transitive_count,
        "largest_with_deps": {"name": "—", "size": "0 B"},
    }

    if include_dependencies:
        largest_with_deps = max(packages, key=lambda p: p.size_with_deps_bytes, default=None)
        if largest_with_deps:
            insights["largest_with_deps"] = {
                "name": largest_with_deps.name,
                "size": largest_with_deps.size_with_deps,
            }

    return insights


def _build_package_rows(
    packages: list[PackageResult],
    *,
    include_dependencies: bool,
    sort_by: str,
    top: Optional[int],
) -> tuple[list[_PackageRow], dict[str, int]]:
    sorted_packages = _sort_packages(packages, sort_by)

    if top:
        display_packages = sorted_packages[:top]
    else:
        display_packages = sorted_packages

    dep_sizes: dict[str, int] = {}
    if include_dependencies:
        dep_sizes = _calculate_dependency_sizes(packages)

    table_rows: list[_PackageRow] = []
    for pkg in display_packages:
        dist_info = pkg.dist_info
        node = pkg.node
        pkg_name_lower = dist_info.name.lower()
        with_deps_size = dep_sizes.get(pkg_name_lower, pkg.total_size)
        row = _PackageRow(
            name=dist_info.name,
            version=dist_info.version,
            size=format_size(pkg.total_size),
            size_bytes=pkg.total_size,
            size_with_deps=(format_size(with_deps_size) if include_dependencies else "—"),
            size_with_deps_bytes=with_deps_size if include_dependencies else 0,
            file_count=pkg.file_count,
            depth=node.depth,
            type="direct" if node.direct else "transitive",
            editable=dist_info.editable,
            location=str(dist_info.location),
        )
        table_rows.append(row)

    return table_rows, dep_sizes


def render_html_report(
    results: ScanResults,
    *,
    top: Optional[int] = None,
    sort_by: str = "size",
    include_dependencies: bool = False,
    command_invocation: Optional[str] = None,
) -> str:
    """Render scan results as an interactive HTML report."""

    env = _get_jinja_environment()
    template = env.get_template("report.html")

    table_rows, dep_sizes = _build_package_rows(
        results.packages,
        include_dependencies=include_dependencies,
        sort_by=sort_by,
        top=top,
    )

    chart_packages = table_rows[: min(10, len(table_rows))]
    chart_data = [
        {
            "name": pkg.name,
            "size_mb": pkg.size_bytes / (1024 * 1024) if pkg.size_bytes else 0,
            "size": pkg.size,
        }
        for pkg in chart_packages
    ]

    summary = {
        "package_count": len(results.packages),
        "total_size_bytes": results.total_size,
        "total_size_formatted": format_size(results.total_size),
        "total_files": results.total_files,
        "site_packages": str(results.site_packages_path or "(unknown)"),
        "total_with_deps": format_size(sum(dep_sizes.values())) if include_dependencies and dep_sizes else "—",
    }

    context = {
        "title": "pkgsizer HTML Report",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "packages": table_rows,
        "chart_data": chart_data,
        "include_dependencies": include_dependencies,
        "command_invocation": command_invocation or "pkgsizer …",
        "displayed_count": len(table_rows),
        "total_packages": len(results.packages),
        "sort_label": "size" if sort_by == "size" else "file count",
        "insights": _compute_insights(table_rows, include_dependencies),
    }

    # Include full JSON data for potential embedding/debugging
    context["json_payload"] = json.dumps(to_json(results), indent=2)

    return template.render(context)


def write_html_report(
    results: ScanResults,
    output_path: Path,
    *,
    top: Optional[int] = None,
    sort_by: str = "size",
    include_dependencies: bool = False,
    command_invocation: Optional[str] = None,
) -> None:
    """Generate and write the HTML report to disk."""

    html = render_html_report(
        results,
        top=top,
        sort_by=sort_by,
        include_dependencies=include_dependencies,
        command_invocation=command_invocation,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

