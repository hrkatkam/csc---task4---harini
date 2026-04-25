from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .alu import ALU
from .constants import hex32
from .control_unit import ControlUnit
from .instruction import Instruction, register_name
from .mux import mux2
from .register_file import RegisterFile


@dataclass(frozen=True)
class TraceEntry:
    cycle: int
    program_counter: int
    stage_model: str
    instruction_text: str
    instruction_word_hex: str
    opcode: int
    funct: int
    control_signals: dict[str, Any]
    register_reads: dict[str, Any]
    alu_details: dict[str, Any]
    write_back: dict[str, Any]
    registers_after: dict[str, int]


class SingleCycleDatapath:
    def __init__(
        self,
        register_file: RegisterFile,
        control_unit: ControlUnit,
        alu: ALU,
    ) -> None:
        self.register_file = register_file
        self.control_unit = control_unit
        self.alu = alu

    def execute_instruction(
        self,
        instruction: Instruction,
        cycle: int,
        program_counter: int,
    ) -> TraceEntry:
        rs_value, rt_value = self.register_file.read(instruction.rs, instruction.rt)
        signals = self.control_unit.decode(instruction)
        alu_result = self.alu.execute(
            input_a=rs_value,
            input_b=rt_value,
            alu_op=signals.alu_op,
            invert_input_a=signals.invert_input_a,
            invert_input_b=signals.invert_input_b,
        )

        writeback_value = mux2(
            signals.writeback_source == "alu",
            0,
            alu_result.result,
        )

        self.register_file.write(
            rd_index=instruction.rd,
            value=writeback_value,
            enable=signals.reg_write_enable,
        )

        return TraceEntry(
            cycle=cycle,
            program_counter=program_counter,
            stage_model="Fetch -> Decode -> Execute -> Write-back (single cycle)",
            instruction_text=instruction.format_assembly(),
            instruction_word_hex=hex32(instruction.encode()),
            opcode=instruction.opcode,
            funct=instruction.funct,
            control_signals=signals.to_dict(),
            register_reads={
                "rs_register": register_name(instruction.rs),
                "rt_register": register_name(instruction.rt),
                "rs_value": rs_value,
                "rt_value": rt_value,
            },
            alu_details={
                "operation": alu_result.operation,
                "raw_input_a": alu_result.raw_input_a,
                "raw_input_b": alu_result.raw_input_b,
                "effective_input_a": alu_result.effective_input_a,
                "effective_input_b": alu_result.effective_input_b,
                "result": alu_result.result,
            },
            write_back={
                "destination_register": register_name(instruction.rd),
                "enabled": signals.reg_write_enable,
                "value": writeback_value,
            },
            registers_after=self.register_file.snapshot(),
        )
