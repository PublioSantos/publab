[English](pubvm.md) | [Português](pubvm.pt_BR.md)

# PubVM — a máquina

A PubVM é a máquina virtual educacional criada para o PubLab. Existe **uma**
implementação; PubVM-8, PubVM-16 e PubVM-32 são essa implementação com um
`wordSize` diferente. As fases 1-2 expõem e validam a configuração de 8 bits.

```kof
record MachineConfig(String name, Int wordSize, Int memorySize, Int addressBits, Int entryPoint)

MachineConfig pubvm8() { return MachineConfig("PubVM-8", 8, 65536, 16, 0) }
```

## Palavra

Os valores são carregados internamente em um `Long` de 64 bits para que uma
palavra de 32 bits sem sinal ainda caiba exatamente. Toda escrita em
registrador passa pelo tamanho da palavra:

| wordSize | faixa | máscara |
|---|---|---|
| 8 | 0..255 | 0xFF |
| 16 | 0..65535 | 0xFFFF |
| 32 | 0..4294967295 | 0xFFFFFFFF |

Valores negativos são complemento de dois: em 8 bits, `-6` é guardado como
`250`, e `250` lido com sinal é `-6`. O `Word.kf` é o único lugar onde isso é
decidido.

## Memória

```
MEMORY_SIZE  = 65536 bytes (64 KB)
ADDRESS_SIZE = 16 bits
```

A memória é **endereçável por byte**: os endereços 0x0000..0xFFFF guardam um
byte cada. Uma palavra ocupa `wordSize / 8` bytes consecutivos, guardados em
**little-endian** (byte menos significativo no endereço mais baixo). Na
PubVM-8 uma palavra é um byte; na PubVM-16 o valor 270 no endereço 8 é `0E` em
8 e `01` em 9.

Um acesso fora da memória é um erro com mensagem, nunca um wrap silencioso.

## Registradores

O Basic Mode tem quatro registradores gerais, todos do tamanho da palavra:

| id | nome |
|---|---|
| 0 | A |
| 1 | B |
| 2 | C |
| 3 | D |

O `PC` é mantido pela própria máquina, não pelo register file: ele é um
**endereço**, então segue o tamanho de endereço (16 bits) e não o tamanho da
palavra.

`X`, `Y`, `SP` e `FP` pertencem ao Advanced Mode (fase 8) e **não estão
implementados**. Os nomes são reservados para que o assembler possa dizer
isso.

## Flags

| flag | significado |
|---|---|
| C | carry para fora da palavra no ADD; borrow no SUB |
| Z | o resultado guardado é zero |
| N | o resultado guardado tem o bit de sinal ativo |
| O | overflow com sinal (complemento de dois) |

As flags são calculadas pelo execution engine, junto com o valor, em
`Alu.kf`. Nada mais no sistema calcula flag.

Exatamente quais instruções mexem em quais flags:

| instrução | C | Z | N | O |
|---|---|---|---|---|
| `ADD`, `SUB` | define | define | define | define |
| `AND`, `OR`, `XOR`, `NOT` | zera | define | define | zera |
| `LOAD`, `STORE`, `JMP`, `JZ`, `JC`, `PRINT`, `HALT` | não mexe | não mexe | não mexe | não mexe |

- **C no ADD** liga quando a soma verdadeira passa da máscara da palavra.
- **C no SUB** é borrow: liga quando o subtraendo é maior, comparado sem sinal.
- **O no ADD** liga quando os dois operandos têm o mesmo sinal e o sinal do
  resultado difere dele.
- **O no SUB** liga quando os operandos têm sinais diferentes e o sinal do
  resultado difere do sinal do minuendo.

## Conjunto de instruções — Basic Mode

```
LOAD  STORE  ADD  SUB  AND  OR  XOR  NOT  JMP  JZ  JC  PRINT  HALT
```

`PRINT` é uma **instrução educacional da PubVM**, não uma instrução física de
CPU (seção 13 da especificação). Ela acrescenta o valor guardado no
registrador, em decimal sem sinal, à saída da máquina.

O Advanced Mode (`PUSH`, `POP`, `CALL`, `RET`, shifts, rotates, `JN`, `JO`,
`JNZ`, `JNC`, `ENTER`, `LEAVE`) **não está implementado**.

