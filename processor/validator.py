from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path

from .instruction import Instruction, register_name
from .register_file import RegisterFile


@dataclass(frozen=True)
class ValidationItem:
    key: str
    description: str
    passed: bool
    points: int
    evidence: str
    manual: bool = False

    def to_dict(self) -> dict[str, str | bool | int]:
        return {
            "key": self.key,
            "description": self.description,
            "passed": self.passed,
            "points": self.points,
            "evidence": self.evidence,
            "manual": self.manual,
        }


@dataclass(frozen=True)
class ValidationReport:
    items: list[ValidationItem]

    @property
    def earned_points(self) -> int:
        return sum(item.points for item in self.items if item.passed)

    @property
    def total_points(self) -> int:
        return sum(item.points for item in self.items)

    @property
    def passed_count(self) -> int:
        return sum(1 for item in self.items if item.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for item in self.items if not item.passed)

    @property
    def all_items_passed(self) -> bool:
        return all(item.passed for item in self.items)

    def to_dict(self) -> dict[str, object]:
        return {
            "earned_points": self.earned_points,
            "total_points": self.total_points,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "all_items_passed": self.all_items_passed,
            "items": [item.to_dict() for item in self.items],
        }


class AssignmentValidator:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def _required_component_files(self) -> list[Path]:
        return [
            self.project_root / "processor" / "register_file.py",
            self.project_root / "processor" / "alu.py",
            self.project_root / "processor" / "mux.py",
            self.project_root / "processor" / "instruction_input.py",
            self.project_root / "processor" / "control_unit.py",
            self.project_root / "processor" / "datapath.py",
        ]

    def _required_modular_files(self) -> list[Path]:
        return [
            self.project_root / "processor" / "instruction.py",
            self.project_root / "processor" / "assembler.py",
            self.project_root / "processor" / "processor.py",
            self.project_root / "main.py",
        ]

    def validate(
        self,
        run_result,
        github_submitted: bool,
        demo_video_complete: bool,
    ) -> ValidationReport:
        program: list[Instruction] = run_result.program_instructions
        trace = run_result.trace

        and_instructions = [instruction for instruction in program if instruction.operation == "AND"]
        or_instructions = [instruction for instruction in program if instruction.operation == "OR"]

        has_and = len(and_instructions) >= 1
        has_or = len(or_instructions) >= 1
        has_inversion_signal = any(
            entry.control_signals.get("invert_input_a", False) for entry in trace
        )

        not_instruction_present = any(
            "not" in entry.instruction_text.split(" ", 1)[0].lower() for entry in trace
        )

        standard_and = next((inst for inst in and_instructions if not inst.invert_input_a), None)
        invert_and = next((inst for inst in and_instructions if inst.invert_input_a), None)

        inversion_in_function_field = (
            standard_and is not None
            and invert_and is not None
            and standard_and.opcode == invert_and.opcode
            and standard_and.funct != invert_and.funct
        )

        component_files = self._required_component_files()
        separate_component_files = all(path.exists() for path in component_files)

        read_signature = inspect.signature(RegisterFile.read)
        write_signature = inspect.signature(RegisterFile.write)
        register_file_ports_ok = (
            len(read_signature.parameters) == 3
            and len(write_signature.parameters) >= 4
            and "enable" in write_signature.parameters
        )

        required_signal_keys = {"alu_op", "invert_input_a", "reg_write_enable"}
        control_signal_schema_ok = all(
            required_signal_keys.issubset(set(entry.control_signals.keys())) for entry in trace
        )

        and_mode_variants = {
            entry.control_signals.get("invert_input_a")
            for entry in trace
            if entry.control_signals.get("alu_op") == "AND"
        }
        differentiated_and_behaviors = and_mode_variants == {False, True}

        single_cycle_model_ok = len(trace) == len(program) and all(
            entry.stage_model == "Fetch -> Decode -> Execute -> Write-back (single cycle)"
            for entry in trace
        )

        observed_sequence = [
            (
                instruction.operation,
                register_name(instruction.rd),
                register_name(instruction.rs),
                register_name(instruction.rt),
                instruction.invert_input_a,
            )
            for instruction in program
        ]
        required_sequence_ok = (
            len(observed_sequence) == 3
            and observed_sequence[0] == ("AND", "t4", "t0", "t1", False)
            and observed_sequence[1][0] == "AND"
            and observed_sequence[1][1] == "t6"
            and observed_sequence[1][3] == "t3"
            and observed_sequence[1][4] is True
            and observed_sequence[1][2] in {"t2", "t5"}
            and observed_sequence[2] == ("OR", "t0", "t4", "t6", False)
        )

        expected_t4 = run_result.inputs["A"] & run_result.inputs["B"]
        expected_t6 = ((~run_result.inputs["C"]) & 0xFFFFFFFF) & run_result.inputs["D"]
        expected_t0 = expected_t4 | expected_t6
        intermediate_ok = (
            run_result.intermediate_registers["t4"] == expected_t4
            and run_result.intermediate_registers["t6"] == expected_t6
            and run_result.intermediate_registers["t0"] == expected_t0
        )

        final_output_ok = run_result.output_matches_expected

        trace_complete = len(trace) == 3 and all(
            entry.control_signals
            and entry.registers_after
            and entry.write_back
            and entry.alu_details
            for entry in trace
        )

        readme_file = self.project_root / "README.md"
        readme_present = False
        readme_contains_video_answer = False
        if readme_file.exists():
            readme_text = readme_file.read_text(encoding="utf-8")
            readme_present = True
            readme_contains_video_answer = (
                "Can video recordings be uploaded to YouTube? Yes." in readme_text
            )

        modular_files_ok = all(path.exists() for path in self._required_modular_files())

        items = [
            ValidationItem(
                key="instruction_and_supported",
                description="Processor supports AND instruction.",
                passed=has_and,
                points=5,
                evidence=f"AND instruction count in program: {len(and_instructions)}",
            ),
            ValidationItem(
                key="instruction_or_supported",
                description="Processor supports OR instruction.",
                passed=has_or,
                points=5,
                evidence=f"OR instruction count in program: {len(or_instructions)}",
            ),
            ValidationItem(
                key="not_via_alu_inversion",
                description="NOT behavior is provided via ALU input inversion control signal.",
                passed=has_inversion_signal,
                points=7,
                evidence=(
                    "At least one instruction had invert_input_a=true in control signals."
                    if has_inversion_signal
                    else "No inversion signal observed."
                ),
            ),
            ValidationItem(
                key="no_not_instruction",
                description="No standalone NOT instruction is used.",
                passed=not not_instruction_present,
                points=4,
                evidence=(
                    "No instruction mnemonic starts with NOT."
                    if not not_instruction_present
                    else "Standalone NOT instruction detected."
                ),
            ),
            ValidationItem(
                key="inversion_in_function_field",
                description="Inversion behavior is encoded in function field, not opcode.",
                passed=inversion_in_function_field,
                points=6,
                evidence=(
                    f"Standard AND opcode/funct: {standard_and.opcode}/{standard_and.funct}; "
                    f"Inverted AND opcode/funct: {invert_and.opcode}/{invert_and.funct}"
                    if inversion_in_function_field
                    else "Could not verify opcode/function separation for inversion behavior."
                ),
            ),
            ValidationItem(
                key="separate_datapath_files",
                description="Datapath components are implemented in separate files.",
                passed=separate_component_files,
                points=9,
                evidence=(
                    "All required component files exist."
                    if separate_component_files
                    else "Missing one or more required datapath component files."
                ),
            ),
            ValidationItem(
                key="register_file_2r1w",
                description="Register file supports two reads and one write.",
                passed=register_file_ports_ok,
                points=6,
                evidence=(
                    f"RegisterFile.read signature: {read_signature}; "
                    f"RegisterFile.write signature: {write_signature}"
                ),
            ),
            ValidationItem(
                key="control_signal_schema",
                description="Control unit emits ALU op, inversion flag, and register write enable.",
                passed=control_signal_schema_ok,
                points=7,
                evidence=(
                    "Required control signal keys are present in every trace entry."
                    if control_signal_schema_ok
                    else "One or more trace entries are missing required control signals."
                ),
            ),
            ValidationItem(
                key="and_mode_differentiation",
                description="Control logic differentiates standard AND and AND-with-inversion.",
                passed=differentiated_and_behaviors,
                points=6,
                evidence=f"Observed AND inversion modes: {sorted(and_mode_variants)}",
            ),
            ValidationItem(
                key="single_cycle_execution",
                description="Execution model is single-cycle per instruction.",
                passed=single_cycle_model_ok,
                points=7,
                evidence=(
                    f"Trace length={len(trace)}, program length={len(program)}, "
                    "stage model consistent across trace entries."
                ),
            ),
            ValidationItem(
                key="required_program_sequence",
                description="Required program sequence for t4, t6, t0 is executed.",
                passed=required_sequence_ok,
                points=6,
                evidence=f"Observed instruction sequence: {observed_sequence}",
            ),
            ValidationItem(
                key="intermediate_register_values",
                description="Intermediate registers match expected values.",
                passed=intermediate_ok,
                points=9,
                evidence=(
                    f"Expected t4={expected_t4}, t6={expected_t6}, t0={expected_t0}; "
                    f"Observed {run_result.intermediate_registers}"
                ),
            ),
            ValidationItem(
                key="final_output_value",
                description="Final output matches Y = A*B + C'*D bitwise expression.",
                passed=final_output_ok,
                points=9,
                evidence=(
                    f"Expected {run_result.expected_output}, observed {run_result.final_output}"
                ),
            ),
            ValidationItem(
                key="trace_and_register_outputs",
                description="Trace includes instruction execution, control signals, and register snapshots.",
                passed=trace_complete,
                points=5,
                evidence=(
                    "Three complete trace entries were produced with control and register data."
                    if trace_complete
                    else "Trace entries are incomplete."
                ),
            ),
            ValidationItem(
                key="readme_and_video_answer",
                description=(
                    "README exists with run instructions and includes the YouTube upload answer."
                ),
                passed=readme_present and readme_contains_video_answer,
                points=4,
                evidence=(
                    "README present and contains: 'Can video recordings be uploaded to YouTube? Yes.'"
                    if readme_present and readme_contains_video_answer
                    else "README missing or missing YouTube answer line."
                ),
            ),
            ValidationItem(
                key="modular_source_layout",
                description="Source code is modular and organized by datapath stage/files.",
                passed=modular_files_ok,
                points=3,
                evidence=(
                    "All required modular source files are present."
                    if modular_files_ok
                    else "One or more modular source files are missing."
                ),
            ),
            ValidationItem(
                key="github_submission",
                description="Code has been submitted to GitHub.",
                passed=github_submitted,
                points=1,
                evidence=(
                    "Marked complete via CLI flag --github-submitted."
                    if github_submitted
                    else "Manual deliverable pending. Run with --github-submitted after pushing."
                ),
                manual=True,
            ),
            ValidationItem(
                key="demo_video_submission",
                description="4-5 minute demo video has been recorded and submitted.",
                passed=demo_video_complete,
                points=1,
                evidence=(
                    "Marked complete via CLI flag --demo-video-complete."
                    if demo_video_complete
                    else (
                        "Manual deliverable pending. Run with --demo-video-complete after recording/upload."
                    )
                ),
                manual=True,
            ),
        ]

        return ValidationReport(items=items)
