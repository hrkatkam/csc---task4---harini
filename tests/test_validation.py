from __future__ import annotations

import unittest
from pathlib import Path

from processor.grader import grade_assignment
from processor.processor import SingleCycleProcessor
from processor.validator import AssignmentValidator


class ValidationTests(unittest.TestCase):
    def test_full_credit_when_manual_deliverables_marked_complete(self) -> None:
        processor = SingleCycleProcessor(author="Harini Reddy Katkam")
        run_result = processor.run(a_value=10, b_value=12, c_value=9, d_value=12)

        validator = AssignmentValidator(project_root=Path(__file__).resolve().parents[1])
        validation_report = validator.validate(
            run_result=run_result,
            github_submitted=True,
            demo_video_complete=True,
        )
        grade_report = grade_assignment(validation_report)

        self.assertTrue(validation_report.all_items_passed)
        self.assertEqual(grade_report.earned_points, 100)
        self.assertEqual(grade_report.total_points, 100)
        self.assertEqual(grade_report.percentage, 100.0)


if __name__ == "__main__":
    unittest.main()
