# Processor Design Task4 App

Author: Harini Reddy Katkam

This project implements a modular single-cycle 32-bit processor simulator for the required computation:

Y = A*B + C'*D

Bitwise form used by the simulator:

Y = (A & B) | ((~C) & D)

## What This Implementation Guarantees

- Supports AND and OR instructions.
- Implements NOT behavior through ALU input inversion control signal.
- Does not implement NOT as a standalone instruction.
- Encodes inversion behavior in the function field, not opcode.
- Uses a single-cycle model per instruction:
  Fetch -> Decode -> Execute -> Write-back.
- Produces required outputs:
  instruction trace, control signals, register state after each instruction, intermediate values, and final Y.
- Includes automated requirement validation and assignment grading out of 100.

## Modular Datapath Files

- `processor/register_file.py`
- `processor/alu.py`
- `processor/mux.py`
- `processor/instruction_input.py`
- `processor/control_unit.py`
- `processor/datapath.py`

Additional modules:

- `processor/instruction.py`
- `processor/assembler.py`
- `processor/processor.py`
- `processor/validator.py`
- `processor/grader.py`
- `processor/trace.py`
- `main.py`

## Run

From the `Harini` folder:

```bash
python3 main.py
```

Custom input run:

```bash
python3 main.py --A 5 --B 3 --C 2 --D 4
```

Generate full-credit validation output (use after external deliverables are complete):

```bash
python3 main.py --github-submitted --demo-video-complete --strict --json-output harini_processor_report.json
```

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Professor Verification Steps

1. Run `python3 main.py`.
2. Confirm trace contains three instructions with single-cycle stage model.
3. Confirm control signals show AND, inverted AND, and OR behavior.
4. Confirm intermediate values are printed:
   - `t4 = A & B`
   - `t6 = (~C) & D`
   - `t0 = t4 | t6`
5. Confirm final output equals `Y = A*B + C'*D`.
6. Run strict full-credit command after submission/video completion to confirm `100/100`.

## Assignment Note

The assignment line `and t6, t5, t3` conflicts with the stated mapping `t2=C`. This implementation follows the declared mapping (`t2=C`) so the required expression is computed correctly.

Can video recordings be uploaded to YouTube? Yes.
