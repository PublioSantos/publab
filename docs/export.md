[English](export.md) | [Português](export.pt_BR.md)

# Export — scope

## Status: stage A done

This page is the scope for phase 12, written before any code, the same
discipline phases 8-11 used. Phase 12 is different from every phase before
it: it is not an architecture, and it is not a UI feature built on facts
already established — it is the one place where PubLab's own warning label
("not an emulator, not a development tool for real hardware") is directly
at stake, so the scope decision itself needs to be explicit rather than
assumed.

## The core tension, stated plainly

PubVM's, the 8051's and the Cortex-M3's opcode tables
(`publab/machine/Opcodes.kf`, `publab/i8051/Opcodes8051.kf`,
`publab/cm3/OpcodesM3.kf`) are **PubLab's own invented encodings**, chosen
for what is simple to teach from — not the real binary opcodes a real 8051
or Cortex-M3 part decodes. `docs/8051.md` and `docs/cortex-m3.md` say so
from their first paragraph, and `docs/cortex-m3.md` already names the
consequence: "Any future export to real hardware (phase 12) must state the
MCU and target explicitly."

That means **"export" cannot mean "produce a binary a real chip can run"**
without an entirely separate undertaking: a real encoder for one named,
specific part (e.g. a real AT89C51's actual instruction encoding, or a real
STM32F103's actual Thumb-2 encoding), built and verified against that part's
own datasheet — not derived from `Opcodes.kf`/`Opcodes8051.kf`/`OpcodesM3.kf`
at all, because those tables were never real to begin with. That is a
project roughly the size of phases 9 or 10 again, per architecture, and it
changes what PubLab is: a second, real toolchain living alongside the
educational one, for a named part, with its own correctness bar (a wrong
byte there is not a teaching simplification, it is a bug in something
someone might flash onto real silicon).

## What phase 12 actually scopes: two honest options

**Option A — a session export (recommended default).** PubLab exports what
it already has, honestly labelled as what it is: the PubASM/8051-asm/
Cortex-M3-asm source, the assembled bytes in PubLab's own format, the final
register/flag/memory state, and the explanation trail — as a text or JSON
file the student can save, print, or hand to an instructor. No claim of
hardware compatibility anywhere in it; the file's own header repeats the
warning label. This is a UI/IO feature on top of what already exists
(`MachineState`/`MachineState8051`/`MachineStateM3`'s `snapshot()`), not a
new encoder, and fits the size of a normal stage.

**Option B — a real binary export for one named MCU.** A second, genuinely
real encoder for a specific, named part, built from that part's own
datasheet, kept entirely separate from the educational opcode tables, with
its own Rule 7 scope document, its own test suite verified against known-
good real assembly output, and its own explicit disclaimer scope (what
subset of the real part's instruction set it covers, since PubLab's
educational subset is already narrower than any real chip's). This is a
much larger undertaking — closer to a new phase 9/10 than a stage of phase
12 — and is **not** proposed as part of this page's scope.

This page proposes **Option A only** for phase 12. Option B, if ever
wanted, needs its own future scope document naming one specific real part,
written with the same care phases 9 and 10 gave the educational models —
real hardware export is not a feature to back into by extending the
teaching encoders.

## Stage A — the session export (Option A) — done

Implemented as `publab/ui/Export.kf`: one `Export` button per laboratory
(PubVM, 8051, Cortex-M3, and the comparison view), each filling a read-only
panel with the text block below. The source, the assembled-byte hex dump
(read back from the machine's own memory, not a second copy kept just for
this) and the final state all come straight from the same `snapshot()`/
`assembledSource` the rest of the UI already reads. No file-download API
exists in Kof's UI runtime, so the export is a selectable on-screen panel —
the student copies or saves it from there — rather than a browser download,
which this toolkit cannot trigger.

| item | real or abstraction |
|---|---|
| the exported source | **real** — exactly the text in the editor when exported, byte for byte |
| the exported assembled bytes | **real for PubLab's own format** — the actual output of `assembleSource`/`assembleSource8051`/`assembleSourceM3`, labelled explicitly as PubLab's educational encoding, not a real chip's |
| the exported register/flag/memory state | **real** — read from the same `snapshot()` the UI and tests already use, nothing re-derived |
| the file format itself | **educational/tooling choice** — plain text or JSON, PubLab's own, not a standard object/hex format (see "Explicitly out of scope") |

Contents of one export, per machine the student had assembled (PubVM,
8051, Cortex-M3, or the comparison view's set — whichever the export was
taken from):

```
PubLab export — <machine name> — <ISO 8601 timestamp>
PubLab's own educational encoding — NOT a real <architecture>'s binary
opcodes. See docs/<page>.md. Never flash this onto real hardware.

--- source ---
<the exact PubASM/8051-asm/Cortex-M3-asm text>

--- assembled bytes (PubLab's own format) ---
<hex dump, same rendering the memory panel already uses>

--- final state ---
<registers, flags, cycles, status, output — the same fields snapshot() carries>
```

The warning paragraph is not optional and not shortenable — it is the one
line standing between "a teaching tool's save file" and "something that
looks like it came off a real toolchain," and it goes in both languages the
UI already supports.

## Explicitly out of scope for phase 12

- **Any binary a real chip could execute** — see "The core tension" above;
  that is Option B, not proposed here.
- **Industry-standard object formats** (Intel HEX, SREC, ELF) — those
  formats carry an implicit claim of hardware-targetability that PubLab's
  own encoding does not meet; a plain hex dump in a text file makes no such
  claim.
- **Import** — phase 12 is export only; reading a `.hex`/`.elf` file back in
  is a different, unrequested feature.
- **Any change to the three educational opcode tables** — phase 12 adds no
  instruction, register or peripheral to any architecture.

## Tests

One test file per machine's export (`tests/export_test.kf` or split per
architecture), asserting the exported text contains the real source
verbatim, the real assembled byte count, the real final register/flag
values from a known program — and that the warning paragraph is present in
both languages. The same "built from real state, not re-derived" rule every
other phase 7/11 explanation panel already follows.
