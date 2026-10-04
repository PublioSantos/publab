[English](pubasm.md) | [Português](pubasm.pt_BR.md)

# PubASM — the language

PubASM is the educational assembly language of PubLab. One instruction per
line. Mnemonics and register names are **case-insensitive**; label names are
**case-sensitive**.

```asm
; overflow.pasm
    LOAD A, 250
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
```

## Lines

```asm
label:                  ; a label on its own line
label: LOAD A, 1        ; or sharing a line with an instruction
    LOAD A, 1           ; indentation is free
; comment
// also a comment
```

A label points at the instruction that follows it. A label on the line after
the last instruction points one byte past the program, which is a legal jump
target (useful as a loop exit).

## Numbers

| form | example |
|---|---|
| decimal | `42` |
| hexadecimal | `0x2A`, `0X2a` |
| binary | `0b101010` |
| negative | `-6` |

A negative immediate is stored in two's complement: on PubVM-8, `-6` becomes
`250`. An immediate is accepted when it fits the machine's word either as an
unsigned or as a signed value — on 8 bits, `-128` to `255`; on 16 bits,
`-32768` to `65535`; on 32 bits, `-2147483648` to `4294967295`.

A value outside the machine's word is `ASM005`, which names the word and the
valid range. Only a literal beyond `999999999999` — far above any variant's
word — is rejected earlier, by the lexer, as `ASM011`; that limit exists so
the accumulator cannot overflow silently, and it is deliberately high enough
that the word check owns every realistic mistake.

## Operands

| operand | meaning |
|---|---|
| `A` `B` `C` `D` | a register |
| `250` | an immediate value |
| `[0x80]` | the memory address 0x80 |
| `[total]` | the memory address of the label `total` |
| `loop` | a label, as a jump target |

The names `X`, `Y`, `SP` and `FP` are **reserved** for Advanced Mode
(phase 8), in any letter case, and are never read as label names.

## Instructions — Basic Mode

| instruction | forms |
|---|---|
| `LOAD` | `LOAD r, imm` · `LOAD r, r` · `LOAD r, [addr]` |
| `STORE` | `STORE [addr], r` |
| `ADD` `SUB` `AND` `OR` `XOR` | `op r, imm` · `op r, r` |
| `NOT` | `NOT r` |
| `JMP` `JZ` `JC` | `op addr` (a label or a number) |
| `PRINT` | `PRINT r` |
| `HALT` | `HALT` |

Which flags each instruction touches is in [pubvm.md](pubvm.md).

Advanced Mode (`PUSH`, `POP`, `CALL`, `RET`, `SHL`, `SHR`, `ROL`, `ROR`, `JN`,
`JO`, `JNZ`, `JNC`, `ENTER`, `LEAVE`) is **not implemented**. The assembler
recognises those mnemonics and rejects them with `ASM010`, saying they belong
to Advanced Mode — not with "unknown instruction".

Note that the Basic Mode set has **no `JNZ`**, so a countdown loop tests for
zero and jumps out, then jumps back unconditionally — see
[examples/loops.pasm](../examples/loops.pasm).

## Diagnostics

A diagnostic carries a **code and arguments**, never a finished sentence: the
text is produced on demand in the requested language. `Messages.kf` is the
only file with translatable text, so adding a language touches one file.

```
Line 1, column 9: error [ASM005]: immediate 300 does not fit in a 8-bit word
  Valid range for 8 bits: -128 to 255.

Linha 1, coluna 9: erro [ASM005]: o imediato 300 não cabe em uma palavra de 8 bits
  Faixa válida para 8 bits: -128 a 255.
```

| code | meaning |
|---|---|
| `ASM001` | unknown instruction |
| `ASM002` | invalid operand shape for this instruction (lists the accepted forms) |
| `ASM003` | wrong number of operands |
| `ASM004` | unknown register |
| `ASM005` | immediate does not fit the machine's word |
| `ASM006` | undefined label |
| `ASM007` | duplicate label (names the first definition) |
| `ASM008` | address outside this machine's memory |
| `ASM009` | unexpected character |
| `ASM010` | the instruction belongs to Advanced Mode, not implemented yet |
| `ASM011` | malformed number |
| `ASM012` | expected one thing, found another (missing comma, unclosed bracket) |
| `ASM013` | the program is larger than the machine's memory |
| `ASM014` | the register belongs to Advanced Mode, not implemented yet |

A bare name is a label only where the instruction accepts an address. For an
instruction that does not — `LOAD Q, 1` — the name can only have been a
misspelled register, and that is what `ASM004` says.

One bad line produces **one** diagnostic: the rest of the line is dropped so a
single mistake does not cascade.

## Assembling

```kof
val result = assembleSource(source, pubvm8())
if (result.ok()) {
    machine.load(result.image())
} else {
    println(renderDiagnostics(result.diagnostics(), "en"))
}
```

`AssemblyResult` carries the image, the byte count, the diagnostics, the
symbol table and a **source map** (address → line) — which is what lets a
debugger highlight the line the machine is currently on (phase 6).

On failure the image comes back **empty**, so a program that did not assemble
can never be loaded by accident.
