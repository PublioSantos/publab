[English](pubvm.md) | [Português](pubvm.pt_BR.md)

# PubVM — a máquina

A PubVM é a máquina virtual educacional criada para o PubLab. Existe **uma**
implementação; PubVM-8, PubVM-16 e PubVM-32 são essa implementação com um
`wordSize` diferente. As três estão implementadas e validadas: a suíte de
conformidade em `tests/matrix_test.kf` roda sobre cada variante devolvida por
`allMachines()`.

```kof
record MachineConfig(String name, Int wordSize, Int memorySize, Int addressBits, Int entryPoint)

MachineConfig pubvm8()  { return MachineConfig("PubVM-8",  8,  65536, 16, 0) }
MachineConfig pubvm16() { return MachineConfig("PubVM-16", 16, 65536, 16, 0) }
MachineConfig pubvm32() { return MachineConfig("PubVM-32", 32, 65536, 16, 0) }

List<MachineConfig> allMachines()   // as três, em ordem
```

O tamanho da memória e o tamanho de endereço são **os mesmos nas três**: só a
palavra muda. Palavra maior não significa mais memória — significa que cada
valor ocupa mais da memória que já existe.

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

`X` e `Y` pertencem ao Advanced Mode (fase 8, etapa A) e **estão
implementados**: mais dois registradores gerais do tamanho da palavra, ids 4
e 5, usáveis em qualquer lugar onde A-D também são.

`SP` e `FP` também pertencem ao Advanced Mode, e **ambos estão
implementados**, como endereços ao lado do `PC`, não como registradores do
tamanho da palavra (seção "Pilha" abaixo) — o `SP` precisa guardar
`memorySize`, um endereço além do topo da memória, o que não cabe numa
palavra de 8 ou 16 bits. O `FP` começa em 0 e é lido e escrito pelo
`ENTER`/`LEAVE` (ver "Endereços de retorno e frames" abaixo). Nenhum dos
dois é alcançável como registrador geral de operando — o assembler rejeita
`SP`/`FP` do mesmo jeito que sempre rejeitou qualquer nome do Advanced Mode,
com `ASM014`.

## Pilha

Advanced Mode, etapa A: `PUSH` e `POP`.

```
SP inicial = memorySize   (um endereço além do topo da memória — não é um endereço válido)
wordBytes  = wordSize / 8
```

A pilha cresce em direção aos endereços **menores**, a partir do topo da
memória. Um núcleo, uma regra, para os três tamanhos de palavra — não há
lógica de pilha por variante.

`PUSH reg`:
```
SP = SP - wordBytes
MEM[SP] = reg
```
verificado primeiro: se `SP - wordBytes < 0`, o push não tem espaço e a
máquina falha com `ERROR` ("stack overflow"), do mesmo jeito que um opcode
desconhecido ou um acesso de memória fora da faixa — nunca um wrap silencioso.

`POP reg`:
```
reg = MEM[SP]
SP = SP + wordBytes
```
verificado primeiro: se `SP >= memorySize`, nada foi empilhado e a máquina
falha com `ERROR` ("stack underflow").

`PUSH` e `POP` não tocam em nenhuma flag nem em nenhum registrador além do
próprio operando. O `reset()` devolve o `SP` para `memorySize` e o `FP` para
0, como qualquer outro pedaço de estado.

### Endereços de retorno e frames (etapa B)

`CALL`, `RET`, `ENTER` e `LEAVE` empilham e desempilham na mesma pilha que
`PUSH`/`POP` usam, através do mesmo `SP` e das mesmas verificações de
overflow/underflow — mas eles movem `addressBytes` (`addressBits / 8`, 2 em
todas as variantes) por vez, nunca `wordBytes`. Um endereço de retorno e um
frame pointer salvo são **localizações**, não dados: sua largura segue o
espaço de endereço de 16 bits em todas as variantes, o mesmo raciocínio que
mantém `SP` e `FP` fora do register file com wrap pela palavra. `PUSH A` na
PubVM-32 ainda move 4 bytes; `CALL` na PubVM-32 ainda move 2.

`CALL addr`:
```
SP = SP - addressBytes
MEM[SP] = PC_depois_do_CALL   ; o endereço da instrução logo após o CALL
PC = addr
```

