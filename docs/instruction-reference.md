[English](instruction-reference.md) | [Português](instruction-reference.pt_BR.md)

# Instruction Reference

Quick reference for every mnemonic each assembler accepts.
For the full specification of each instruction — flag behaviour, encoding,
memory layout, real vs. simplified — see the architecture-specific documents
linked at the top of each section.

---

## PubASM (PubVM-8 / PubVM-16 / PubVM-32)

Full spec: [pubasm.md](pubasm.md) · [pubvm.md](pubvm.md)

Registers: `A` `B` `C` `D` · Advanced Mode adds `X` `Y`  
`SP` and `FP` are reserved; managed by the stack instructions only.

### Basic Mode

| mnemonic | accepted forms | what it does |
|---|---|---|
| `LOAD` | `LOAD r, imm` · `LOAD r, r` · `LOAD r, [addr]` | copy value into register |
| `STORE` | `STORE [addr], r` | write register to memory |
| `ADD` | `ADD r, imm` · `ADD r, r` | add; sets Z C O N |
| `SUB` | `SUB r, imm` · `SUB r, r` | subtract; sets Z C O N |
| `AND` | `AND r, imm` · `AND r, r` | bitwise AND; sets Z N, clears C O |
| `OR` | `OR r, imm` · `OR r, r` | bitwise OR; sets Z N, clears C O |
| `XOR` | `XOR r, imm` · `XOR r, r` | bitwise XOR; sets Z N, clears C O |
| `NOT` | `NOT r` | bitwise NOT; sets Z N |
| `JMP` | `JMP label` · `JMP addr` | unconditional jump |
| `JZ` | `JZ label` · `JZ addr` | jump if Z set |
| `JC` | `JC label` · `JC addr` | jump if C set |
| `PRINT` | `PRINT r` | output register value (educational, not a real CPU instruction) |
| `HALT` | `HALT` | stop execution (educational) |

### Advanced Mode

| mnemonic | accepted forms | what it does |
|---|---|---|
| `PUSH` | `PUSH r` | decrement SP, write register at SP |
| `POP` | `POP r` | read at SP into register, increment SP |
| `CALL` | `CALL label` · `CALL addr` | push return address, jump |
| `RET` | `RET` | pop return address, jump |
| `ENTER` | `ENTER` | push FP, set FP = SP (open a stack frame) |
| `LEAVE` | `LEAVE` | restore SP = FP, pop FP (close a stack frame) |
| `SHL` | `SHL r, imm` · `SHL r, r` | logical shift left |
| `SHR` | `SHR r, imm` · `SHR r, r` | logical shift right |
| `ROL` | `ROL r, imm` · `ROL r, r` | rotate left |
| `ROR` | `ROR r, imm` · `ROR r, r` | rotate right |
| `JN` | `JN label` · `JN addr` | jump if N set |
| `JO` | `JO label` · `JO addr` | jump if O set |
| `JNZ` | `JNZ label` · `JNZ addr` | jump if Z clear |
| `JNC` | `JNC label` · `JNC addr` | jump if C clear |

### Number literals

`42` · `0x2A` · `0b101010` · `-6`  
Accepted range per word width: 8-bit `-128..255`, 16-bit `-32768..65535`,
32-bit `-2147483648..4294967295`.

---

## 8051 Assembler

Full spec: [8051.md](8051.md)

Registers: `A` `B` `R0`–`R7` `DPTR` · `SP` managed by stack instructions  
Peripheral (stage B): `P0` · `P1`–`P3` reserved, not yet implemented

> ⚠️ Real 8051 spellings — these are **not** the same mnemonics as PubASM.
> `SUBB` (not `SUB`), `ANL`/`ORL`/`XRL` (not `AND`/`OR`/`XOR`), and there
> is no borrow-less subtract on real hardware.

| mnemonic | accepted forms | what it does |
|---|---|---|
| `MOV` | `MOV r, #imm` · `MOV r, r` · `MOV r, direct` · `MOV direct, r` | move/copy |
| `ADD` | `ADD A, r` · `ADD A, #imm` | add to A; sets C AC OV P |
| `ADDC` | `ADDC A, r` · `ADDC A, #imm` | add with carry; sets C AC OV P |
| `SUBB` | `SUBB A, r` · `SUBB A, #imm` | subtract with borrow; sets C AC OV P |
| `ANL` | `ANL A, r` · `ANL A, #imm` | bitwise AND into A; updates P only |
| `ORL` | `ORL A, r` · `ORL A, #imm` | bitwise OR into A; updates P only |
| `XRL` | `XRL A, r` · `XRL A, #imm` | bitwise XOR into A; updates P only |
| `INC` | `INC r` | increment; updates P when operand is A |
| `DEC` | `DEC r` | decrement; updates P when operand is A |
| `JZ` | `JZ label` | jump if A == 0 (tests A live, not a flag) |
| `JNZ` | `JNZ label` | jump if A ≠ 0 (same) |
| `JC` | `JC label` | jump if C set |
| `JNC` | `JNC label` | jump if C clear |
| `JMP` | `JMP label` | unconditional jump (educational simplification of AJMP/LJMP/SJMP) |
| `CALL` | `CALL label` | push return address, jump (simplification of ACALL/LCALL) |
| `RET` | `RET` | return from call |
| `PUSH` | `PUSH r` | SP++, write at SP |
| `POP` | `POP r` | read at SP into register, SP-- |
| `PRINT` | `PRINT r` | output register value (educational, not a real 8051 instruction) |
| `HALT` | `HALT` | stop execution (educational, not a real 8051 instruction) |

