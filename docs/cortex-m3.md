[English](cortex-m3.md) | [Português](cortex-m3.pt_BR.md)

# Cortex-M3 — educational model

## ⚠️ Simplified implementation for learning — not production-compatible code

The ARM Cortex-M3 module of PubLab is a **teaching model**, not an emulator
and not a development tool for real ARM hardware.

- A program that runs here is **not** guaranteed to behave the same way on a
  physical Cortex-M3, and must never be used as a reference for firmware,
  certification, timing analysis or any production decision.
- Only an explicitly documented subset of the Thumb instruction set is
  modelled. What is outside that subset is **absent, not approximated**.
- Peripherals (GPIO, UART, SysTick, Timer) are marked `conceptual` or
  `based on <specific MCU>`. **No peripheral address is invented.** The
  Cortex-M3 core defines very little of what a board exposes; whenever a real
  register or address is used, the specific part is named.
- Interrupt latency, cycle counts, the memory protection unit, caches,
  pipelining and electrical behaviour are **not** modelled.
- Any future export to real hardware (phase 12) must state the MCU and
  target explicitly.

## Status: stage A done

This page is the full scope for phase 10, marked item by item as real
architecture or educational abstraction (Rule 7 of the specification),
following the same discipline phase 8 (Advanced Mode) and phase 9 (8051)
used: documented and approved before any code was written. Implementation
proceeds in stages, each with its own tests.

- **Stage A — done.** Core: registers, APSR flags, a flat memory space,
  the Thumb subset below, conditional branches, `BL`/`BX LR`,
  multi-register `PUSH`/`POP`. Lives in `publab/cm3/`, its own
  self-contained toolchain — not a mode of PubVM's or the 8051's. Covered
  by `tests/cm3_core_test.kf`, `tests/cm3_asm_test.kf`,
  `tests/cm3_engine_test.kf` and `tests/cm3_golden_test.kf`. No UI tab
  yet, same order the other two machines followed.
- **Stage B** — one GPIO port, modelled the same way 8051's `P0` is: a
  plain readable/writable register, conceptual, no peripheral address
  invented.

## Registers