`RET`:
```
PC = MEM[SP]
SP = SP + addressBytes
```

`ENTER` (prólogo clássico — ainda sem operando de tamanho de locals):
```
SP = SP - addressBytes
MEM[SP] = FP
FP = SP
```

`LEAVE` (o epílogo correspondente):
```
SP = FP                      ; descarta o que o frame empilhou acima do FP
FP = MEM[SP]
SP = SP + addressBytes
```

A pilha logo depois de um `CALL` seguido de um `ENTER`, endereços crescendo
para baixo:

```
endereços maiores
  [ endereço de retorno ]   <- SP logo após o CALL, FP ainda não se move
  [ FP salvo             ]   <- SP, e o FP agora aponta aqui, logo após o ENTER
   ...                          (futuras locals iriam abaixo desta linha)
endereços menores
```

O `LEAVE` desfaz exatamente isso (`SP = FP` primeiro, então o que uma função
chamada empilhou acima do próprio frame é descartado sem precisar
desempilhar valor por valor), deixando `SP` de volta onde estava logo após o
`CALL` — no endereço de retorno — então o `RET` seguinte desempilha
exatamente isso.

Uma chamada cujo `ENTER` nunca encontra um `LEAVE`, ou cujo `CALL` nunca
encontra um `RET`, ainda assim não corrompe memória: todo
`PUSH`/`POP`/`CALL`/`RET`/`ENTER`/`LEAVE` passa pela mesma verificação de
limites do `PUSH`/`POP` acima, então uma cadeia de chamadas desbalanceada
ainda cai na falha explícita de stack overflow em vez de crescer além do
endereço 0.

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
| `SHL`, `SHR`, `ROL`, `ROR` | define com o bit que saiu | define | define | zera |
| `LOAD`, `STORE`, `JMP`, `JZ`, `JC`, `JN`, `JO`, `JNZ`, `JNC`, `PUSH`, `POP`, `CALL`, `RET`, `ENTER`, `LEAVE`, `PRINT`, `HALT` | não mexe | não mexe | não mexe | não mexe |

### Z e N — idênticos nas seis instruções aritméticas e lógicas

```
ADD / SUB / AND / OR / XOR / NOT:
    Z = resultado guardado == 0
    N = bit de sinal do resultado guardado
```

Os dois são calculados sobre o resultado **guardado** — o valor depois do
truncamento para a palavra — nunca sobre o não truncado. Na PubVM-8,
`255 + 1` guarda `0`, então `Z = 1` mesmo que a soma verdadeira seja 256.

### C — carry no ADD, borrow no SUB

O significado de Carry numa subtração varia entre arquiteturas reais, então a
PubVM fixa uma definição simples e consistente:

```
ADD:  C = carry out
SUB:  C = borrow
```

- **C no ADD** liga quando a soma verdadeira passa da máscara da palavra.
- **C no SUB** liga quando o subtraendo é maior que o minuendo, comparado
  **sem sinal** — a subtração precisou pedir emprestado.

```
10 - 3 = 7          C = 0
3 - 10 = 249        C = 1    (PubVM-8,  256 - 7)
3 - 10 = 65529      C = 1    (PubVM-16, 65536 - 7)
```

### O — overflow com sinal

- **O no ADD** liga quando os dois operandos têm o mesmo sinal e o sinal do
  resultado difere dele.
- **O no SUB** liga quando os operandos têm sinais diferentes e o sinal do
  resultado difere do sinal do minuendo.

### C e O nas instruções lógicas

```
AND / OR / XOR / NOT:
    Z = resultado == 0
    N = bit de sinal do resultado
    C = 0
    O = 0
```

Não existe carry nem overflow com sinal numa operação bitwise, então os dois
são **zerados** em vez de ficarem intocados — um programa pode confiar no
valor deles depois de uma instrução lógica.

### Shifts e rotates (etapa C)

