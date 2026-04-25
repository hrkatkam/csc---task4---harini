from __future__ import annotations

from dataclasses import dataclass

from .instruction import FUNCT_AND, FUNCT_AND_INVERT_RS, FUNCT_OR, Instruction, OPCODE_RTYPE


@dataclass(frozen=True)
class ControlSignals:
    alu_op: str
    invert_input_a: bool
    invert_input_b: bool
    reg_write_enable: bool
    writeback_source: str
    inversion_source: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "alu_op": self.alu_op,
            "invert_input_a": self.invert_input_a,
            "invert_input_b": self.invert_input_b,
            "reg_write_enable": self.reg_write_enable,
            "writeback_source": self.writeback_source,
            "inversion_source": self.inversion_source,
        }


class ControlUnit:
    def decode(self, instruction: Instruction) -> ControlSignals:
        if instruction.opcode != OPCODE_RTYPE:
            raise ValueError(f"Unsupported opcode: {instruction.opcode}")

        if instruction.funct == FUNCT_AND:
            return ControlSignals(
                alu_op="AND",
                invert_input_a=False,
                invert_input_b=False,
                reg_write_enable=True,
                writeback_source="alu",
                inversion_source="function_field",
            )

        if instruction.funct == FUNCT_AND_INVERT_RS:
            return ControlSignals(
                alu_op="AND",
                invert_input_a=True,
                invert_input_b=False,
                reg_write_enable=True,
                writeback_source="alu",
                inversion_source="function_field",
            )

        if instruction.funct == FUNCT_OR:
            return ControlSignals(
                alu_op="OR",
                invert_input_a=False,
                invert_input_b=False,
                reg_write_enable=True,
                writeback_source="alu",
                inversion_source="function_field",
            )

        raise ValueError(f"Unsupported function code: {instruction.funct}")
