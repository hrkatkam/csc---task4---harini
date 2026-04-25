from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .constants import hex32



def _value(value: int) -> str:
    return f"{hex32(value)} ({value})"



def render_console_report(run_result, validation_report=None, grade_report=None) -> str:
    lines: list[str] = []

    lines.append("Processor Design Task4 Report")
    lines.append(f"Author: {run_result.author}")
    lines.append("Expression: Y = A*B + C'*D  (bitwise: (A & B) | ((~C) & D))")
    lines.append("")

    lines.append("Input Values")
    for key in ["A", "B", "C", "D"]:
        lines.append(f"  {key}: {_value(run_result.inputs[key])}")
    lines.append("")

    lines.append("Program Listing")
    for index, line in enumerate(run_result.program_listing, start=1):
        lines.append(f"  {index}. {line}")
    lines.append("")

    lines.append("Instruction Execution Trace")
    for entry in run_result.trace:
        lines.append(
            f"  Cycle {entry.cycle} | PC {entry.program_counter} | {entry.instruction_text}"
        )
        lines.append(f"    Stage model: {entry.stage_model}")
        lines.append(
            "    Control: "
            f"alu_op={entry.control_signals['alu_op']}, "
            f"invert_input_a={entry.control_signals['invert_input_a']}, "
            f"reg_write_enable={entry.control_signals['reg_write_enable']}"
        )
        lines.append(
            "    Reads: "
            f"{entry.register_reads['rs_register']}={_value(entry.register_reads['rs_value'])}, "
            f"{entry.register_reads['rt_register']}={_value(entry.register_reads['rt_value'])}"
        )
        lines.append(
            "    ALU: "
            f"effective_a={_value(entry.alu_details['effective_input_a'])}, "
            f"effective_b={_value(entry.alu_details['effective_input_b'])}, "
            f"result={_value(entry.alu_details['result'])}"
        )
        lines.append(
            "    Write-back: "
            f"{entry.write_back['destination_register']} <- {_value(entry.write_back['value'])}"
        )
        register_state = ", ".join(
            f"{register}={_value(value)}"
            for register, value in entry.registers_after.items()
        )
        lines.append(f"    Registers: {register_state}")
    lines.append("")

    lines.append("Intermediate Registers")
    lines.append(f"  t4 = {_value(run_result.intermediate_registers['t4'])}")
    lines.append(f"  t6 = {_value(run_result.intermediate_registers['t6'])}")
    lines.append(f"  t0 = {_value(run_result.intermediate_registers['t0'])}")
    lines.append("")

    lines.append("Final Output")
    lines.append(f"  Expected Y: {_value(run_result.expected_output)}")
    lines.append(f"  Observed Y: {_value(run_result.final_output)}")
    lines.append(f"  Match: {run_result.output_matches_expected}")

    if validation_report is not None:
        lines.append("")
        lines.append("Validation Checklist")
        for item in validation_report.items:
            status = "PASS" if item.passed else "FAIL"
            lines.append(f"  [{status}] ({item.points} pts) {item.description}")
            lines.append(f"      Evidence: {item.evidence}")

    if grade_report is not None:
        lines.append("")
        lines.append("Assignment Grade")
        lines.append(
            f"  Score: {grade_report.earned_points}/{grade_report.total_points} "
            f"({grade_report.percentage}%)"
        )
        lines.append(f"  Letter: {grade_report.letter_grade}")

    return "\n".join(lines)



def build_json_report(run_result, validation_report=None, grade_report=None) -> dict[str, Any]:
    trace_data = [asdict(entry) for entry in run_result.trace]

    report: dict[str, Any] = {
        "assignment": "Processor Design Semester Project - Task4",
        "author": run_result.author,
        "inputs": run_result.inputs,
        "program_listing": run_result.program_listing,
        "trace": trace_data,
        "intermediate_registers": run_result.intermediate_registers,
        "final_registers": run_result.final_registers,
        "final_output": run_result.final_output,
        "expected_output": run_result.expected_output,
        "output_matches_expected": run_result.output_matches_expected,
    }

    if validation_report is not None:
        report["validation"] = validation_report.to_dict()
    if grade_report is not None:
        report["grade"] = grade_report.to_dict()

    return report