`SHL`, `SHR`, `ROL` e `ROR` têm as mesmas duas formas de `ADD`/`SUB`/`AND`/
`OR`/`XOR`: `op reg, imm` ou `op reg, reg` — o segundo operando é a
**contagem** de deslocamento ou rotação, não um segundo valor para combinar.
`Z` e `N` seguem a mesma regra de qualquer outra instrução
aritmética/lógica: calculados sobre o resultado guardado. `O` sempre zera,
pelo mesmo motivo das instruções bitwise — não existe conceito de overflow
com sinal num shift ou rotate.

`C` é o único bit que de fato atravessou a borda da palavra:

```
SHL reg, n:  C = bit (wordSize - n) de reg, ANTES do shift   (o bit mais alto que saiu)
             reg = reg << n                                   (preenchido com zero pelo lado baixo)

SHR reg, n:  C = bit (n - 1) de reg, ANTES do shift            (o bit mais baixo que saiu)
             reg = reg >>> n                                   (preenchido com zero pelo lado alto, sem sinal)

ROL reg, n:  C = bit (wordSize - n) de reg, ANTES do rotate    (o bit que se torna o novo bit 0)
             reg = reg rotacionado à esquerda por n

ROR reg, n:  C = bit (n - 1) de reg, ANTES do rotate            (o bit que se torna o novo bit mais alto)
             reg = reg rotacionado à direita por n
```

`n` é reduzido antes de ser usado: para `SHL`/`SHR`, contagem 0 é um no-op
(`C = 0`, nada se moveu) e contagem `>= wordSize` esvazia o registrador
inteiro (`C = 0` — com todo bit já sumido, não há um único "último bit que
saiu" para reportar). Para `ROL`/`ROR`, a contagem é tomada módulo
`wordSize`, já que rotacionar por uma palavra inteira é a identidade.

O shift é **sem sinal** (`SHR` nunca estende o sinal) — a PubVM não tem uma
instrução de shift com sinal separada; os registradores do Basic Mode já não
têm noção de sinal além da flag `N`, que é reconstruída a partir do padrão de
bits guardado do mesmo jeito que o `wordToSigned` faz para qualquer outra
instrução.

## Conjunto de instruções — Basic Mode

```
LOAD  STORE  ADD  SUB  AND  OR  XOR  NOT  JMP  JZ  JC  PRINT  HALT
```

`PRINT` é uma **instrução educacional da PubVM**, não uma instrução física de
CPU (seção 13 da especificação). Ela acrescenta o valor guardado no
registrador, em decimal sem sinal, à saída da máquina.

O Advanced Mode está totalmente implementado, nas três etapas que as
próprias notas descrevem: etapa A (`PUSH`, `POP`, e os registradores
`X`/`Y`/`SP`/`FP` — ver "Pilha" acima), etapa B (`CALL`, `RET`, `ENTER`,
`LEAVE` — ver "Endereços de retorno e frames" acima) e etapa C (`SHL`,
`SHR`, `ROL`, `ROR`, `JN`, `JO`, `JNZ`, `JNC` — ver "Shifts e rotates" acima
e a tabela de saltos condicionais abaixo).

### Saltos condicionais

```
JZ   addr   salta se Z == 1       JNZ  addr   salta se Z == 0
JC   addr   salta se C == 1       JNC  addr   salta se C == 0
JN   addr   salta se N == 1       JO   addr   salta se O == 1
```

Os seis recebem um label ou um endereço numérico, exatamente como o `JMP`,
e não mexem em nenhuma flag.

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
| `0x70` | `PUSH reg` | `op reg` | 2 |
| `0x71` | `POP reg` | `op reg` | 2 |

Imediatos e endereços são little-endian. A largura do imediato segue o tamanho
da palavra, então **a mesma fonte produz uma imagem diferente em cada
variante** — o que é parte do que o laboratório existe para mostrar. O
programa de conformidade da suíte monta em 63 bytes na PubVM-8, 72 na
PubVM-16 e 90 na PubVM-32, a partir de fonte idêntica.

Uma consequência prática que vale ensinar: como o programa é maior numa
máquina mais larga, um endereço de dados que está livre na PubVM-8 pode cair
**dentro do próprio código** na PubVM-32. Nada impede um `STORE` de
sobrescrever código — é o que uma máquina real faz também — então os exemplos
colocam seus dados fora do alcance da maior imagem.

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
