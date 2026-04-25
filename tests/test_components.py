from __future__ import annotations

import unittest

from processor.alu import ALU
from processor.control_unit import ControlUnit
from processor.instruction import Instruction, register_index
from processor.register_file import RegisterFile


class ComponentTests(unittest.TestCase):
    def test_alu_and(self) -> None:
        alu = ALU()
        result = alu.execute(0b1010, 0b1100, "AND")
        self.assertEqual(result.result, 0b1000)

    def test_alu_and_with_invert_input(self) -> None:
        alu = ALU()
        c_value = 0b1001
        d_value = 0b1100
        result = alu.execute(c_value, d_value, "AND", invert_input_a=True)
        expected = ((~c_value) & 0xFFFFFFFF) & d_value
        self.assertEqual(result.result, expected)

    def test_control_unit_differentiates_and_modes(self) -> None:
        control = ControlUnit()
        standard = Instruction.and_(
            rd=register_index("t4"),
            rs=register_index("t0"),
            rt=register_index("t1"),
            invert_rs=False,
        )
        inverted = Instruction.and_(
            rd=register_index("t6"),
            rs=register_index("t2"),
            rt=register_index("t3"),
            invert_rs=True,
        )
        standard_signals = control.decode(standard)
        inverted_signals = control.decode(inverted)
        self.assertFalse(standard_signals.invert_input_a)
        self.assertTrue(inverted_signals.invert_input_a)

    def test_register_file_two_reads_one_write(self) -> None:
        registers = RegisterFile(register_count=8)
        registers.write(0, 11)
        registers.write(1, 7)
        a_value, b_value = registers.read(0, 1)
        self.assertEqual((a_value, b_value), (11, 7))


if __name__ == "__main__":
    unittest.main()