`direct` is an Internal Data Memory address (0x00–0x7F).

---

## Cortex-M3 Assembler (Thumb subset)

Full spec: [cortex-m3.md](cortex-m3.md)

Low registers: `R0`–`R7`  
Special registers: `SP` (R13, managed by PUSH/POP) · `LR` (R14, set by BL) · `PC` (R15)  
Peripheral (stage B): `GPIOA` — reachable only via `MOV`

> ⚠️ ARM register naming (`R0`–`R7`), ARM mnemonics (`ORR`/`EOR`, not
> `OR`/`XOR`), three-operand arithmetic, and `CMP` sets flags without storing
> a result. `C` on subtraction is **NOT borrow** (opposite of PubVM and 8051).

| mnemonic | accepted forms | what it does |
|---|---|---|
| `MOV` | `MOV Rd, #imm` · `MOV Rd, Rm` | move; sets N Z |
| `ADD` | `ADD Rd, Rn, Rm` · `ADD Rd, Rn, #imm` | add; sets N Z C V |
| `SUB` | `SUB Rd, Rn, Rm` · `SUB Rd, Rn, #imm` | subtract; sets N Z C V (C = NOT borrow) |
| `AND` | `AND Rd, Rn, Rm` | bitwise AND; sets N Z |
| `ORR` | `ORR Rd, Rn, Rm` | bitwise OR; sets N Z |
| `EOR` | `EOR Rd, Rn, Rm` | bitwise XOR; sets N Z |
| `CMP` | `CMP Rn, Rm` · `CMP Rn, #imm` | sets N Z C V from `Rn - Rm`; **result is discarded** |
| `LDR` | `LDR Rd, [Rn]` · `LDR Rd, [Rn, #imm]` | load from memory |
| `STR` | `STR Rd, [Rn]` · `STR Rd, [Rn, #imm]` | store to memory |
| `B` | `B label` | unconditional branch |
| `BEQ` | `BEQ label` | branch if Z set (equal) |
| `BNE` | `BNE label` | branch if Z clear (not equal) |
| `BCS` | `BCS label` | branch if C set (carry set / unsigned higher-or-same) |
| `BCC` | `BCC label` | branch if C clear (carry clear / unsigned lower) |
| `BMI` | `BMI label` | branch if N set (minus / negative) |
| `BPL` | `BPL label` | branch if N clear (plus / non-negative) |
| `BVS` | `BVS label` | branch if V set (overflow) |
| `BVC` | `BVC label` | branch if V clear (no overflow) |
| `BL` | `BL label` | branch with link: `LR = return address`, `PC = label`; **does not touch the stack** |
| `BX` | `BX LR` | branch to `LR` (return); only the `LR` form is implemented |
| `PUSH` | `PUSH {R0, R2, LR, …}` | push register list (full-descending; written in increasing register order) |
| `POP` | `POP {R0, R2, PC, …}` | pop register list; `PC` in the list returns to the caller |
| `PRINT` | `PRINT Rd` | output register value (educational, not a real Thumb instruction) |
| `HALT` | `HALT` | stop execution (educational, not a real Thumb instruction) |

### Key differences from PubASM at a glance

| feature | PubASM | 8051 ASM | Cortex-M3 ASM |
|---|---|---|---|
| subtract | `SUB r, r` | `SUBB A, r` (with borrow) | `SUB Rd, Rn, Rm` (three operands) |
| bitwise OR | `OR r, r` | `ORL A, r` | `ORR Rd, Rn, Rm` |
| bitwise XOR | `XOR r, r` | `XRL A, r` | `EOR Rd, Rn, Rm` |
| conditional jump on zero | `JZ` (reads Z flag) | `JZ` (tests A live) | `BEQ` (reads Z flag) |
| subroutine call | `CALL addr` | `CALL addr` | `BL label` (LR, no stack) |
| return | `RET` | `RET` | `BX LR` or `POP {…, PC}` |
| PUSH/POP operand | one register | one register | register list `{R0, LR, …}` |