## Encoding

O programa é realmente montado na memória e o `PC` é um endereço de memória
real, então a visão de memória do laboratório mostra código de máquina, e não
zeros.

Um byte de opcode, depois os operandos. O nibble alto é o grupo da operação e
os bits baixos selecionam a forma dos operandos, o que mantém um dump de
memória legível. `W` = `wordSize / 8`, `A` = `addressBits / 8` (2).

| opcode | instrução | layout | tamanho |
|---|---|---|---|
| `0x00` | `HALT` | `op` | 1 |
| `0x10` | `LOAD reg, imm` | `op reg imm:W` | 2+W |
| `0x11` | `LOAD reg, reg` | `op reg reg` | 3 |
| `0x12` | `LOAD reg, [addr]` | `op reg addr:A` | 2+A |
| `0x18` | `STORE [addr], reg` | `op addr:A reg` | 2+A |
| `0x20` | `ADD reg, imm` | `op reg imm:W` | 2+W |
| `0x21` | `ADD reg, reg` | `op reg reg` | 3 |
| `0x28` | `SUB reg, imm` | `op reg imm:W` | 2+W |
| `0x29` | `SUB reg, reg` | `op reg reg` | 3 |
| `0x30` | `AND reg, imm` | `op reg imm:W` | 2+W |
| `0x31` | `AND reg, reg` | `op reg reg` | 3 |
| `0x38` | `OR reg, imm` | `op reg imm:W` | 2+W |
| `0x39` | `OR reg, reg` | `op reg reg` | 3 |
| `0x40` | `XOR reg, imm` | `op reg imm:W` | 2+W |
| `0x41` | `XOR reg, reg` | `op reg reg` | 3 |
| `0x48` | `NOT reg` | `op reg` | 2 |
| `0x50` | `JMP addr` | `op addr:A` | 1+A |
| `0x51` | `JZ addr` | `op addr:A` | 1+A |
| `0x52` | `JC addr` | `op addr:A` | 1+A |
| `0x60` | `PRINT reg` | `op reg` | 2 |

Imediatos e endereços são little-endian. A largura do imediato segue o tamanho
da palavra, então **a mesma fonte produz uma imagem diferente na PubVM-8 e na
PubVM-16** — o que é parte do que o laboratório existe para mostrar.

O `Opcodes.kf` guarda essa tabela uma vez; o assembler codifica a partir dela
e o engine decodifica a partir dela, então os dois não podem divergir.

O programa do golden test monta em 12 bytes na PubVM-8:

```
LOAD A, 250    10 00 FA
LOAD B, 20     10 01 14
ADD  A, B      21 00 01
PRINT A        60 00
HALT           00
```

## Execução

```kof
machine.load(image)       // instala um programa e vai para READY
machine.reset()           // volta ao estado imediatamente após o load
machine.step()            // exatamente uma instrução
machine.run(maxCycles)    // até HALT, falha, pause ou o orçamento
machine.requestPause()
machine.halt()
machine.snapshot()        // uma leitura completa e imutável do estado
```

Status: `READY`, `RUNNING`, `PAUSED`, `HALTED`, `ERROR`.

- `step()` executa uma instrução e deixa a máquina `PAUSED`, pronta para a
  próxima.
- `run(maxCycles)` é limitado de propósito: um programa pode entrar em laço
  infinito. Se retorna com status `PAUSED`, o programa **não terminou** — o
  orçamento acabou ou houve pedido de pause. Chamar `run` de novo retoma.
- `requestPause()` é consumido pela execução que ele interrompe, então nunca
  envenena a próxima.
- No `HALT`, o `PC` fica **sobre** a instrução HALT: a máquina parou ali.
- Um opcode desconhecido ou um acesso fora da memória põe o status em `ERROR`
  com a mensagem em `errorMessage`. A máquina não quebra e não continua.
- `reset()` reescreve a memória a partir da imagem do programa, então tudo o
  que o programa escreveu na memória é desfeito.

O `snapshot()` devolve um record `MachineState` — registradores, flags, PC,
ciclos, status, saída e o texto da instrução atual. A instrução atual é
**desmontada a partir dos bytes que estão na memória**, não lembrada da fonte,
então o que aparece é o que a máquina vai executar de verdade.
