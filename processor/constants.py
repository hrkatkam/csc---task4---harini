from __future__ import annotations

WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1
AUTHOR = "Harini Reddy Katkam"

REGISTER_ALIASES = {
    "t0": 0,
    "t1": 1,
    "t2": 2,
    "t3": 3,
    "t4": 4,
    "t5": 5,
    "t6": 6,
    "t7": 7,
}

REGISTER_NAMES = {index: alias for alias, index in REGISTER_ALIASES.items()}

REQUIRED_PROGRAM_TEXT = [
    "and t4, t0, t1 ; t4 = A & B",
    "and t6, t2, t3 ; t6 = (~C) & D via ALU input inversion control",
    "or t0, t4, t6 ; t0 = t4 | t6",
]


def mask32(value: int) -> int:
    return value & WORD_MASK


def hex32(value: int) -> str:
    return f"0x{mask32(value):08X}"
