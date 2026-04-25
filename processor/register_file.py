from __future__ import annotations

from .constants import REGISTER_ALIASES, mask32


class RegisterFile:
    """Eight-register file with two read ports and one write port."""

    def __init__(self, register_count: int = 8) -> None:
        self.register_count = register_count
        self._registers = [0] * register_count

    def reset(self) -> None:
        self._registers = [0] * self.register_count

    def _validate_index(self, register_index: int) -> None:
        if not 0 <= register_index < self.register_count:
            raise IndexError(f"Register index out of range: {register_index}")

    def read(self, rs_index: int, rt_index: int) -> tuple[int, int]:
        self._validate_index(rs_index)
        self._validate_index(rt_index)
        return self._registers[rs_index], self._registers[rt_index]

    def write(self, rd_index: int, value: int, enable: bool = True) -> None:
        if not enable:
            return
        self._validate_index(rd_index)
        self._registers[rd_index] = mask32(value)

    def get_register(self, register_index: int) -> int:
        self._validate_index(register_index)
        return self._registers[register_index]

    def set_register(self, register_index: int, value: int) -> None:
        self._validate_index(register_index)
        self._registers[register_index] = mask32(value)

    def load_inputs(self, a_value: int, b_value: int, c_value: int, d_value: int) -> None:
        self.set_register(REGISTER_ALIASES["t0"], a_value)
        self.set_register(REGISTER_ALIASES["t1"], b_value)
        self.set_register(REGISTER_ALIASES["t2"], c_value)
        self.set_register(REGISTER_ALIASES["t3"], d_value)

    def snapshot(self) -> dict[str, int]:
        return {
            alias: self._registers[index]
            for alias, index in REGISTER_ALIASES.items()
            if index < self.register_count
        }
