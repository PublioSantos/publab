[English](architecture-comparison.md) | [Português](architecture-comparison.pt_BR.md)

# Architecture comparison — educational model

## Status: stages A and B done

This page is the full scope for phase 11, written before any code, the same
discipline phases 8, 9 and 10 used. Phase 11 is **not** a fourth machine: it
adds no silicon semantics of its own. It is a teaching feature built entirely
on facts phases 8-10 already established and documented — this page's job is
to say exactly which of those facts it surfaces, and how, not to invent new
ones.

## Why phase 11 exists

By the end of phase 10, PubLab can run three real architectures — PubVM,
the 8051 and the Cortex-M3 — but only one at a time, each in its own tab,
each teaching its own facts in isolation. A student can learn that the 8051's
stack grows upward, or that the Cortex-M3's `BL` never touches the stack,
but nothing in the lab puts those two facts **next to each other**. Phase 11
is that juxtaposition: the same small task, written once per architecture,
run side by side, so the differences documented in `docs/8051.md` and
`docs/cortex-m3.md` as prose become something the student watches happen.

## What phase 11 is not

- **Not a unified instruction set or a translation layer.** There is no
  "write once, run on all three" assembly. Each architecture keeps its own
  real mnemonics, forms and registers, exactly as phases 9 and 10 modelled
  them. A comparison program is three separate, independently assembled
  source files — one per architecture — that happen to do the same
  conceptual thing.
- **Not a fourth toolchain.** No new lexer, parser, assembler or engine.
  Phase 11 is UI and example content only, built on the three engines that
  already exist (`publab/machine`, `publab/i8051`, `publab/cm3`).
- **Not an exhaustive comparison.** Only the differences already named as
  "real, not abstraction" in phases 8-10's Rule 7 tables are surfaced.
  Phase 11 does not go looking for new real-vs-abstraction distinctions of
  its own.

## Stage A — 8051 and Cortex-M3 get a UI tab each — done

