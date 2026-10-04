[English](cortex-m3.md) | [Português](cortex-m3.pt_BR.md)

# Cortex-M3 — modelo educacional

## ⚠️ Implementação simplificada para aprendizado, não código compatível com produção

O módulo ARM Cortex-M3 do PubLab é um **modelo de ensino**, não um emulador
e não uma ferramenta de desenvolvimento para hardware ARM real.

- Um programa que roda aqui **não** tem garantia de se comportar igual em um
  Cortex-M3 físico, e nunca deve ser usado como referência para firmware,
  certificação, análise de temporização ou qualquer decisão de produção.
- Apenas um subconjunto explicitamente documentado do conjunto de
  instruções Thumb é modelado. O que está fora desse subconjunto está
  **ausente, não aproximado**.
- Periféricos (GPIO, UART, SysTick, Timer) são marcados como `conceitual`
  ou `baseado em <MCU específico>`. **Nenhum endereço de periférico é
  inventado.** O núcleo Cortex-M3 define muito pouco do que uma placa
  expõe; sempre que um registrador ou endereço real for usado, a peça
  específica será nomeada.
- Latência de interrupção, contagem de ciclos, a memory protection unit,
  caches, pipelining e comportamento elétrico **não** são modelados.
- Qualquer exportação futura para hardware real (fase 12) precisa declarar
  o MCU e o alvo explicitamente.

## Situação: etapas A e B concluídas

Esta página é o escopo completo para a fase 10, marcado item por item como
arquitetura real ou abstração educacional (Regra 7 da especificação),
seguindo a mesma disciplina que a fase 8 (Advanced Mode) e a fase 9 (8051)
usaram: documentado e aprovado antes de qualquer código ter sido escrito. A
implementação segue em etapas, cada uma com seus próprios testes.

- **Etapa A — concluída.** Núcleo: registradores, flags do APSR, um
  espaço de memória plano, o subconjunto Thumb abaixo, saltos
  condicionais, `BL`/`BX LR`, `PUSH`/`POP` multi-registrador. Vive em
  `publab/cm3/`, sua própria toolchain autocontida — não é um modo da
  PubVM nem do 8051. Coberta por `tests/cm3_core_test.kf`,
  `tests/cm3_asm_test.kf`, `tests/cm3_engine_test.kf` e
  `tests/cm3_golden_test.kf`. Ainda sem aba na UI, a mesma ordem que as
  outras duas máquinas seguiram.
- **Etapa B — concluída.** Uma porta GPIO (`GPIOA`), modelada do mesmo
  jeito que o `P0` do 8051: um registrador comum de leitura/escrita,
  conceitual, sem endereço de periférico inventado.

## Registradores

| nome | largura | real ou abstração |
|---|---|---|
| `R0`-`R12` | 32 bits | real — um register file genuinamente plano, diferente do `R0`-`R7` bancado do 8051. Isso em si é um ponto de ensino para a fase 11: dois esquemas de "registradores de uso geral" que funcionam de formas completamente diferentes sob o mesmo tipo de nome. |
| `SP` (`R13`) | 32 bits | real, mas **restrito**: o Cortex-M3 real tem dois stack pointers (Main SP e Process SP, trocados por um bit do registrador CONTROL, para uso com RTOS). Este modelo tem **um** SP só — apenas o Main SP. O Process SP e a troca estão ausentes, não aproximados; são um recurso real, ligado a um modelo de privilégio/RTOS que este laboratório não tem uso para, de outra forma. |
| `LR` (`R14`) | 32 bits | real — guarda o endereço de retorno depois do `BL`, exatamente como o hardware real. Diferente do `CALL` da PubVM ou do 8051, **o `BL` não toca a pilha de forma alguma** — uma chamada aninhada precisa fazer `PUSH {LR}` ela mesma antes de chamar de novo, ou o primeiro endereço de retorno simplesmente se perde. Isso é comportamento real do ARM, não uma simplificação, e é uma das comparações mais claras para as quais a fase 11 existe. |
| `PC` (`R15`) | 32 bits | real, com uma restrição: o hardware real lê o `PC` como "o endereço da instrução atual + 4" quando usado como operando de dado (o deslocamento histórico do pipeline do Thumb), o que nenhuma instrução da etapa A expõe — o `PC` aqui é sempre só o endereço de busca, nunca lido como um valor de dado. |

## Flags (APSR: `N`, `Z`, `C`, `V`)

Reais, e — diferente do `C`/`AC`/`OV`/`P` do 8051 — o mesmo formato de
quatro letras que a PubVM já usa (`C`, `Z`, `N`, `O`), o que é deliberado:
a comparação da fase 11 precisa de pelo menos uma arquitetura cujas flags
se alinhem com as da PubVM quase pelo nome, para que a comparação seja
sobre comportamento, não vocabulário.

