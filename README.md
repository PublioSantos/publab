[English](README.md) | [Português](README.pt_BR.md)

# PubLab

**Interactive Computer Architecture Laboratory**

> See the machine.

**Powered by: [Kof](https://github.com/KofLang/Kof4j)**

[![Deploy to GitHub Pages](https://github.com/PublioSantos/publab/actions/workflows/pages.yml/badge.svg)](https://github.com/PublioSantos/publab/actions/workflows/pages.yml)

**Try it live:** <https://publiosantos.github.io/publab/> — rebuilt and
redeployed automatically on every push to `main` (see
[.github/workflows/pages.yml](.github/workflows/pages.yml)), so the page
always runs the current version. A push is never published unless it first
passes the full test suite on both targets.

PubLab is a laboratory for learning how a computer works on the inside: you
write a small program, execute it one instruction at a time and watch the
registers, the flags, the memory and the program counter actually change.

```
PubLab
├── PubASM        the educational assembly language
├── PubVM         the educational virtual machine
│   ├── PubVM-8
│   ├── PubVM-16
│   └── PubVM-32
├── 8051          historical architecture      (educational model)
└── Cortex-M3     modern ARM architecture      (educational model)
```

---

## ⚠️ 8051 and Cortex-M3: simplified educational models

**Simplified implementation for learning — not production-compatible code.**

The 8051 and Cortex-M3 modules of PubLab are **teaching models**. When they
are implemented they will cover a documented subset of each architecture,
chosen for what it teaches, and every peripheral that is an abstraction rather
than real silicon will say so on the page where it appears.

What that means concretely:

- PubLab is **not** an emulator, and it is **not** a development tool for
  real 8051 or ARM Cortex-M3 hardware.
- A program that runs in PubLab is **not** guaranteed to behave the same way
  on a physical chip, and must never be used as a reference for firmware,
  certification, timing analysis or any production decision.
- Only an explicitly documented subset of the instructions and peripherals is
  modelled. Anything outside that subset is absent, not approximated.
- Where real register names or addresses are used, the specific MCU is named.
  PubLab does not invent peripheral addresses, registers, instructions or
  behaviours and present them as real hardware.

For real work on those architectures, use the manufacturer's documentation and
toolchain.

**Current status: neither module is implemented.** They are planned for
phases 9 and 10. See [docs/8051.md](docs/8051.md) and
[docs/cortex-m3.md](docs/cortex-m3.md).

---

## What is implemented today

Development follows the order in the specification: machine → tests →
assembler → debugger → UI → educational layer. Nothing below is claimed
unless it is covered by the test suite.

| Phase | Area | Status |
|---|---|---|
| 1 | PubVM core — registers, memory, flags, ALU, execution engine | **done** |
| 2 | PubASM — lexer, parser, labels, diagnostics, assembler | **done** |
| 3 | PubVM-16 (same core, wider word) | **done** |
| 4 | PubVM-32 (same core, wider word) | **done** |
| 5A | JS-target parity for the core | **done** |
| 5B | Minimal UI | **done** |
| 6 | Debugger | **done** |
| 7 | Educational layer | **done** |
| 8 | Advanced Mode — X, Y, SP, FP, stack, shifts, extra jumps | **done** |
| 9 | 8051 educational model | not started |
| 10 | Cortex-M3 educational model | not started |
| 11 | Architecture comparison | not started |
| 12 | Export | not started |

The machine core is **parameterized by word size**: PubVM-8, -16 and -32 are
one implementation configured differently, never three copies. All three are
validated end to end — `tests/matrix_test.kf` runs the whole Basic Mode
instruction set, the encoding, immediates, memory, PC, labels, branches and
all four flags over every variant, from identical PubASM source.

The laboratory window is the minimal interface of phase 5B: a PubASM editor, a
machine selector, an example selector, a language selector, the four controls,
the registers in decimal/hexadecimal/binary, the flags, the status with PC and
cycle count, the current instruction read back out of memory, the output and
the diagnostics. It renders in the browser from the same core the tests run.

```bash
kof run Main.kf --target js
```

The debugger of phase 6 adds to it: the memory dump in hexadecimal, decimal
or binary with PC and the cells the last instruction wrote both marked, a
before/after list of everything that instruction changed, a one-character
change marker on the registers and flags, and the source line PC is on,
through the assembler's source map.

The educational layer (phase 7) adds a plain-language EXPLANATION panel: what
the last Step or Run actually did, built from the same before/after snapshots
the debugger's change list reads — never a second interpretation of the
program.

Advanced Mode (phase 8) is **done**, built in three stages. Stage A: `X` and
`Y` are ordinary general registers; `SP` and `FP` are implemented as
addresses next to `PC` (not word-sized registers — `SP`'s initial value, one
past the top of memory, does not fit an 8-bit or 16-bit word); `PUSH` and
`POP` move the stack, with explicit overflow/underflow faults, never a
silent wrap. Stage B: `CALL` and `RET` push/pop the return address, `ENTER`
and `LEAVE` are the classic save-FP / restore-FP prologue and epilogue — all
through the same stack and the same overflow/underflow checks `PUSH`/`POP`
use, but moving `addressBytes` rather than `wordBytes` (a return address and
a saved FP are locations, not data — see "Stack" in
[docs/pubvm.md](docs/pubvm.md)). The debugger's STACK panel shows SP/FP and
the words on the stack, read from the real memory through SP. Stage C:
`SHL`/`SHR`/`ROL`/`ROR` take the same `op reg, imm`/`op reg, reg` forms as
`ADD`/`SUB` (the second operand is the shift/rotate count), with `C` set to
the one bit that actually crossed the word's boundary; `JN`, `JO`, `JNZ`
and `JNC` round out the conditional jumps. Every Advanced Mode mnemonic the
specification lists is now implemented — `ASM010` ("belongs to Advanced
Mode, not implemented yet") has no live example left to assemble it from.
The EXPLANATION panel covers all of it too: `PUSH`/`POP`/`CALL`/`RET`/
`ENTER`/`LEAVE` describe what moved on the stack, and the shifts/rotates
name the carry bit that crossed the boundary.

One absence is deliberate rather than pending:

- **No Pause button.** Kof's JS UI runtime has no timer, so a run cannot be
  interrupted from a button — the click could not be delivered while the run
  is executing. What exists instead is real: `Run` is bounded by a cycle
  budget, reports that it did not finish, and continues where it left off.
  The engine keeps `requestPause()` for a caller that can drive the machine
  in slices.

## Attribution on screen

PubLab displays **Powered by: Kof** in the footer of the window, as a plain
line linking to <https://github.com/KofLang/Kof4j> — no styling applied to it.

The text and the URL live in `publab/app/Brand.kf` as the single source the
interface reads — `poweredByLabel()` and `poweredByUrl()` — rather than as a
string the UI could forget or let drift. Covered by `tests/brand_test.kf`.

## Running the tests

Requires the Kof toolchain (built against 0.5.0-beta):

```bash
kof test tests
```

## License

MIT — see [LICENSE](LICENSE).

## Documentation

- [docs/architecture.md](docs/architecture.md) — layers and how they are kept apart
- [docs/pubvm.md](docs/pubvm.md) — the machine: registers, flags, memory, encoding
- [docs/pubasm.md](docs/pubasm.md) — the language: syntax, instructions, diagnostics
- [docs/8051.md](docs/8051.md) — educational model (not implemented)
- [docs/cortex-m3.md](docs/cortex-m3.md) — educational model (not implemented)
- [examples/](examples/) — programs that really run

The teaching documentation of section 38 of the specification (what a CPU is,
what a register is, what overflow is) arrives with the educational layer in
phase 7.

## Targets

The core runs on both Kof targets from the same source — there is no second
implementation of the machine in JavaScript:

```
                  ┌── jvm   (tests, and a future CLI)
PubVM core ───────┤
                  └── js    (the browser UI, phase 5B)
```

Both are green on the whole suite:

```bash
kof test tests
kof test tests --target js
```

`tests/js_parity_test.kf` is the parity battery: the bitwise and numeric
operations the core depends on (SG-002), plus guards against the two
JS-target codegen defects found in phase 5A. See
[docs/architecture.md](docs/architecture.md) and
[notes/kof-compiler-findings.md](notes/kof-compiler-findings.md).
