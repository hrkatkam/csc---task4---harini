from __future__ import annotations

from typing import Sequence

from .instruction import Instruction


class InstructionInput:
    """Instruction source for fetch stage."""

    def __init__(self, instructions: Sequence[Instruction]) -> None:
        self._instructions = list(instructions)

    def fetch(self, program_counter: int) -> Instruction | None:
        if 0 <= program_counter < len(self._instructions):
            return self._instructions[program_counter]
        return None

    def __len__(self) -> int:
        return len(self._instructions)
