from __future__ import annotations

import unittest

from processor.processor import SingleCycleProcessor


class ProgramExecutionTests(unittest.TestCase):
    def test_required_program_matches_expression(self) -> None:
        processor = SingleCycleProcessor()
        result = processor.run(a_value=10, b_value=12, c_value=9, d_value=12)

        expected_t4 = 10 & 12
        expected_t6 = ((~9) & 0xFFFFFFFF) & 12
        expected_t0 = expected_t4 | expected_t6

        self.assertEqual(result.intermediate_registers["t4"], expected_t4)
        self.assertEqual(result.intermediate_registers["t6"], expected_t6)
        self.assertEqual(result.intermediate_registers["t0"], expected_t0)
        self.assertEqual(result.final_output, expected_t0)
        self.assertTrue(result.output_matches_expected)

    def test_program_has_three_instruction_trace_entries(self) -> None:
        processor = SingleCycleProcessor()
        result = processor.run(a_value=1, b_value=1, c_value=0, d_value=1)
        self.assertEqual(len(result.trace), 3)
        for index, entry in enumerate(result.trace):
            self.assertEqual(entry.program_counter, index)
            self.assertIn("single cycle", entry.stage_model.lower())


if __name__ == "__main__":
    unittest.main()
