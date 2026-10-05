[English](instruction-reference.md) | [Português](instruction-reference.pt_BR.md)

# Referência de Instruções

Referência rápida de todos os mnemônicos que cada montador aceita.
Para a especificação completa de cada instrução — comportamento de flags,
encoding, layout de memória, real vs. simplificado — consulte os documentos
de arquitetura específicos com link no topo de cada seção.

---

## PubASM (PubVM-8 / PubVM-16 / PubVM-32)

Especificação completa: [pubasm.pt_BR.md](pubasm.pt_BR.md) · [pubvm.pt_BR.md](pubvm.pt_BR.md)

Registradores: `A` `B` `C` `D` · Advanced Mode adiciona `X` `Y`  
`SP` e `FP` são reservados; gerenciados apenas pelas instruções de pilha.

### Basic Mode

| mnemônico | formas aceitas | o que faz |
|---|---|---|
| `LOAD` | `LOAD r, imm` · `LOAD r, r` · `LOAD r, [addr]` | copia valor para o registrador |
| `STORE` | `STORE [addr], r` | escreve registrador na memória |
| `ADD` | `ADD r, imm` · `ADD r, r` | soma; atualiza Z C O N |
| `SUB` | `SUB r, imm` · `SUB r, r` | subtrai; atualiza Z C O N |
| `AND` | `AND r, imm` · `AND r, r` | AND bit a bit; atualiza Z N, zera C O |
| `OR` | `OR r, imm` · `OR r, r` | OR bit a bit; atualiza Z N, zera C O |
| `XOR` | `XOR r, imm` · `XOR r, r` | XOR bit a bit; atualiza Z N, zera C O |
| `NOT` | `NOT r` | NOT bit a bit; atualiza Z N |
| `JMP` | `JMP label` · `JMP addr` | salto incondicional |
| `JZ` | `JZ label` · `JZ addr` | salta se Z ligado |
| `JC` | `JC label` · `JC addr` | salta se C ligado |
| `PRINT` | `PRINT r` | exibe valor do registrador (instrução educacional, não é instrução real de CPU) |
| `HALT` | `HALT` | encerra a execução (instrução educacional) |

### Advanced Mode

| mnemônico | formas aceitas | o que faz |
|---|---|---|
| `PUSH` | `PUSH r` | decrementa SP, escreve registrador em SP |
| `POP` | `POP r` | lê em SP para registrador, incrementa SP |
| `CALL` | `CALL label` · `CALL addr` | empilha endereço de retorno, salta |
| `RET` | `RET` | desempilha endereço de retorno, salta |
| `ENTER` | `ENTER` | empilha FP, faz FP = SP (abre um stack frame) |
| `LEAVE` | `LEAVE` | restaura SP = FP, desempilha FP (fecha um stack frame) |
| `SHL` | `SHL r, imm` · `SHL r, r` | shift lógico à esquerda |
| `SHR` | `SHR r, imm` · `SHR r, r` | shift lógico à direita |
| `ROL` | `ROL r, imm` · `ROL r, r` | rotação à esquerda |
| `ROR` | `ROR r, imm` · `ROR r, r` | rotação à direita |
| `JN` | `JN label` · `JN addr` | salta se N ligado |
| `JO` | `JO label` · `JO addr` | salta se O ligado |
| `JNZ` | `JNZ label` · `JNZ addr` | salta se Z desligado |
| `JNC` | `JNC label` · `JNC addr` | salta se C desligado |

### Literais numéricos

`42` · `0x2A` · `0b101010` · `-6`  
Faixa aceita por largura de palavra: 8 bits `-128..255`, 16 bits `-32768..65535`,
32 bits `-2147483648..4294967295`.

---

## Montador 8051

Especificação completa: [8051.pt_BR.md](8051.pt_BR.md)

Registradores: `A` `B` `R0`–`R7` `DPTR` · `SP` gerenciado pelas instruções de pilha  
Periférico (stage B): `P0` · `P1`–`P3` reservados, ainda não implementados

> ⚠️ Ortografia real do 8051 — **não** são os mesmos mnemônicos do PubASM.
> `SUBB` (não `SUB`), `ANL`/`ORL`/`XRL` (não `AND`/`OR`/`XOR`), e não
> existe subtração sem borrow no hardware real.

| mnemônico | formas aceitas | o que faz |
|---|---|---|
| `MOV` | `MOV r, #imm` · `MOV r, r` · `MOV r, direct` · `MOV direct, r` | move/copia |
| `ADD` | `ADD A, r` · `ADD A, #imm` | soma em A; atualiza C AC OV P |
| `ADDC` | `ADDC A, r` · `ADDC A, #imm` | soma com carry; atualiza C AC OV P |
| `SUBB` | `SUBB A, r` · `SUBB A, #imm` | subtrai com borrow; atualiza C AC OV P |
| `ANL` | `ANL A, r` · `ANL A, #imm` | AND bit a bit em A; atualiza apenas P |
| `ORL` | `ORL A, r` · `ORL A, #imm` | OR bit a bit em A; atualiza apenas P |
| `XRL` | `XRL A, r` · `XRL A, #imm` | XOR bit a bit em A; atualiza apenas P |
| `INC` | `INC r` | incrementa; atualiza P quando operando é A |
| `DEC` | `DEC r` | decrementa; atualiza P quando operando é A |
| `JZ` | `JZ label` | salta se A == 0 (testa A ao vivo, não uma flag) |
| `JNZ` | `JNZ label` | salta se A ≠ 0 (idem) |
| `JC` | `JC label` | salta se C ligado |
| `JNC` | `JNC label` | salta se C desligado |
| `JMP` | `JMP label` | salto incondicional (simplificação educacional de AJMP/LJMP/SJMP) |
| `CALL` | `CALL label` | empilha endereço de retorno, salta (simplificação de ACALL/LCALL) |
| `RET` | `RET` | retorno de chamada |
| `PUSH` | `PUSH r` | SP++, escreve em SP |
| `POP` | `POP r` | lê em SP para registrador, SP-- |
| `PRINT` | `PRINT r` | exibe valor do registrador (instrução educacional, não é instrução real do 8051) |
| `HALT` | `HALT` | encerra a execução (instrução educacional, não é instrução real do 8051) |

