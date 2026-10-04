[English](pubvm.md) | [Português](pubvm.pt_BR.md)

# PubVM — the machine

PubVM is the educational virtual machine built for PubLab. There is **one**
implementation; PubVM-8, PubVM-16 and PubVM-32 are that implementation with a
different `wordSize`. All three are implemented and validated: the conformance
suite in `tests/matrix_test.kf` runs over every variant returned by
`allMachines()`.

```kof
record MachineConfig(String name, Int wordSize, Int memorySize, Int addressBits, Int entryPoint)

MachineConfig pubvm8()  { return MachineConfig("PubVM-8",  8,  65536, 16, 0) }
MachineConfig pubvm16() { return MachineConfig("PubVM-16", 16, 65536, 16, 0) }
MachineConfig pubvm32() { return MachineConfig("PubVM-32", 32, 65536, 16, 0) }

List<MachineConfig> allMachines()   // the three, in order
```

Memory size and address size are **the same on all three**: only the word
changes. A wider word does not mean more memory — it means each value takes
more of the memory that is already there.

## Word

Values are carried internally in a 64-bit `Long` so that an unsigned 32-bit
word still fits exactly. Every write to a register goes through the word size:

| wordSize | range | mask |
|---|---|---|
| 8 | 0..255 | 0xFF |
| 16 | 0..65535 | 0xFFFF |
| 32 | 0..4294967295 | 0xFFFFFFFF |

Negative values are two's complement: on 8 bits, `-6` is stored as `250`, and
`250` read as signed is `-6`. `Word.kf` is the only place this is decided.

## Memory

```
MEMORY_SIZE  = 65536 bytes (64 KB)
ADDRESS_SIZE = 16 bits
```

Memory is **byte-addressable**: addresses 0x0000..0xFFFF each hold one byte. A
word occupies `wordSize / 8` consecutive bytes, stored **little-endian** (least
significant byte at the lowest address). On PubVM-8 a word is one byte; on
PubVM-16 the value 270 at address 8 is `0E` at 8 and `01` at 9.

An access outside memory is an error with a message, never a silent wrap.

## Registers

Basic Mode has four general registers, all of them word-sized:

| id | name |
|---|---|
| 0 | A |
| 1 | B |
| 2 | C |
| 3 | D |

`PC` is held by the machine itself, not by the register file: it is an
**address**, so it follows the address size (16 bits) and not the word size.

`X` and `Y` belong to Advanced Mode (phase 8, stage A) and **are
implemented**: two more word-sized general registers, ids 4 and 5, usable
anywhere A-D are.

`SP` and `FP` also belong to Advanced Mode. `SP` **is implemented**, but as
an address next to `PC`, not as a word-sized register (section "Stack"
below) — it has to hold `memorySize`, one past the top of memory, which does
not fit an 8-bit or 16-bit word. `FP` exists as the same kind of address
field, initialized to 0, but nothing reads or writes it yet: it is reserved
for `CALL`/`RET`/`ENTER`/`LEAVE`, a later stage. Neither is reachable as a
general operand register — the assembler rejects `SP`/`FP` the same way it
always rejected every Advanced Mode name, with `ASM014`.

## Stack

Advanced Mode, stage A: `PUSH` and `POP`.

```
SP initial = memorySize   (one past the top of memory — not a valid address)
wordBytes  = wordSize / 8
```

The stack grows toward **lower** addresses, from the top of memory down. One
core, one rule, for all three word sizes — there is no per-variant stack
logic.

`PUSH reg`:
```
SP = SP - wordBytes
MEM[SP] = reg
```
checked first: if `SP - wordBytes < 0`, the push has no room left and the
machine faults with `ERROR` ("stack overflow"), the same way an unknown
opcode or an out-of-range memory access does — never a silent wrap.

`POP reg`:
```
reg = MEM[SP]
SP = SP + wordBytes
```
checked first: if `SP >= memorySize`, nothing has been pushed and the machine
faults with `ERROR` ("stack underflow").

`PUSH` and `POP` touch no flag and no register other than their own operand.
`reset()` puts `SP` back at `memorySize` and `FP` back at 0, like every other
piece of state.

`CALL`, `RET`, `ENTER` and `LEAVE` will use this same stack; they are a later
stage of Advanced Mode, not yet implemented.

## Flags