Kof's UI runtime has no tab or visibility widget (`docs/architecture.md` lists
the toolkit's real constraints), so "tab" here means a self-contained
section, not a dynamically shown/hidden pane: all three laboratories —
PubVM, 8051, Cortex-M3 — sit one below another in the same window, each with
its own editor, controls, registers, flags, output, diagnostics and
explanation. `publab/ui/Lab8051.kf` and `publab/ui/LabM3.kf` are the
controllers (mirroring `Lab.kf`'s shape); `Presenter8051.kf`/`PresenterM3.kf`
render their state; `Explain8051.kf`/`ExplainM3.kf` give each one a
generic "what changed" explanation (registers and flags that differed
between the before/after snapshot) rather than the hand-tuned
per-mnemonic prose phase 7 wrote for PubVM — phase 11 is a comparison
feature, not a second educational layer to maintain per architecture.

Phases 9 and 10 stopped at the engine: "no UI tab yet, same order the other
two machines followed" (docs/8051.md, docs/cortex-m3.md). Phase 11 cannot
show three machines side by side if two of them have no screen at all, so
stage A closes that gap first, one tab each, following the same shape
PubVM's tab already has (phase 5B/6/7): source editor, Step/Run, a register
panel, a flags panel, a memory/stack view, and a plain-language explanation
line built from before/after state — not a second interpretation of the
program that could drift from what really happened, the same rule
`docs/architecture.md` states for PubVM's own explanation panel.

| item | real or abstraction |
|---|---|
| the tab itself (editor, Step/Run, panels) | **educational** — a UI affordance, not a hardware fact, same status as PubVM's existing tab |
| register/flag/stack panel contents | **real** — reads directly from each engine's own `snapshot()` (`MachineState8051`, `MachineStateM3`), already validated by phases 9-10's test suites; stage A adds no new machine facts, only a renderer for facts that already exist |
| the explanation line | **educational**, built the same way phase 7's `Explain.kf` is: a sentence derived from the actual before/after state, never a hand-written description of what an instruction is "supposed to" do |

Each tab is its own self-contained UI module (`publab/ui/Lab8051.kf`,
`publab/ui/LabM3.kf` or similar), mirroring `Lab.kf`'s shape rather than
generalizing it — the three toolchains have stayed deliberately independent
through phases 9-10 for exactly this reason (so each architecture's real
idiosyncrasies stay faithful, not normalized), and the UI layer keeps that
same independence.

## Stage B — the comparison view — done

Implemented as `publab/ui/Compare.kf`, its own controller (the same
independence Stage A's three tabs keep): a program selector, Assemble and
"Step (all three)" controls, and three compact per-architecture panels —
status, output, and the same generic explanation Stage A's tabs use. Once
all three machines have a tab, stage B adds a fourth view: not a new
machine, a side-by-side reading of the other three. The student picks one
of a small set of **comparison programs** — a short task implemented three
times, once per architecture, in each one's own real assembly — and the lab
runs all three at once, Step-synchronized (one Step advances all three by
one instruction each), with the known real differences called out as each
one happens.

### Comparison programs (stage B's content, not new engine features)

Each comparison program is three example sources (e.g.
`examples/compare/add_overflow.pasm`, `.a51`, `.cm3`), picked because the
difference it shows is already a documented **real** fact from phases 8-10,
not a new claim:

| task | what it shows | the real difference (already documented) |
|---|---|---|
| add two numbers past the register width | the same overflow, three different flag vocabularies | PubVM's `C`/`O` are "borrow/overflow happened"; the 8051 has no persistent `Z`, only `C`/`AC`/`OV`/`P`; the Cortex-M3's `C` on a subtract is **NOT borrow**, the opposite sense from the other two (docs/cortex-m3.md, "A real difference") |
| a subroutine call and return | three real calling conventions | PubVM's `CALL`/`RET` push/pop a return address on a stack growing **downward**; the 8051's `CALL`/`RET` push/pop low-byte-then-high-byte on a stack growing **upward** (docs/8051.md); the Cortex-M3's `BL`/`BX LR` touch **no stack at all** — a nested call that forgets `PUSH {LR}` silently loses the outer return address (docs/cortex-m3.md, "Registers") |
| a register-wide value moved through a "port" | the same `PRINT`-visible round trip, different register shapes | PubVM's `X`/`Y` are ordinary general registers; the 8051's `R0`-`R7` are **banked**, aliased into Internal Data Memory by `PSW.RS1:RS0` (docs/8051.md); the Cortex-M3's `R0`-`R12` are a genuinely **flat** file, and its `GPIOA` is reachable only by `MOV`, never by `ADD`/`SUB`/etc. (docs/cortex-m3.md) |

Three programs, not more, for stage B — each one reusing a difference the
project has already proven real and already written up, rather than phase
11 researching new ones. A fourth comparison (e.g. the 8051's `DPTR` vs
PubVM's address bus) is a natural future addition, not required for stage B
to be complete.

| item | real or abstraction |
|---|---|
| the comparison programs | **real-per-architecture** — each one is an ordinary, independently valid program in its own real assembly; nothing about running it changes what phases 9-10 already validated |
| Step-synchronization across three machines | **educational** — real hardware has no such concept; it exists only so a student sees "the same conceptual step" on three screens at once |
| the "what's different here" callout | **educational presentation of real facts** — it names the table above's already-documented real difference at the point in the run where it is observable (e.g. the callout for the calling-convention program fires right after each machine's call instruction), never a new claim about any architecture |

## Explicitly out of scope for phase 11

- **No new instructions, registers or peripherals** on any of the three
  architectures — phase 11 adds no row to any of the three opcode tables.
- **No cross-architecture binary compatibility or translation** — the three
  programs in a comparison set are hand-written per architecture, not
  generated from one source.
- **No synchronized Run**, only synchronized Step — phases 1-10 already
  decided PubVM has no Pause (`README.md`, "One absence... is deliberate");
  running three machines unattended in lockstep would need exactly the timer
  Kof's JS UI runtime does not have. Run still exists per-machine, independently.
- **No new export or hardware-targeting concerns** — those are phase 12's.

## Tests

Stage A: one test file per new tab, following the existing UI-adjacent
pattern (`tests/explain_test.kf`'s shape) — asserting the panel/explanation
content against known machine states, not exercising the UI toolkit itself.
Stage B: one test file per comparison program, asserting that each of the
three sources in a set assembles, runs, and reaches the documented real
difference (e.g. the overflow program's test asserts all three machines'
flags end up in the states the table above claims).
