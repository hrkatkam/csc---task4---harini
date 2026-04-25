from __future__ import annotations

import argparse
import json
from pathlib import Path

from processor.constants import AUTHOR
from processor.grader import grade_assignment
from processor.processor import SingleCycleProcessor
from processor.trace import build_json_report, render_console_report
from processor.validator import AssignmentValidator



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Single-cycle processor simulator for Task4: "
            "Y = A*B + C'*D using AND/OR and ALU input inversion."
        )
    )
    parser.add_argument("--A", type=int, default=10, help="Input register A value")
    parser.add_argument("--B", type=int, default=12, help="Input register B value")
    parser.add_argument("--C", type=int, default=9, help="Input register C value")
    parser.add_argument("--D", type=int, default=12, help="Input register D value")
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("harini_processor_report.json"),
        help="Output path for JSON execution and validation report",
    )
    parser.add_argument(
        "--github-submitted",
        action="store_true",
        help="Mark GitHub submission deliverable as complete",
    )
    parser.add_argument(
        "--demo-video-complete",
        action="store_true",
        help="Mark demo video deliverable as complete",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero exit code when any validation item fails",
    )
    return parser.parse_args()



def main() -> int:
    args = parse_args()

    processor = SingleCycleProcessor(author=AUTHOR)
    run_result = processor.run(
        a_value=args.A,
        b_value=args.B,
        c_value=args.C,
        d_value=args.D,
    )

    validator = AssignmentValidator(project_root=Path(__file__).resolve().parent)
    validation_report = validator.validate(
        run_result=run_result,
        github_submitted=args.github_submitted,
        demo_video_complete=args.demo_video_complete,
    )
    grade_report = grade_assignment(validation_report)

    console_report = render_console_report(
        run_result=run_result,
        validation_report=validation_report,
        grade_report=grade_report,
    )
    print(console_report)

    json_report = build_json_report(
        run_result=run_result,
        validation_report=validation_report,
        grade_report=grade_report,
    )
    args.json_output.write_text(json.dumps(json_report, indent=2), encoding="utf-8")
    print(f"\nJSON report written to: {args.json_output}")

    if args.strict and not validation_report.all_items_passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
