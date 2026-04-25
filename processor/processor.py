from __future__ import annotations

from dataclasses import dataclass

from .alu import ALU
from .assembler import build_required_program, required_program_listing
from .constants import AUTHOR, REGISTER_ALIASES, mask32
from .control_unit import ControlUnit
from .datapath import SingleCycleDatapath, TraceEntry
from .instruction import Instruction
from .instruction_input import InstructionInput
from .register_file import RegisterFile


@dataclass(frozen=True)
class ProcessorRunResult:
    author: str
    inputs: dict[str, int]
    program_listing: list[str]
    program_instructions: list[Instruction]
    trace: list[TraceEntry]
    intermediate_registers: dict[str, int]
    final_registers: dict[str, int]
    final_output: int
    expected_output: int
    output_matches_expected: bool


class SingleCycleProcessor:
    def __init__(self, author: str = AUTHOR) -> None:
        self.author = author

    @staticmethod
    def compute_expected_output(a_value: int, b_value: int, c_value: int, d_value: int) -> int:
        return mask32((a_value & b_value) | (mask32(~c_value) & d_value))

    def run(self, a_value: int, b_value: int, c_value: int, d_value: int) -> ProcessorRunResult:
        register_file = RegisterFile(register_count=8)
        register_file.load_inputs(
            a_value=a_value,
            b_value=b_value,
            c_value=c_value,
            d_value=d_value,
        )

        program = build_required_program()
        instruction_input = InstructionInput(program)
        datapath = SingleCycleDatapath(
            register_file=register_file,
            control_unit=ControlUnit(),
            alu=ALU(),
        )

        trace_entries: list[TraceEntry] = []
        cycle = 1
        program_counter = 0

        while True:
            instruction = instruction_input.fetch(program_counter)
            if instruction is None:
                break

            trace_entries.append(
                datapath.execute_instruction(
                    instruction=instruction,
                    cycle=cycle,
                    program_counter=program_counter,
                )
            )

            cycle += 1
            program_counter += 1

        final_registers = register_file.snapshot()
        intermediate_registers = {
            "t4": final_registers["t4"],
            "t6": final_registers["t6"],
            "t0": final_registers["t0"],
        }

        expected_output = self.compute_expected_output(
            a_value=a_value,
            b_value=b_value,
            c_value=c_value,
            d_value=d_value,
        )

        return ProcessorRunResult(
            author=self.author,
            inputs={
                "A": mask32(a_value),
                "B": mask32(b_value),
                "C": mask32(c_value),
                "D": mask32(d_value),
            },
            program_listing=required_program_listing(),
            program_instructions=program,
            trace=trace_entries,
            intermediate_registers=intermediate_registers,
            final_registers=final_registers,
            final_output=final_registers["t0"],
            expected_output=expected_output,
            output_matches_expected=final_registers["t0"] == expected_output,
        )