| name | width | real or abstraction |
|---|---|---|
| `R0`-`R12` | 32-bit | real — a genuinely flat register file, unlike the 8051's banked `R0`-`R7`. This is itself a teaching point for phase 11: two "general-purpose registers" schemes that work completely differently under the same kind of name. |
| `SP` (`R13`) | 32-bit | real, but **narrowed**: real Cortex-M3 has two stack pointers (Main SP and Process SP, switched by a CONTROL register bit, for RTOS use). This model has **one** SP — the Main SP only. Process SP and the switch are absent, not approximated; they are a real feature, tied to an RTOS/privilege model this lab does not otherwise have a use for. |
| `LR` (`R14`) | 32-bit | real — holds the return address after `BL`, exactly like real hardware. Unlike PubVM's or the 8051's `CALL`, **`BL` does not touch the stack at all** — a nested call must `PUSH {LR}` itself before calling again, or the first return address is simply lost. That is real ARM behaviour, not a simplification, and it is one of the clearest comparisons phase 11 is for. |
| `PC` (`R15`) | 32-bit | real, with one narrowing: real hardware reads `PC` as "the address of the current instruction + 4" when used as a data operand (the Thumb pipeline's historical offset), which no instruction in stage A exposes — `PC` is only ever the fetch address here, never read as a data value. |

## Flags (APSR: `N`, `Z`, `C`, `V`)

Real, and — unlike the 8051's `C`/`AC`/`OV`/`P` — the same four-letter shape
PubVM already uses (`C`, `Z`, `N`, `O`), which is deliberate: phase 11's
comparison needs at least one architecture whose flags line up with
PubVM's almost by name, so the comparison is about behaviour, not
vocabulary.

| flag | meaning | real or abstraction |
|---|---|---|
| `N` | sign bit of the result | real |
| `Z` | result is zero | real |
| `C` | carry out (data-processing) / NOT borrow (on `SUB`/`CMP`, ARM's carry convention is the complement of a subtract borrow — see below) | real |
| `V` | signed overflow | real |

### A real difference from both PubVM and the 8051: `CMP` sets flags without storing a result

`CMP Rn, Rm` (and `CMP Rn, #imm`) computes `Rn - Rm` for the flags **only** —
the subtraction's result is discarded, never written to a register. This is
the real, idiomatic way ARM code decides a branch: compute the comparison
with `CMP`, then branch with a condition that reads the flags `CMP` just
set — unlike PubVM/8051, where the flags a jump tests come from whatever
arithmetic instruction happened to run right before it.

### `C` on `SUB`/`CMP` is real ARM's own convention, not PubVM's

Real ARM defines `C` on a subtract as **NOT borrow** (`C = 1` means no
borrow occurred — the opposite sense from PubVM's and the 8051's `C`, which
are both "borrow occurred"). This model keeps that real inversion rather
than normalising it to match PubVM, because the inversion itself —
"the same flag name means the opposite thing on a different real
architecture" — is exactly what phase 11 exists to show.

### Which instructions touch which flags

| instruction | N | Z | C | V |
|---|---|---|---|---|
| `ADD`, `ADC` | set | set | set | set |
| `SUB`, `CMP` | set | set | set (NOT borrow — see above) | set |
| `AND`, `ORR`, `EOR` | set | set | unchanged | unchanged |
| `MOV` | set | set | unchanged | unchanged |
| `LDR`, `STR`, `B`, `B<cond>`, `BL`, `BX`, `PUSH`, `POP`, `HALT`, `PRINT` (educational) | unchanged | unchanged | unchanged | unchanged |

Real Thumb-1 hardware sets flags on data-processing instructions
unconditionally outside an `IT` block (a Thumb-2 feature, see "Explicitly
out of scope") — so this model always updates flags on `ADD`/`SUB`/`CMP`/
logic/`MOV`, which is the real, simple-case behaviour, not an abstraction.
The `S` suffix real assemblers sometimes require (`ADDS` vs `ADD`) is not
modelled as a separate mnemonic — see "Instructions" below.

## Memory

```
Memory   64 KB, one flat address space (code and data together)
```

Real Cortex-M3 exposes a single, unified address space to software too
(Flash, SRAM and peripherals at different fixed ranges of the same map) —
this model's **simplification** is size and the absence of fixed regions:
one flat 64 KB space, with no reserved Flash/SRAM/peripheral ranges,
because stage A has no peripheral yet to carve out a region for (stage B's
GPIO port is a named register, not a memory-mapped address — see
"Peripherals").

## Instructions — stage A

Real Thumb mnemonics, a deliberately small subset:

| instruction | forms | notes |
|---|---|---|
| `MOV` | `MOV Rd, #imm` · `MOV Rd, Rm` | real |
| `ADD` | `ADD Rd, Rn, Rm` · `ADD Rd, Rn, #imm` | real; three-operand form, like real Thumb (`Rd` need not be `Rn`) |
| `SUB` | `SUB Rd, Rn, Rm` · `SUB Rd, Rn, #imm` | real, same three-operand shape |
| `AND`, `ORR`, `EOR` | `op Rd, Rn, Rm` | real mnemonics (`EOR`, not PubVM's `XOR`); no immediate form in stage A — real Thumb-1's immediate logic forms are narrow and not worth the encoding effort here |
| `CMP` | `CMP Rn, Rm` · `CMP Rn, #imm` | real — see "A real difference" above |
| `LDR`, `STR` | `op Rd, [Rn]` · `op Rd, [Rn, #imm]` | real — the only way to touch memory; there is no memory operand on `ADD`/`SUB`/etc., the real load/store-architecture restriction |
| `B` | `B label` | real, unconditional |
| `BEQ`, `BNE`, `BCS`, `BCC`, `BMI`, `BPL`, `BVS`, `BVC` | `op label` | real condition codes, reading `Z`/`C`/`N`/`V` exactly as real hardware's condition logic does (`BCS`≡`BHS`, `BCC`≡`BLO` are the same real condition under ARM's two names — only one spelling each is implemented) |
| `BL` | `BL label` | real — `LR = return address`, `PC = label`. No stack involved (see "Registers" above). |
| `BX` | `BX LR` | real — `PC = LR`. The real return idiom; only the `LR` operand form is implemented (real `BX` accepts any register) |
| `PUSH`, `POP` | `op {reglist}` | real Thumb syntax — a **list** of registers in braces, not a single register the way PubVM's/the 8051's `PUSH`/`POP` are. Stored/loaded in increasing register-number order to/from increasing addresses, full-descending (`SP` decremented by the whole list's size *before* the first store) — the real `STMDB`/`LDM` behaviour `PUSH`/`POP` expand to. |
| `HALT` | `HALT` | **not a real Cortex-M3 instruction.** Same justification as PubVM's and the 8051's educational `HALT`. |
| `PRINT` | `PRINT Rd` | **not a real instruction**, reused verbatim for the same reason. |

## Explicitly out of scope for phase 10

- **Thumb-2 32-bit instructions, `IT`/`ITE` conditional-execution blocks** —
  real Cortex-M3 supports both 16-bit Thumb and 32-bit Thumb-2 instructions
  in the same stream; this model implements only 16-bit-shaped Thumb-1-style
  instructions and has no conditional-execution-without-branching construct.
- **The barrel shifter** (`LSL`/`LSR`/`ASR`/`ROR` as a shifted second operand
  on data-processing instructions, and as standalone instructions) — a real,
  significant part of the Thumb ISA, absent here, not approximated.
- **`MUL`, long multiply/divide, saturating arithmetic** — absent.
- **Exceptions and interrupts** (the NVIC, `SVC`, fault handlers, the vector
  table, `PRIMASK`/`FAULTMASK`/`BASEPRI`) — a real, large part of the
  Cortex-M3 programming model, entirely out of scope for phase 10. Like the
  8051's interrupts, this would need its own Rule 7 scope document if ever
  modelled.
- **The Process stack pointer and the CONTROL register** — see "Registers"
  above (`SP`).
- **Bit-banding, the MPU, caches, the debug/trace unit (ITM, DWT)** — absent.
- **SysTick, UART, Timer peripherals** — only one GPIO port is planned
  (stage B). The rest are absent until a future phase scopes them the same
  way this page scopes the GPIO port.
- **Cycle counts, pipelining, interrupt latency, electrical behaviour** —
  never modelled, as stated at the top of this page.

## Peripherals — stage B

| name | model |
|---|---|
| GPIO port (one) | **conceptual** — based on the general shape of a Cortex-M3 GPIO port (a data register that is directly readable and writable), not a specific manufacturer's exact register layout or address, since the Cortex-M3 core itself defines no peripheral addresses at all — those are entirely vendor-specific (the whole reason this page's opening disclaimer says "no peripheral address is invented"). Modelled the same way as the 8051's `P0`: a plain register, no electrical nuance (drive strength, pull-up/down configuration, alternate function muxing — all real on actual silicon) modelled. |
