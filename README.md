[English](README.md) | [Português](README.pt_BR.md)

# PubLab

**Interactive Computer Architecture Laboratory**

> See the machine.

[![Deploy to GitHub Pages](https://github.com/PublioSantos/publab/actions/workflows/pages.yml/badge.svg)](https://github.com/PublioSantos/publab/actions/workflows/pages.yml)
**Powered by: [Kof](https://github.com/KofLang/Kof4j)**

### 👉 [Try PubLab right now — no install](https://publiosantos.github.io/publab/)

It redeploys automatically on every push to `main`, so that page always runs
the current version — and a push is never published unless it first passes
the full test suite on both targets. What you see there is exactly this
repository.

---

PubLab is a laboratory for learning how a computer works on the inside. You
write a few lines of assembly, press **Step**, and watch it actually happen:
the registers change, a flag flips, a byte lands in memory, the program
counter moves to the next instruction — in the real, running machine, not in
a diagram.

Open it and load `overflow.pasm`, the example it starts with:

```asm
    LOAD A, 250
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
```

Run it on `PubVM-8` and `A` ends up `14` with the carry flag set. Switch the
machine selector to `PubVM-16` with no other change, run it again, and `A`
is `270` instead — same source, same instructions, different answer,
because 270 does not fit in an 8-bit register. That one difference *is* the
lesson, and the laboratory lets you watch it happen rather than take it on
faith.

## Why this matters

**It opens hardware's "black box."** Most developers entering the field
today start out working with high-level abstractions — Python, JavaScript,
frameworks, the cloud. That produces great programmers, but it leaves a gap
when it comes to understanding what the processor actually does with the
code. PubLab makes the physics of software visible: registers, the bus,
flags, bit overflow, the stack pointer. It runs entirely in the browser, on
any operating system, with nothing to install and a modern UI — the barrier
to entry is immediate, and what it teaches is root cause, not trivia.
Watching `250 + 20` really produce `14` at 8 bits and `270` at 16 bits is
what makes classic production bugs — integer overflow, stack leaks, memory-
precision issues — click once and for all, instead of staying a rule to
memorize.

**It connects theory, history and the industry.** Bringing a parameterized
educational VM, the historical 8051 (8-bit CISC) and the modern Cortex-M3
(32-bit ARM) into the same environment gives students and senior engineers
alike a panoramic view of how computer architecture evolved into the chips
that drive the industry today — IoT, automation, embedded systems.

```
PubLab
├── PubASM        the educational assembly language
├── PubVM         the educational virtual machine
│   ├── PubVM-8
│   ├── PubVM-16
│   └── PubVM-32
├── 8051          historical architecture      (educational model, planned)
└── Cortex-M3     modern ARM architecture      (educational model, planned)
```

## Running it locally

Requires the [Kof toolchain](https://github.com/KofLang/Kof4j) (built against
`0.5.0-beta`):

```bash
kof run Main.kf --target js    # opens the laboratory in Kof's webview
kof test tests                 # the full suite, JVM target
kof test tests --target js     # the same suite, JS target
```

## What's inside

- **PubVM**, one core configured three ways (`PubVM-8`/`-16`/`-32`) — same
  registers, same instruction set, same encoding logic, only the word width
  changes. `tests/matrix_test.kf` runs the entire instruction set, the
  encoding, immediates, memory, labels, branches and all four flags across
  every variant, from identical PubASM source, so the three variants cannot
  quietly drift apart.
- **PubASM**, a small two-pass assembler with labels, diagnostics in English
  and Portuguese, and a source map the debugger uses to highlight the line
  the machine is on.
- **A real debugger**: a memory dump (hex/dec/bin) with the program counter
  and the last instruction's writes both marked, a before/after list of
  everything that instruction changed, and a STACK panel tracking `SP`/`FP`
  live.
- **A plain-language EXPLANATION panel**: what the last Step or Run actually
  did, in a sentence, built from the same before/after state the debugger
  reads — not a second, separate interpretation of the program that could
  drift from what really happened.
- **Advanced Mode**, fully implemented: `X`/`Y` general registers, a real
  stack (`SP`/`FP`, `PUSH`/`POP` with explicit overflow/underflow faults,
  never a silent wrap), `CALL`/`RET`/`ENTER`/`LEAVE`, shifts and rotates, and
  the full set of conditional jumps.

Development follows the order in the specification: machine → tests →
assembler → debugger → UI → educational layer → Advanced Mode. Every row
below is enforced by the test suite.

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
| 9 | 8051 educational model | stages A-B done (core + assembler + P0, no UI yet) |
| 10 | Cortex-M3 educational model | stage A done (core + assembler, no UI yet) |
| 11 | Architecture comparison | not started |
| 12 | Export | not started |

One absence in phases 1-8 is deliberate rather than pending: there is no
**Pause** button, because Kof's JS UI runtime has no timer, so a run cannot
be interrupted by a click while it is executing. What exists instead is
real: `Run` is bounded by a cycle budget, reports honestly when it did not
finish, and continues right where it left off on the next click.

## Two more architectures are coming — 8051 and Cortex-M3

Phases 9 and 10 will add two more educational models, and it matters to be
upfront about what that will and will not be:

- PubLab is **not** an emulator and **not** a development tool for real 8051
  or ARM Cortex-M3 hardware. A program that runs in PubLab is **not**
  guaranteed to behave the same way on a physical chip — never use it as a
  reference for firmware, certification, timing analysis or any production
  decision.
- Only an explicitly documented subset of each architecture's instructions
  and peripherals will be modelled, chosen for what it teaches. Anything
  outside that subset will be absent, not approximated — and wherever a real
  register name or address is used, the specific MCU will be named. PubLab
  will not invent peripheral addresses, registers or behaviours and present
  them as real hardware.

For real work on those architectures, use the manufacturer's documentation
and toolchain. Neither module is implemented yet — see
[docs/8051.md](docs/8051.md) and [docs/cortex-m3.md](docs/cortex-m3.md) for
what is planned.

## Attribution on screen

PubLab displays **Powered by: Kof** in the footer of the window, as a plain
line linking to <https://github.com/KofLang/Kof4j> — no styling applied to it.

The text and the URL live in `publab/app/Brand.kf` as the single source the
interface reads — `poweredByLabel()` and `poweredByUrl()` — rather than as a
string the UI could forget or let drift. Covered by `tests/brand_test.kf`.

## License

MIT — see [LICENSE](LICENSE).

## Documentation

- [docs/architecture.md](docs/architecture.md) — layers and how they are kept apart
- [docs/pubvm.md](docs/pubvm.md) — the machine: registers, flags, memory, encoding
- [docs/pubasm.md](docs/pubasm.md) — the language: syntax, instructions, diagnostics
- [docs/8051.md](docs/8051.md) — educational model (not implemented)
- [docs/cortex-m3.md](docs/cortex-m3.md) — educational model (not implemented)
- [examples/](examples/) — programs that really run, with comments in English and Portuguese

The teaching documentation of section 38 of the specification (what a CPU is,
what a register is, what overflow is) arrives with phases 9-10.

## Targets

The core runs on both Kof targets from the same source — there is no second
implementation of the machine in JavaScript:

```
                  ┌── jvm   (tests, and a future CLI)
PubVM core ───────┤
                  └── js    (the browser UI, and the live page above)
```

`tests/js_parity_test.kf` is the parity battery: the bitwise and numeric
operations the core depends on (SG-002), plus guards against the two
JS-target codegen defects found in phase 5A. See
[docs/architecture.md](docs/architecture.md) and
[notes/kof-compiler-findings.md](notes/kof-compiler-findings.md).