| flag | meaning |
|---|---|
| C | carry out of the word on ADD; borrow on SUB |
| Z | the stored result is zero |
| N | the stored result has its sign bit set |
| O | signed (two's complement) overflow |

Flags are computed by the execution engine, together with the value, in
`Alu.kf`. Nothing else in the system computes a flag.

Exactly which instructions touch which flags:

| instruction | C | Z | N | O |
|---|---|---|---|---|
| `ADD`, `SUB` | set | set | set | set |
| `AND`, `OR`, `XOR`, `NOT` | cleared to 0 | set | set | cleared to 0 |
| `LOAD`, `STORE`, `JMP`, `JZ`, `JC`, `PRINT`, `HALT` | unchanged | unchanged | unchanged | unchanged |

### Z and N — identical for all six arithmetic and logic instructions

```
ADD / SUB / AND / OR / XOR / NOT:
    Z = stored result == 0
    N = sign bit of the stored result
```

Both are computed on the **stored** result — the value after truncation to the
word — never on the untruncated one. On PubVM-8, `255 + 1` stores `0`, so
`Z = 1` even though the true sum is 256.

### C — carry on ADD, borrow on SUB

The meaning of Carry in a subtraction differs between real architectures, so
PubVM fixes one simple, consistent definition:

```
ADD:  C = carry out
SUB:  C = borrow
```

- **C on ADD** is set when the true sum exceeds the word mask.
- **C on SUB** is set when the subtrahend is larger than the minuend, compared
  **unsigned** — the subtraction had to borrow.

```
10 - 3 = 7          C = 0
3 - 10 = 249        C = 1    (PubVM-8,  256 - 7)
3 - 10 = 65529      C = 1    (PubVM-16, 65536 - 7)
```

### O — signed overflow

- **O on ADD** is set when both operands have the same sign and the result's
  sign differs from it.
- **O on SUB** is set when the operands have different signs and the result's
  sign differs from the minuend's.

### C and O on the logic instructions

```
AND / OR / XOR / NOT:
    Z = result == 0
    N = sign bit of the result
    C = 0
    O = 0
```

There is no carry and no signed overflow in a bitwise operation, so both are
**cleared** rather than left alone — a program can rely on their value after a
logic instruction.

## Instruction set — Basic Mode

```
LOAD  STORE  ADD  SUB  AND  OR  XOR  NOT  JMP  JZ  JC  PRINT  HALT
```

`PRINT` is an **educational instruction of the PubVM**, not a physical CPU
instruction (section 13 of the specification). It appends the register's
stored value, in unsigned decimal, to the machine's output.

Advanced Mode, stage A: `PUSH` and `POP` (see "Stack" above). `CALL`, `RET`,
shifts, rotates, `JN`, `JO`, `JNZ`, `JNC`, `ENTER` and `LEAVE` are **not
implemented** yet.

## Encoding

A program is really assembled into memory and `PC` is a real memory address,
so the memory view of the laboratory shows machine code rather than zeros.

One opcode byte, then the operands. The high nibble is the operation group and
the low bits select the operand form, which keeps a memory dump readable.
`W` = `wordSize / 8`, `A` = `addressBits / 8` (2).

| opcode | instruction | layout | length |
|---|---|---|---|
| `0x00` | `HALT` | `op` | 1 |
| `0x10` | `LOAD reg, imm` | `op reg imm:W` | 2+W |
| `0x11` | `LOAD reg, reg` | `op reg reg` | 3 |
| `0x12` | `LOAD reg, [addr]` | `op reg addr:A` | 2+A |
| `0x18` | `STORE [addr], reg` | `op addr:A reg` | 2+A |
| `0x20` | `ADD reg, imm` | `op reg imm:W` | 2+W |
| `0x21` | `ADD reg, reg` | `op reg reg` | 3 |
| `0x28` | `SUB reg, imm` | `op reg imm:W` | 2+W |
| `0x29` | `SUB reg, reg` | `op reg reg` | 3 |
| `0x30` | `AND reg, imm` | `op reg imm:W` | 2+W |
| `0x31` | `AND reg, reg` | `op reg reg` | 3 |
| `0x38` | `OR reg, imm` | `op reg imm:W` | 2+W |
| `0x39` | `OR reg, reg` | `op reg reg` | 3 |
| `0x40` | `XOR reg, imm` | `op reg imm:W` | 2+W |
| `0x41` | `XOR reg, reg` | `op reg reg` | 3 |
| `0x48` | `NOT reg` | `op reg` | 2 |
| `0x50` | `JMP addr` | `op addr:A` | 1+A |
| `0x51` | `JZ addr` | `op addr:A` | 1+A |
| `0x52` | `JC addr` | `op addr:A` | 1+A |
| `0x60` | `PRINT reg` | `op reg` | 2 |
| `0x70` | `PUSH reg` | `op reg` | 2 |
| `0x71` | `POP reg` | `op reg` | 2 |

Immediates and addresses are little-endian. Immediate width follows the word
size, so **the same source produces a different image on each variant** —
which is part of what the laboratory is meant to show. The conformance program
of the test suite assembles to 63 bytes on PubVM-8, 72 on PubVM-16 and 90 on
PubVM-32, from identical source.

A practical consequence worth teaching: because the program is longer on a
wider machine, a data address that is free on PubVM-8 can land **inside the
program's own code** on PubVM-32. Nothing stops a `STORE` from overwriting
code — that is what a real machine does too — so examples place their data
clear of the longest image.

`Opcodes.kf` holds this table once; the assembler encodes from it and the
engine decodes from it, so the two cannot disagree.

The golden program assembles to 12 bytes on PubVM-8:

```
LOAD A, 250    10 00 FA
LOAD B, 20     10 01 14
ADD  A, B      21 00 01
PRINT A        60 00
HALT           00
```

## Execution

```kof
machine.load(image)       // install a program and go to READY
machine.reset()           // back to the state right after load
machine.step()            // exactly one instruction
machine.run(maxCycles)    // until HALT, a fault, a pause, or the budget
machine.requestPause()
machine.halt()
machine.snapshot()        // a complete, immutable reading of the state
```

Status: `READY`, `RUNNING`, `PAUSED`, `HALTED`, `ERROR`.

- `step()` executes one instruction and leaves the machine `PAUSED`, ready for
  the next one.
- `run(maxCycles)` is bounded on purpose: a program can loop forever. If it
  returns with status `PAUSED`, the program **did not finish** — the budget ran
  out or a pause was requested. Calling `run` again resumes.
- `requestPause()` is consumed by the run it stops, so it never poisons the
  next one.
- On `HALT`, `PC` stays **on** the HALT instruction: the machine stopped there.
- An unknown opcode or an out-of-range memory access sets status `ERROR` with a
  message in `errorMessage`. The machine does not crash and does not continue.
- `reset()` rewrites memory from the program image, so anything the program
  wrote to memory is undone.

`snapshot()` returns a `MachineState` record — registers, flags, PC, cycles,
status, output and the text of the current instruction. The current
instruction is **disassembled from the bytes in memory**, not remembered from
the source, so what is displayed is what the machine will actually execute.
