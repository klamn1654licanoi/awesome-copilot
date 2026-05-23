#!/usr/bin/env python3
"""Generate a summary report of instruction file validation results."""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from validate_instructions import validate_all


def build_report(root: Path) -> dict:
    """Build a structured validation report for all instruction files."""
    results = validate_all(root)
    files_ok = []
    files_with_errors = []

    for path, errors in results.items():
        entry = {"path": path, "errors": errors}
        if errors:
            files_with_errors.append(entry)
        else:
            files_ok.append(entry)

    total_errors = sum(len(e["errors"]) for e in files_with_errors)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_files": len(results),
            "files_passing": len(files_ok),
            "files_failing": len(files_with_errors),
            "total_errors": total_errors,
        },
        "passing": files_ok,
        "failing": files_with_errors,
    }


def print_report(report: dict, fmt: str = "text") -> None:
    """Print the report in the requested format."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return

    summary = report["summary"]
    print(f"Instruction File Validation Report")
    print(f"Generated: {report['generated_at']}")
    print(f"{'=' * 40}")
    print(f"Total files : {summary['total_files']}")
    print(f"Passing     : {summary['files_passing']}")
    print(f"Failing     : {summary['files_failing']}")
    print(f"Total errors: {summary['total_errors']}")

    if report["failing"]:
        print("\nFailing files:")
        for entry in report["failing"]:
            print(f"  {entry['path']}")
            for err in entry["errors"]:
                print(f"    - {err}")


def main() -> int:
    fmt = "json" if "--json" in sys.argv else "text"
    root = Path(".")
    report = build_report(root)
    print_report(report, fmt=fmt)
    return 0 if report["summary"]["total_errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