`direct` é um endereço da Internal Data Memory (0x00–0x7F).

---

## Montador Cortex-M3 (subconjunto Thumb)

Especificação completa: [cortex-m3.pt_BR.md](cortex-m3.pt_BR.md)

Registradores baixos: `R0`–`R7`  
Registradores especiais: `SP` (R13, gerenciado por PUSH/POP) · `LR` (R14, preenchido por BL) · `PC` (R15)  
Periférico (stage B): `GPIOA` — acessível apenas via `MOV`

> ⚠️ Nomenclatura ARM (`R0`–`R7`), mnemônicos ARM (`ORR`/`EOR`, não
> `OR`/`XOR`), aritmética com três operandos, e `CMP` atualiza flags sem
> armazenar resultado. `C` na subtração é **NOT borrow** (oposto do PubVM e do 8051).

| mnemônico | formas aceitas | o que faz |
|---|---|---|
| `MOV` | `MOV Rd, #imm` · `MOV Rd, Rm` | move; atualiza N Z |
| `ADD` | `ADD Rd, Rn, Rm` · `ADD Rd, Rn, #imm` | soma; atualiza N Z C V |
| `SUB` | `SUB Rd, Rn, Rm` · `SUB Rd, Rn, #imm` | subtrai; atualiza N Z C V (C = NOT borrow) |
| `AND` | `AND Rd, Rn, Rm` | AND bit a bit; atualiza N Z |
| `ORR` | `ORR Rd, Rn, Rm` | OR bit a bit; atualiza N Z |
| `EOR` | `EOR Rd, Rn, Rm` | XOR bit a bit; atualiza N Z |
| `CMP` | `CMP Rn, Rm` · `CMP Rn, #imm` | atualiza N Z C V com `Rn - Rm`; **resultado é descartado** |
| `LDR` | `LDR Rd, [Rn]` · `LDR Rd, [Rn, #imm]` | carrega da memória |
| `STR` | `STR Rd, [Rn]` · `STR Rd, [Rn, #imm]` | armazena na memória |
| `B` | `B label` | branch incondicional |
| `BEQ` | `BEQ label` | branch se Z ligado (igual) |
| `BNE` | `BNE label` | branch se Z desligado (diferente) |
| `BCS` | `BCS label` | branch se C ligado (carry set / unsigned ≥) |
| `BCC` | `BCC label` | branch se C desligado (carry clear / unsigned <) |
| `BMI` | `BMI label` | branch se N ligado (negativo) |
| `BPL` | `BPL label` | branch se N desligado (não-negativo) |
| `BVS` | `BVS label` | branch se V ligado (overflow) |
| `BVC` | `BVC label` | branch se V desligado (sem overflow) |
| `BL` | `BL label` | branch com link: `LR = endereço de retorno`, `PC = label`; **não toca a pilha** |
| `BX` | `BX LR` | branch para `LR` (retorno); apenas a forma com `LR` é implementada |
| `PUSH` | `PUSH {R0, R2, LR, …}` | empilha lista de registradores (full-descending; escritos em ordem crescente) |
| `POP` | `POP {R0, R2, PC, …}` | desempilha lista de registradores; `PC` na lista retorna ao chamador |
| `PRINT` | `PRINT Rd` | exibe valor do registrador (instrução educacional, não é Thumb real) |
| `HALT` | `HALT` | encerra a execução (instrução educacional, não é Thumb real) |

### Diferenças principais em relação ao PubASM

| característica | PubASM | Montador 8051 | Montador Cortex-M3 |
|---|---|---|---|
| subtração | `SUB r, r` | `SUBB A, r` (com borrow) | `SUB Rd, Rn, Rm` (três operandos) |
| OR bit a bit | `OR r, r` | `ORL A, r` | `ORR Rd, Rn, Rm` |
| XOR bit a bit | `XOR r, r` | `XRL A, r` | `EOR Rd, Rn, Rm` |
| salto condicional em zero | `JZ` (lê flag Z) | `JZ` (testa A ao vivo) | `BEQ` (lê flag Z) |
| chamada de sub-rotina | `CALL addr` | `CALL addr` | `BL label` (usa LR, não empilha) |
| retorno | `RET` | `RET` | `BX LR` ou `POP {…, PC}` |
| operando de PUSH/POP | um registrador | um registrador | lista `{R0, LR, …}` |
