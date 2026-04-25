from __future__ import annotations

import re

from .constants import REQUIRED_PROGRAM_TEXT
from .instruction import Instruction, register_index


def assemble_line(line: str) -> Instruction:
    without_comment = re.split(r"[;#]", line, maxsplit=1)[0].strip()
    if not without_comment:
        raise ValueError("Instruction line is empty")

    tokens = [token for token in re.split(r"[\s,]+", without_comment) if token]
    if len(tokens) < 4:
        raise ValueError(f"Malformed instruction: {line}")

    mnemonic = tokens[0].lower()
    rd = register_index(tokens[1])
    rs = register_index(tokens[2])
    rt = register_index(tokens[3])

    invert_rs = mnemonic in {"andn", "orn"}
    if len(tokens) >= 5 and tokens[4].lower() in {"inv", "invert", "invert_rs"}:
        invert_rs = True

    if mnemonic in {"and", "andn"}:
        return Instruction.and_(rd=rd, rs=rs, rt=rt, invert_rs=invert_rs)

    if mnemonic in {"or", "orn"}:
        if invert_rs:
            raise ValueError("OR inversion is not used in this assignment")
        return Instruction.or_(rd=rd, rs=rs, rt=rt)

    raise ValueError(f"Unsupported instruction mnemonic: {mnemonic}")



def build_required_program() -> list[Instruction]:
    return [
        Instruction.and_(
            rd=register_index("t4"),
            rs=register_index("t0"),
            rt=register_index("t1"),
            invert_rs=False,
        ),
        Instruction.and_(
            rd=register_index("t6"),
            rs=register_index("t2"),
            rt=register_index("t3"),
            invert_rs=True,
        ),
        Instruction.or_(
            rd=register_index("t0"),
            rs=register_index("t4"),
            rt=register_index("t6"),
        ),
    ]



def required_program_listing() -> list[str]:
    return list(REQUIRED_PROGRAM_TEXT)
