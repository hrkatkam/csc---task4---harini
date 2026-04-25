from __future__ import annotations

from dataclasses import dataclass

from .constants import mask32
from .mux import mux2


@dataclass(frozen=True)
class ALUResult:
    operation: str
    raw_input_a: int
    raw_input_b: int
    effective_input_a: int
    effective_input_b: int
    result: int


class ALU:
    def execute(
        self,
        input_a: int,
        input_b: int,
        alu_op: str,
        invert_input_a: bool = False,
        invert_input_b: bool = False,
    ) -> ALUResult:
        operation = alu_op.upper()
        if operation not in {"AND", "OR"}:
            raise ValueError(f"Unsupported ALU operation: {alu_op}")

        raw_a = mask32(input_a)
        raw_b = mask32(input_b)

        effective_a = mux2(invert_input_a, raw_a, mask32(~raw_a))
        effective_b = mux2(invert_input_b, raw_b, mask32(~raw_b))

        if operation == "AND":
            result = mask32(effective_a & effective_b)
        else:
            result = mask32(effective_a | effective_b)

        return ALUResult(
            operation=operation,
            raw_input_a=raw_a,
            raw_input_b=raw_b,
            effective_input_a=effective_a,
            effective_input_b=effective_b,
            result=result,
        )
