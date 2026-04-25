from __future__ import annotations

from dataclasses import dataclass

from .constants import REGISTER_ALIASES, REGISTER_NAMES

OPCODE_RTYPE = 0b000000

FUNCT_AND = 0b000001
FUNCT_AND_INVERT_RS = 0b000010
FUNCT_OR = 0b000011

_SUPPORTED_FUNCTS = {
    FUNCT_AND,
    FUNCT_AND_INVERT_RS,
    FUNCT_OR,
}


@dataclass(frozen=True)
class Instruction:
    opcode: int
    rs: int
    rt: int
    rd: int
    funct: int
    shamt: int = 0

    @property
    def operation(self) -> str:
        if self.funct in {FUNCT_AND, FUNCT_AND_INVERT_RS}:
            return "AND"
        if self.funct == FUNCT_OR:
            return "OR"
        raise ValueError(f"Unsupported function code: {self.funct}")

    @property
    def invert_input_a(self) -> bool:
        return self.funct == FUNCT_AND_INVERT_RS

    def encode(self) -> int:
        return (
            ((self.opcode & 0x3F) << 26)
            | ((self.rs & 0x1F) << 21)
            | ((self.rt & 0x1F) << 16)
            | ((self.rd & 0x1F) << 11)
            | ((self.shamt & 0x1F) << 6)
            | (self.funct & 0x3F)
        )

    def format_assembly(self) -> str:
        base = self.operation.lower()
        suffix = " ; invert rs input via control signal" if self.invert_input_a else ""
        return (
            f"{base} {register_name(self.rd)}, {register_name(self.rs)}, "
            f"{register_name(self.rt)}{suffix}"
        )

    def is_supported(self) -> bool:
        return self.opcode == OPCODE_RTYPE and self.funct in _SUPPORTED_FUNCTS

    @classmethod
    def and_(cls, rd: int, rs: int, rt: int, invert_rs: bool = False) -> "Instruction":
        funct = FUNCT_AND_INVERT_RS if invert_rs else FUNCT_AND
        return cls(opcode=OPCODE_RTYPE, rs=rs, rt=rt, rd=rd, funct=funct)

    @classmethod
    def or_(cls, rd: int, rs: int, rt: int) -> "Instruction":
        return cls(opcode=OPCODE_RTYPE, rs=rs, rt=rt, rd=rd, funct=FUNCT_OR)



def register_index(alias: str) -> int:
    cleaned = alias.strip().lower().rstrip(",")
    if cleaned not in REGISTER_ALIASES:
        raise ValueError(f"Unsupported register alias: {alias}")
    return REGISTER_ALIASES[cleaned]



def register_name(index: int) -> str:
    if index not in REGISTER_NAMES:
        return f"r{index}"
    return REGISTER_NAMES[index]
