from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib
import json
import platform
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def evaluate(actual: Any, operator: str, target: Any) -> bool:
    operations = {
        "eq": lambda a, b: a == b,
        "ne": lambda a, b: a != b,
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
        "between": lambda a, b: b[0] <= a <= b[1],
    }
    if operator not in operations:
        raise ValueError(f"Unsupported requirement operator: {operator}")
    return bool(operations[operator](actual, target))


def run_component(component: dict[str, Any]) -> dict[str, Any]:
    component_id = component["id"]
    module = importlib.import_module(component["module"])

    exporter = component.get("exporter")
    if exporter:
        getattr(module, exporter)()

    inspector = component.get("inspector")
    if not inspector:
        raise ValueError(f"Component {component_id} has no inspector")

    metrics = getattr(module, inspector)()
    if not isinstance(metrics, dict):
        raise TypeError(f"Inspector for {component_id} must return a dict")
    return metrics


def requirement_results(
    requirements: list[dict[str, Any]],
    metrics: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for requirement in requirements:
        result = dict(requirement)
        component_id = requirement.get("component")
        metric_name = requirement.get("metric")
        actual = metrics.get(component_id, {}).get(metric_name)
        result["actual"] = actual

        if component_id not in metrics or metric_name not in metrics.get(component_id, {}):
            result["status"] = "UNKNOWN"
            result["reason"] = "metric_not_available"
        else:
            try:
                passed = evaluate(actual, requirement["operator"], requirement.get("target"))
                result["status"] = "PASS" if passed else "FAIL"
            except Exception as exc:
                result["status"] = "UNKNOWN"
                result["reason"] = f"evaluation_error: {exc}"

        results.append(result)

    return results


def overall_status(
    results: list[dict[str, Any]],
    component_errors: list[dict[str, str]],
) -> str:
    if component_errors or any(item["status"] == "FAIL" for item in results):
        return "FAIL"
    if any(item["status"] == "UNKNOWN" for item in results):
        return "UNKNOWN"
    return "PASS"


def make_report(summary: dict[str, Any]) -> str:
    esc = lambda value: html.escape(str(value))
    counts = summary["counts"]

    requirement_rows = "".join(
        f"<tr><td>{esc(r['id'])}</td><td>{esc(r.get('title',''))}</td>"
        f"<td>{esc(r.get('actual'))}</td><td>{esc(r.get('operator'))} {esc(r.get('target'))}</td>"
        f"<td>{esc(r.get('unit',''))}</td><td class='status {r['status'].lower()}'>{esc(r['status'])}</td></tr>"
        for r in summary["requirements"]
    )

    metric_rows = "".join(
        f"<tr><td>{esc(component)}</td><td>{esc(name)}</td><td>{esc(value)}</td></tr>"
        for component, values in summary["metrics"].items()
        for name, value in values.items()
    )

    assumption_rows = "".join(
        f"<tr><td>{esc(a.get('id'))}</td><td>{esc(a.get('statement'))}</td>"
        f"<td>{esc(a.get('confidence'))}</td><td>{esc(a.get('status'))}</td></tr>"
        for a in summary["assumptions"]
    ) or "<tr><td colspan='4'>None recorded</td></tr>"

    risk_rows = "".join(
        f"<tr><td>{esc(r.get('id'))}</td><td>{esc(r.get('statement'))}</td>"
        f"<td>{esc(r.get('severity'))}</td><td>{esc(r.get('status'))}</td></tr>"
        for r in summary["risks"]
    ) or "<tr><td colspan='4'>None recorded</td></tr>"

    error_html = "".join(
        f"<li><strong>{esc(e['component'])}</strong>: {esc(e['error'])}</li>"
        for e in summary["component_errors"]
    ) or "<li>None</li>"

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Prototype Evidence — {esc(summary['project']['name'])}</title>
<style>
:root{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#161616;background:#f6f6f3}}
body{{margin:0;padding:32px}} main{{max-width:1180px;margin:auto}}
header{{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:28px}}
h1{{margin:0 0 6px;font-size:30px}} .muted{{color:#676767}} .badge{{padding:9px 14px;border:1px solid #bbb;border-radius:999px;font-weight:700;background:white}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0 28px}} .card{{background:white;border:1px solid #ddd;border-radius:12px;padding:16px}} .big{{font-size:26px;font-weight:750}}
section{{background:white;border:1px solid #ddd;border-radius:12px;padding:20px;margin:14px 0}} h2{{font-size:18px;margin:0 0 14px}}
table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{text-align:left;padding:10px 8px;border-bottom:1px solid #eee;vertical-align:top}} th{{color:#555;font-weight:650}}
.status{{font-weight:750}} .pass{{color:#176b36}} .fail{{color:#a22}} .unknown{{color:#8a6418}}
code,pre{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}
@media(max-width:800px){{body{{padding:16px}}.grid{{grid-template-columns:repeat(2,1fr)}}header{{display:block}}}}
</style>
</head>
<body><main>
<header>
<div><h1>{esc(summary['project']['name'])}</h1>
<div class='muted'>Run <code>{esc(summary['run_id'])}</code> · source <code>{esc(summary['provenance'].get('source_ref') or 'working-copy')}</code></div></div>
<div class='badge'>{esc(summary['status'])}</div>
</header>
<div class='grid'>
<div class='card'><div class='muted'>Requirements</div><div class='big'>{counts['total']}</div></div>
<div class='card'><div class='muted'>Pass</div><div class='big'>{counts['pass']}</div></div>
<div class='card'><div class='muted'>Fail</div><div class='big'>{counts['fail']}</div></div>
<div class='card'><div class='muted'>Unknown</div><div class='big'>{counts['unknown']}</div></div>
</div>
<section><h2>Requirement evidence</h2><table><thead><tr><th>ID</th><th>Requirement</th><th>Actual</th><th>Acceptance</th><th>Unit</th><th>Status</th></tr></thead><tbody>{requirement_rows}</tbody></table></section>
<section><h2>Measured digital metrics</h2><table><thead><tr><th>Component</th><th>Metric</th><th>Value</th></tr></thead><tbody>{metric_rows}</tbody></table></section>
<section><h2>Assumptions</h2><table><thead><tr><th>ID</th><th>Statement</th><th>Confidence</th><th>Status</th></tr></thead><tbody>{assumption_rows}</tbody></table></section>
<section><h2>Risks</h2><table><thead><tr><th>ID</th><th>Statement</th><th>Severity</th><th>Status</th></tr></thead><tbody>{risk_rows}</tbody></table></section>
<section><h2>Component errors</h2><ul>{error_html}</ul></section>
<section><h2>Provenance</h2><pre>{esc(json.dumps(summary['provenance'], indent=2))}</pre></section>
</main></body></html>"""


def write_evidence(summary: dict[str, Any], config: dict[str, Any]) -> None:
    evidence_root = ROOT / config.get("pipeline", {}).get("evidence_root", "evidence")
    run_dir = evidence_root / "runs" / summary["run_id"]
    latest_dir = evidence_root / "latest"
    publish_dir = ROOT / config.get("pipeline", {}).get("publish_report_to", "docs/evidence")

    for directory in (run_dir, latest_dir, publish_dir):
        directory.mkdir(parents=True, exist_ok=True)

    summary_json = json.dumps(summary, indent=2) + "\n"
    report_html = make_report(summary)

    for directory in (run_dir, latest_dir):
        (directory / "summary.json").write_text(summary_json, encoding="utf-8")
        (directory / "report.html").write_text(report_html, encoding="utf-8")

    (publish_dir / "summary.json").write_text(summary_json, encoding="utf-8")
    (publish_dir / "index.html").write_text(report_html, encoding="utf-8")


def execute(
    run_id: str | None = None,
    source_ref: str | None = None,
    source_commit: str | None = None,
) -> dict[str, Any]:
    config = load_yaml(ROOT / "prototype.yaml")
    requirements_doc = load_yaml(ROOT / "requirements" / "requirements.yaml")
    assumptions_doc = load_yaml(ROOT / "assumptions" / "assumptions.yaml")
    risks_doc = load_yaml(ROOT / "risks" / "risks.yaml")

    now = dt.datetime.now(dt.timezone.utc)
    run_id = run_id or f"RUN-{now.strftime('%Y%m%dT%H%M%SZ')}"

    metrics: dict[str, dict[str, Any]] = {}
    component_errors: list[dict[str, str]] = []

    for component in config.get("components", []):
        component_id = component["id"]
        try:
            metrics[component_id] = run_component(component)
        except Exception as exc:
            component_errors.append(
                {
                    "component": component_id,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )

    results = requirement_results(requirements_doc.get("requirements", []), metrics)
    status = overall_status(results, component_errors)
    counts = {
        "total": len(results),
        "pass": sum(r["status"] == "PASS" for r in results),
        "fail": sum(r["status"] == "FAIL" for r in results),
        "unknown": sum(r["status"] == "UNKNOWN" for r in results),
    }

    summary = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at_utc": now.isoformat(),
        "status": status,
        "project": config.get("project", {}),
        "counts": counts,
        "metrics": metrics,
        "requirements": results,
        "assumptions": assumptions_doc.get("assumptions", []),
        "risks": risks_doc.get("risks", []),
        "component_errors": component_errors,
        "provenance": {
            "executor": "chatgpt_tool_environment",
            "source_ref": source_ref or git_value("branch", "--show-current"),
            "source_commit": source_commit or git_value("rev-parse", "HEAD"),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
    }

    write_evidence(summary, config)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ad-hoc prototype evidence pipeline.")
    parser.add_argument("--run-id")
    parser.add_argument("--source-ref")
    parser.add_argument("--source-commit")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = execute(
        run_id=args.run_id,
        source_ref=args.source_ref,
        source_commit=args.source_commit,
    )

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"{summary['run_id']}: {summary['status']} "
            f"({summary['counts']['pass']} pass, "
            f"{summary['counts']['fail']} fail, "
            f"{summary['counts']['unknown']} unknown)"
        )

    if summary["status"] == "PASS":
        return 0
    if summary["status"] == "UNKNOWN":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
