[English](pubasm.md) | [Português](pubasm.pt_BR.md)

# PubASM — a linguagem

PubASM é a linguagem assembly educacional do PubLab. Uma instrução por linha.
Mnemônicos e nomes de registradores são **insensíveis a maiúsculas**; nomes de
label são **sensíveis a maiúsculas**.

```asm
; overflow.pasm
    LOAD A, 250
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
```

## Linhas

```asm
label:                  ; um label em linha própria
label: LOAD A, 1        ; ou dividindo a linha com uma instrução
    LOAD A, 1           ; a indentação é livre
; comentário
// também é comentário
```

Um label aponta para a instrução que vem depois dele. Um label na linha após a
última instrução aponta um byte além do programa, o que é um destino de salto
válido (útil como saída de laço).

## Números

| forma | exemplo |
|---|---|
| decimal | `42` |
| hexadecimal | `0x2A`, `0X2a` |
| binário | `0b101010` |
| negativo | `-6` |

Um imediato negativo é guardado em complemento de dois: na PubVM-8, `-6` fica
`250`. Um imediato é aceito quando cabe na palavra da máquina como valor sem
sinal ou com sinal — em 8 bits, de `-128` a `255`.

## Operandos

| operando | significado |
|---|---|
| `A` `B` `C` `D` | um registrador |
| `250` | um valor imediato |
| `[0x80]` | o endereço de memória 0x80 |
| `[total]` | o endereço de memória do label `total` |
| `loop` | um label, como destino de salto |

Os nomes `X`, `Y`, `SP` e `FP` são **reservados** para o Advanced Mode
(fase 8), em qualquer caixa, e nunca são lidos como nome de label.

## Instruções — Basic Mode

| instrução | formas |
|---|---|
| `LOAD` | `LOAD r, imm` · `LOAD r, r` · `LOAD r, [addr]` |
| `STORE` | `STORE [addr], r` |
| `ADD` `SUB` `AND` `OR` `XOR` | `op r, imm` · `op r, r` |
| `NOT` | `NOT r` |
| `JMP` `JZ` `JC` | `op addr` (um label ou um número) |
| `PRINT` | `PRINT r` |
| `HALT` | `HALT` |

Quais flags cada instrução altera está em [pubvm.pt_BR.md](pubvm.pt_BR.md).

O Advanced Mode (`PUSH`, `POP`, `CALL`, `RET`, `SHL`, `SHR`, `ROL`, `ROR`,
`JN`, `JO`, `JNZ`, `JNC`, `ENTER`, `LEAVE`) **não está implementado**. O
assembler reconhece esses mnemônicos e os rejeita com `ASM010`, dizendo que
pertencem ao Advanced Mode — não com "instrução desconhecida".

Note que o conjunto do Basic Mode **não tem `JNZ`**, então um laço de contagem
decrescente testa zero e sai, depois volta com um salto incondicional — veja
[examples/loops.pasm](../examples/loops.pasm).

## Diagnostics

Um diagnóstico carrega um **código e argumentos**, nunca uma frase pronta: o
texto é produzido na hora, no idioma pedido. `Messages.kf` é o único arquivo
com texto traduzível, então acrescentar um idioma mexe em um arquivo só.

```
Line 1, column 9: error [ASM005]: immediate 300 does not fit in a 8-bit word
  Valid range for 8 bits: -128 to 255.

Linha 1, coluna 9: erro [ASM005]: o imediato 300 não cabe em uma palavra de 8 bits
  Faixa válida para 8 bits: -128 a 255.
```

| código | significado |
|---|---|
| `ASM001` | instrução desconhecida |
| `ASM002` | forma de operando inválida para esta instrução (lista as formas aceitas) |
| `ASM003` | número errado de operandos |
| `ASM004` | registrador desconhecido |
| `ASM005` | o imediato não cabe na palavra da máquina |
| `ASM006` | label não definido |
| `ASM007` | label duplicado (aponta a primeira definição) |
| `ASM008` | endereço fora da memória desta máquina |
| `ASM009` | caractere inesperado |
| `ASM010` | a instrução pertence ao Advanced Mode, ainda não implementado |
| `ASM011` | número malformado |
| `ASM012` | esperava uma coisa, encontrou outra (vírgula faltando, colchete aberto) |
| `ASM013` | o programa é maior que a memória da máquina |
| `ASM014` | o registrador pertence ao Advanced Mode, ainda não implementado |

Um nome solto é um label só onde a instrução aceita um endereço. Para uma
instrução que não aceita — `LOAD Q, 1` — o nome só pode ter sido um
registrador escrito errado, e é isso que o `ASM004` diz.

Uma linha ruim produz **um** diagnóstico: o resto da linha é descartado para
que um erro só não vire cascata.

## Montando

```kof
val result = assembleSource(source, pubvm8())
if (result.ok()) {
    machine.load(result.image())
} else {
    println(renderDiagnostics(result.diagnostics(), "pt"))
}
```

O `AssemblyResult` carrega a imagem, a contagem de bytes, os diagnósticos, a
tabela de símbolos e um **source map** (endereço → linha) — que é o que vai
permitir ao debugger destacar a linha em que a máquina está (fase 6).

Em caso de falha a imagem volta **vazia**, então um programa que não montou
nunca pode ser carregado por acidente.
