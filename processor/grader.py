from __future__ import annotations

from dataclasses import dataclass

from .validator import ValidationReport


@dataclass(frozen=True)
class GradeReport:
    earned_points: int
    total_points: int
    percentage: float
    letter_grade: str
    failed_requirements: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "earned_points": self.earned_points,
            "total_points": self.total_points,
            "percentage": self.percentage,
            "letter_grade": self.letter_grade,
            "failed_requirements": self.failed_requirements,
        }



def _letter_grade(percent: float) -> str:
    if percent >= 97:
        return "A+"
    if percent >= 93:
        return "A"
    if percent >= 90:
        return "A-"
    if percent >= 87:
        return "B+"
    if percent >= 83:
        return "B"
    if percent >= 80:
        return "B-"
    if percent >= 77:
        return "C+"
    if percent >= 73:
        return "C"
    if percent >= 70:
        return "C-"
    if percent >= 60:
        return "D"
    return "F"



def grade_assignment(report: ValidationReport) -> GradeReport:
    total_points = report.total_points
    earned_points = report.earned_points
    percentage = round((earned_points / total_points) * 100, 2) if total_points else 0.0

    failed_requirements = [
        f"{item.key}: {item.description}"
        for item in report.items
        if not item.passed
    ]

    return GradeReport(
        earned_points=earned_points,
        total_points=total_points,
        percentage=percentage,
        letter_grade=_letter_grade(percentage),
        failed_requirements=failed_requirements,
    )
