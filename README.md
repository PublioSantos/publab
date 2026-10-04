[English](README.md) | [Português](README.pt_BR.md)

# PubLab

**Interactive Computer Architecture Laboratory**

> See the machine.

**Powered by: [Kof](https://github.com/KofLang/Kof4j)**

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
| 5B | Minimal UI | not started |
| 6 | Debugger | not started |
| 7 | Educational layer | not started |
| 8 | Advanced Mode — X, Y, SP, FP, stack, shifts, extra jumps | not started |
| 9 | 8051 educational model | not started |
| 10 | Cortex-M3 educational model | not started |
| 11 | Architecture comparison | not started |
| 12 | Export | not started |

The machine core is **parameterized by word size**: PubVM-8, -16 and -32 are
one implementation configured differently, never three copies. All three are
validated end to end — `tests/matrix_test.kf` runs the whole Basic Mode
instruction set, the encoding, immediates, memory, PC, labels, branches and
all four flags over every variant, from identical PubASM source.

There is **no user interface yet**. The machine is driven from the test suite
and from Kof code.

Advanced Mode instructions (`PUSH`, `POP`, `CALL`, `RET`, `SHL`, `SHR`, `ROL`,
`ROR`, `JN`, `JO`, `JNZ`, `JNC`, `ENTER`, `LEAVE`) and the registers `X`, `Y`,
`SP`, `FP` are **not implemented**. The assembler recognises them and says so,
rather than reporting them as unknown.

## Attribution on screen

PubLab displays **Powered by: Kof**, linking to
<https://github.com/KofLang/Kof4j>, next to the product name.

There is no interface yet (phase 5B), so the attribution lives in
`publab/app/Brand.kf` as the single source of truth the interface will render
— `poweredByLabel()` and `poweredByUrl()` — rather than as a string the UI
could forget. It is covered by `tests/brand_test.kf`.

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
