[English](architecture.md) | [Português](architecture.pt_BR.md)

# Architecture

## Layers

```
┌─────────────────────────────┐
│             UI              │  phase 5   — not implemented
├─────────────────────────────┤
│      Educational Layer      │  phase 7   — not implemented
├─────────────────────────────┤
│       Debugger / State      │  phase 6   — MachineState exists; the
│                             │              debugger itself does not
├─────────────────────────────┤
│      Execution Engine       │  publab/machine/Engine.kf
├─────────────────────────────┤
│         Assembler           │  publab/assembler/
├─────────────────────────────┤
│   Architecture Interface    │  publab/machine/MachineConfig.kf + Opcodes.kf
├─────────────────────────────┤
│  PubVM / 8051 / Cortex-M3   │  PubVM only; the other two are phases 9-10
└─────────────────────────────┘
```

What is enforced today:

- The machine knows nothing about an interface. Nothing in `publab/machine`
  prints, formats for a screen or holds a UI concept.
- The machine knows nothing about **source code**. The current instruction is
  disassembled from the bytes in memory, not remembered from the assembler.
  Mapping an address back to a source line is the assembler's source map, and
  joining the two is the debugger's job (phase 6).
- The assembler knows nothing about an interface, and produces **codes**, not
  sentences: the language of a diagnostic is chosen when it is rendered.
- Flags are computed in one place, `Alu.kf`, together with the value.
- The instruction table lives once, in `Opcodes.kf`. The assembler encodes
  from it and the engine decodes from it (see the rule below).
- The word size is a configuration value. There is no `PubVM8` /`PubVM16` /
  `PubVM32` class — only `MachineConfig`.

## Architectural rule: one encoding, one definition

**There must never be an opcode table in the assembler and another in the
engine.** A single definition — `publab/machine/Opcodes.kf` — carries the whole
path:

```
PubASM
   ↓   Assembler   (encodes from the table)
bytes
   ↓
Memory
   ↓
PC
   ↓   Decoder     (decodes from the same table)
Execution
```

Everything downstream depends on this holding: the memory view shows real
machine code, the disassembly of the current instruction is read back out of
memory rather than remembered from the source, and the debugger (phase 6) can
trust that the bytes at PC mean exactly what the assembler wrote. A second
table would let the two halves drift apart silently — the kind of defect that
shows up as a laboratory teaching something false.

Adding an instruction means adding one row to `opcodeTable()`. If a change ever
requires editing an opcode number in two places, the change is wrong.

Because the machine is a plain Kof object with a `snapshot()`, it can be driven
headless: the whole test suite does exactly that, and a CLI or a UI is just
another caller.

## Directory layout

A directory **is** a package in Kof, so the tree is also the package tree.

```
publab/
├── kof.toml                 project manifest (makes the root the module root)
├── publab/
│   ├── app/                 product identity, incl. the Kof attribution
│   ├── machine/             PubVM: word, memory, registers, flags, ALU,
│   │                        opcode table, decoder, execution engine
│   └── assembler/           PubASM: lexer, parser, assembler, diagnostics
├── tests/                   one program per file, run by `kof test tests`
├── examples/                PubASM programs, executed by the test suite
└── docs/
```

## Tests

`kof test` compiles **each file independently** as its own program, so every
test file is self-contained and imports the packages it needs. Running the
whole suite:

```bash
kof test tests
```

The examples are part of the suite: `tests/examples_test.kf` reads each
`examples/*.pasm` from disk, assembles it for PubVM-8, runs it and asserts the
output. An example that stopped working would fail the build.

## Notes on building this in Kof

Written against **Kof 0.5.0-beta**. Decisions and workarounds worth knowing
before editing the code:

- **Values are `Long`, not `Int`.** An unsigned 32-bit word does not fit in a
  signed 32-bit `Int`, so registers, memory words and ALU results are `Long`.
  Memory *cells* are `Int` in 0..255.
- **Kof has no `~`.** Bit complement is `x ^ mask` (`aluNot`).
- **Kof has no long literal.** A wide constant is written `4294967295 as Long`.
- **Primitive types have no static fields** (`Int.MAX_VALUE` does not exist),
  so limits are computed from the word size instead.
- **A `throw` lives in its own function** (`memoryFault`, `registerFault`,
  `decodeFault`). The Kof JS backend has mishandled a `throw` nested inside an
  if/else chain, and the machine core is meant to compile to the JS target
  later for the UI.
- **Bitwise operators on `Long` are used for masking and the logic
  instructions.** The language specification marks bitwise semantics as
  unspecified across targets (SG-002), so they were verified on **both**
  targets before any UI work: `tests/js_parity_test.kf` runs the masks, the
  shifts, the logic operations above 2^31, the flags and the 32-bit memory
  word on `jvm` and on `js`, and the results are identical. SG-002 is not a
  problem for this core. The usage stays confined to `Word.kf`, `Alu.kf`,
  `Memory.kf` and one helper in `Assembler.kf`.
- **Two JS-target codegen defects shape how control flow is written here**,
  both found in phase 5A and documented with minimal repros in
  `notes/kof-compiler-findings.md`:
  - **Never put an early `return` inside an `if` nested in an `else` branch**
    when more statements follow it in that branch — the JS target drops the
    function's trailing `return` and the function yields `undefined`. Use a
    single exit point. (`resolveAddressOperand`, `parseMemoryOperand`.)
  - **Never guard an indexing expression with `&&` in the same condition** —
    `list.size > 0 && list.get(list.size - 1)` evaluates the right side on the
    JS target even when the left is false. Use a nested `if`. (Pass 1 of the
    assembler.)
- **`List<T>` of a package-local `record` cannot be annotated empty**
  (`var l: List<OpSpec> = listOf()` trips SEM010 inside its own package).
  Either seed the list with its first element, or spell the fully-qualified
  name once in a helper — which is what `emptyDiagnostics()`,
  `emptyTokens()` and friends are for.
- **Nullability narrowing only applies inside the `if`**, so a `String?` from
  `File.readText()` is used inside `if (source != null) { … }` rather than
  after an early return.
- **No sentinel returns.** A lookup that can fail returns a small record with
  a `found` flag (`OpLookup`, `RegisterLookup`, `SymbolLookup`, `LineLookup`),
  not `-1`.