| flag | significado | real ou abstração |
|---|---|---|
| `N` | bit de sinal do resultado | real |
| `Z` | resultado é zero | real |
| `C` | carry out (data-processing) / NÃO borrow (em `SUB`/`CMP`, a convenção de carry do ARM é o complemento de um borrow de subtração — ver abaixo) | real |
| `V` | overflow com sinal | real |

### Uma diferença real tanto da PubVM quanto do 8051: o `CMP` define flags sem guardar um resultado

`CMP Rn, Rm` (e `CMP Rn, #imm`) calcula `Rn - Rm` só para as flags — o
resultado da subtração é descartado, nunca escrito num registrador. Esse é
o jeito real e idiomático do código ARM decidir um salto: calcular a
comparação com `CMP`, depois saltar com uma condição que lê as flags que o
`CMP` acabou de definir — diferente da PubVM/8051, onde as flags que um
salto testa vêm de qualquer instrução aritmética que rodou bem antes dele.

### O `C` no `SUB`/`CMP` é a convenção do próprio ARM real, não a da PubVM

O ARM real define o `C` numa subtração como **NÃO borrow** (`C = 1`
significa que não houve borrow — o sentido oposto do `C` da PubVM e do
8051, que são ambos "houve borrow"). Este modelo mantém essa inversão real
em vez de normalizá-la para combinar com a PubVM, porque a própria inversão
— "a mesma flag com o mesmo nome significa o oposto numa arquitetura real
diferente" — é exatamente o que a fase 11 existe para mostrar.

### Exatamente quais instruções mexem em quais flags

| instrução | N | Z | C | V |
|---|---|---|---|---|
| `ADD`, `ADC` | define | define | define | define |
| `SUB`, `CMP` | define | define | define (NÃO borrow — ver acima) | define |
| `AND`, `ORR`, `EOR` | define | define | não mexe | não mexe |
| `MOV` | define | define | não mexe | não mexe |
| `LDR`, `STR`, `B`, `B<cond>`, `BL`, `BX`, `PUSH`, `POP`, `HALT`, `PRINT` (educacionais) | não mexe | não mexe | não mexe | não mexe |

O hardware Thumb-1 real define as flags em instruções de data-processing
incondicionalmente fora de um bloco `IT` (um recurso do Thumb-2, ver
"Explicitamente fora de escopo") — então este modelo sempre atualiza as
flags em `ADD`/`SUB`/`CMP`/lógicas/`MOV`, que é o comportamento real do
caso simples, não uma abstração. O sufixo `S` que alguns assemblers reais
exigem (`ADDS` vs `ADD`) não é modelado como um mnemônico separado — ver
"Instruções" abaixo.

## Memória

```
Memória   64 KB, um espaço de endereço plano só (código e dados juntos)
```

O Cortex-M3 real também expõe um espaço de endereço único e unificado ao
software (Flash, SRAM e periféricos em faixas fixas diferentes do mesmo
mapa) — a **simplificação** deste modelo é o tamanho e a ausência de
faixas fixas: um espaço plano de 64 KB só, sem faixas reservadas de
Flash/SRAM/periférico, porque a etapa A ainda não tem periférico para
reservar uma faixa (a porta GPIO da etapa B é um registrador nomeado, não
um endereço mapeado em memória — ver "Periféricos").

## Instruções — etapa A

Mnemônicos reais do Thumb, um subconjunto deliberadamente pequeno:

| instrução | formas | notas |
|---|---|---|
| `MOV` | `MOV Rd, #imm` · `MOV Rd, Rm` | real |
| `ADD` | `ADD Rd, Rn, Rm` · `ADD Rd, Rn, #imm` | real; forma de três operandos, como o Thumb real (`Rd` não precisa ser `Rn`) |
| `SUB` | `SUB Rd, Rn, Rm` · `SUB Rd, Rn, #imm` | real, mesma forma de três operandos |
| `AND`, `ORR`, `EOR` | `op Rd, Rn, Rm` | mnemônicos reais (`EOR`, não o `XOR` da PubVM); sem forma imediata na etapa A — as formas imediatas lógicas do Thumb-1 real são estreitas e não valem o esforço de encoding aqui |
| `CMP` | `CMP Rn, Rm` · `CMP Rn, #imm` | real — ver "Uma diferença real" acima |
| `LDR`, `STR` | `op Rd, [Rn]` · `op Rd, [Rn, #imm]` | real — o único jeito de tocar memória; não há operando de memória no `ADD`/`SUB`/etc., a restrição real de arquitetura load/store |
| `B` | `B label` | real, incondicional |
| `BEQ`, `BNE`, `BCS`, `BCC`, `BMI`, `BPL`, `BVS`, `BVC` | `op label` | códigos de condição reais, lendo `Z`/`C`/`N`/`V` exatamente como a lógica de condição do hardware real faz (`BCS`≡`BHS`, `BCC`≡`BLO` são a mesma condição real sob dois nomes do ARM — só uma grafia de cada é implementada) |
| `BL` | `BL label` | real — `LR = endereço de retorno`, `PC = label`. Nenhuma pilha envolvida (ver "Registradores" acima). |
| `BX` | `BX LR` | real — `PC = LR`. O idioma real de retorno; só a forma de operando `LR` é implementada (o `BX` real aceita qualquer registrador) |
| `PUSH`, `POP` | `op {reglist}` | sintaxe real do Thumb — uma **lista** de registradores entre chaves, não um registrador único do jeito que o `PUSH`/`POP` da PubVM/8051 são. Guardados/carregados em ordem crescente de número de registrador para endereços crescentes, full-descending (`SP` decrementado pelo tamanho da lista inteira *antes* da primeira escrita) — o comportamento real de `STMDB`/`LDM` que o `PUSH`/`POP` expandem para. |
| `HALT` | `HALT` | **não é uma instrução real do Cortex-M3.** Mesma justificativa do `HALT` educacional da PubVM e do 8051. |
| `PRINT` | `PRINT Rd` | **não é uma instrução real**, reaproveitada ao pé da letra pelo mesmo motivo. |

## Explicitamente fora de escopo para a fase 10

- **Instruções Thumb-2 de 32 bits, blocos de execução condicional
  `IT`/`ITE`** — o Cortex-M3 real suporta tanto Thumb de 16 bits quanto
  Thumb-2 de 32 bits no mesmo stream; este modelo implementa só instruções
  no formato Thumb-1 de 16 bits e não tem um construto de
  execução-condicional-sem-salto.
- **O barrel shifter** (`LSL`/`LSR`/`ASR`/`ROR` como segundo operando
  deslocado em instruções de data-processing, e como instruções
  independentes) — uma parte real e significativa do ISA Thumb, ausente
  aqui, não aproximada.
- **`MUL`, multiplicação/divisão longa, aritmética saturada** — ausentes.
- **Exceções e interrupções** (o NVIC, `SVC`, fault handlers, a vector
  table, `PRIMASK`/`FAULTMASK`/`BASEPRI`) — uma parte real e grande do
  modelo de programação do Cortex-M3, totalmente fora de escopo para a
  fase 10. Assim como as interrupções do 8051, isso precisaria de sua
  própria página de escopo sob a Regra 7, se um dia for modelado.
- **O Process stack pointer e o registrador CONTROL** — ver
  "Registradores" acima (`SP`).
- **Bit-banding, a MPU, caches, a unidade de debug/trace (ITM, DWT)** —
  ausentes.
- **Periféricos SysTick, UART, Timer** — só uma porta GPIO está planejada
  (etapa B). O resto está ausente até que uma fase futura os coloque em
  escopo do mesmo jeito que esta página coloca a porta GPIO.
- **Contagem de ciclos, pipelining, latência de interrupção, comportamento
  elétrico** — nunca modelados, como dito no topo desta página.

## Periféricos — etapa B (concluída)

| nome | modelo |
|---|---|
| `GPIOA` (uma porta GPIO) | **conceitual** — baseada na forma geral de uma porta GPIO do Cortex-M3 (um registrador de dados diretamente legível e gravável), não no layout de registrador exato ou endereço de um fabricante específico, já que o próprio núcleo Cortex-M3 não define nenhum endereço de periférico — isso é inteiramente específico do fabricante (o motivo inteiro do aviso de abertura desta página dizer "nenhum endereço de periférico é inventado"). Modelada do mesmo jeito que o `P0` do 8051: um registrador comum, sem nenhuma nuance elétrica (força de drive, configuração de pull-up/down, multiplexação de função alternativa — tudo real em silício de verdade) modelada. Nomeada como `SP`/`LR`, não como `R0`-`R12` — **não** é um registrador baixo, então `ADD`/`SUB`/`AND`/`ORR`/`EOR`/`CMP` a rejeitam exatamente como rejeitam `SP`/`LR`; só o `MOV` alcança ela nesta etapa. `GPIOB`, o `SysTick`, a `UART` e o `Timer` continuam reservados; nada além de uma porta está em escopo para a fase 10. |
