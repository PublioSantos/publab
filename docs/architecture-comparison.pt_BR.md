[English](architecture-comparison.md) | [Português](architecture-comparison.pt_BR.md)

# Comparação entre arquiteturas — modelo educacional

## Situação: etapas A e B concluídas

Esta página é o escopo completo para a fase 11, escrita antes de qualquer
código, a mesma disciplina que as fases 8, 9 e 10 usaram. A fase 11 **não**
é uma quarta máquina: ela não adiciona nenhuma semântica de silício própria.
É um recurso de ensino construído inteiramente sobre fatos que as fases
8-10 já estabeleceram e documentaram — o trabalho desta página é dizer
exatamente quais desses fatos ela expõe, e como, não inventar fatos novos.

## Por que a fase 11 existe

Ao final da fase 10, o PubLab consegue rodar três arquiteturas reais — a
PubVM, o 8051 e o Cortex-M3 — mas só uma por vez, cada uma na sua própria
aba, cada uma ensinando seus próprios fatos isoladamente. Um estudante pode
aprender que a pilha do 8051 cresce para cima, ou que o `BL` do Cortex-M3
nunca toca a pilha, mas nada no laboratório coloca esses dois fatos **lado a
lado**. A fase 11 é essa justaposição: a mesma tarefa pequena, escrita uma
vez por arquitetura, rodando lado a lado, para que as diferenças documentadas
em `docs/8051.md` e `docs/cortex-m3.md` como prosa se tornem algo que o
estudante vê acontecer.

## O que a fase 11 não é

- **Não é um conjunto de instruções unificado ou uma camada de tradução.**
  Não existe um "escreva uma vez, rode nas três". Cada arquitetura mantém
  seus próprios mnemônicos, formas e registradores reais, exatamente como
  as fases 9 e 10 os modelaram. Um programa de comparação são três arquivos
  fonte separados, montados independentemente — um por arquitetura — que
  por acaso fazem a mesma coisa do ponto de vista conceitual.
- **Não é uma quarta toolchain.** Nenhum lexer, parser, assembler ou engine
  novo. A fase 11 é só UI e conteúdo de exemplo, construída sobre as três
  engines que já existem (`publab/machine`, `publab/i8051`, `publab/cm3`).
- **Não é uma comparação exaustiva.** Só são expostas as diferenças já
  marcadas como "real, não abstração" nas tabelas da Regra 7 das fases
  8-10. A fase 11 não sai procurando novas distinções real-vs-abstração
  por conta própria.

## Etapa A — 8051 e Cortex-M3 ganham uma aba cada — concluída

O runtime de UI do Kof não tem um widget de aba ou de visibilidade
(`docs/architecture.md` lista as restrições reais do toolkit), então "aba"
aqui significa uma seção autocontida, não um painel dinamicamente
mostrado/escondido: os três laboratórios — PubVM, 8051, Cortex-M3 — ficam
um abaixo do outro na mesma janela, cada um com seu próprio editor,
controles, registradores, flags, saída, diagnósticos e explicação.
`publab/ui/Lab8051.kf` e `publab/ui/LabM3.kf` são os controladores
(espelhando a forma do `Lab.kf`); `Presenter8051.kf`/`PresenterM3.kf`
renderizam seus estados; `Explain8051.kf`/`ExplainM3.kf` dão a cada um uma
explicação genérica de "o que mudou" (registradores e flags que diferiram
entre o estado antes/depois) em vez da prosa por mnemônico feita à mão que
a fase 7 escreveu para a PubVM — a fase 11 é um recurso de comparação, não
uma segunda camada educacional para manter por arquitetura.

As fases 9 e 10 pararam na engine: "ainda sem aba na UI, a mesma ordem que
as outras duas máquinas seguiram" (docs/8051.md, docs/cortex-m3.md). A fase
11 não consegue mostrar três máquinas lado a lado se duas delas não têm
nenhuma tela, então a etapa A fecha essa lacuna primeiro, uma aba cada,
seguindo a mesma forma que a aba da PubVM já tem (fase 5B/6/7): editor de
fonte, Step/Run, um painel de registradores, um painel de flags, uma visão
de memória/pilha, e uma linha de explicação em linguagem simples construída
a partir do estado antes/depois — não uma segunda interpretação do programa
que poderia se distanciar do que realmente aconteceu, a mesma regra que
`docs/architecture.md` estabelece para o próprio painel de explicação da
PubVM.

| item | real ou abstração |
|---|---|
| a aba em si (editor, Step/Run, painéis) | **educacional** — uma facilidade de UI, não um fato de hardware, mesma situação da aba que a PubVM já tem |
| conteúdo dos painéis de registrador/flag/pilha | **real** — lê diretamente do `snapshot()` de cada engine (`MachineState8051`, `MachineStateM3`), já validado pelas suítes de teste das fases 9-10; a etapa A não adiciona nenhum fato novo de máquina, só um renderizador para fatos que já existem |
| a linha de explicação | **educacional**, construída do mesmo jeito que o `Explain.kf` da fase 7: uma frase derivada do estado antes/depois real, nunca uma descrição escrita à mão do que uma instrução "deveria" fazer |

Cada aba é seu próprio módulo de UI autocontido (`publab/ui/Lab8051.kf`,
`publab/ui/LabM3.kf` ou similar), espelhando a forma do `Lab.kf` em vez de
generalizá-lo — as três toolchains se mantiveram deliberadamente
independentes ao longo das fases 9-10 exatamente por esse motivo (para que
as idiossincrasias reais de cada arquitetura fiquem fiéis, não
normalizadas), e a camada de UI mantém essa mesma independência.

## Etapa B — a visão de comparação — concluída

Implementada como `publab/ui/Compare.kf`, seu próprio controlador (a mesma
independência que as três abas da etapa A mantêm): um seletor de programa,
os controles Montar e "Passo (as três)", e três painéis compactos por
arquitetura — situação, saída, e a mesma explicação genérica que as abas
da etapa A usam. Depois que as três máquinas tiverem uma aba, a etapa B
adiciona uma quarta visão: não uma máquina nova, uma leitura lado a lado
das outras três. O
estudante escolhe um de um pequeno conjunto de **programas de comparação**
— uma tarefa curta implementada três vezes, uma por arquitetura, em cada
uma de suas próprias linguagens de montagem reais — e o laboratório roda as
três de uma vez, sincronizadas por Step (um Step avança as três em uma
instrução cada), com as diferenças reais conhecidas destacadas no momento
em que cada uma acontece.

### Programas de comparação (conteúdo da etapa B, não um recurso novo de engine)

Cada programa de comparação são três fontes de exemplo (por exemplo,
`examples/compare/add_overflow.pasm`, `.a51`, `.cm3`), escolhidas porque a
diferença que mostram já é um fato **real** documentado nas fases 8-10, não
uma afirmação nova:

| tarefa | o que mostra | a diferença real (já documentada) |
|---|---|---|
| somar dois números além da largura do registrador | o mesmo overflow, três vocabulários de flag diferentes | o `C`/`O` da PubVM significam "houve borrow/overflow"; o 8051 não tem `Z` persistente, só `C`/`AC`/`OV`/`P`; o `C` do Cortex-M3 numa subtração é **NÃO borrow**, o sentido oposto dos outros dois (docs/cortex-m3.md, "Uma diferença real") |
| uma chamada e retorno de subrotina | três convenções de chamada reais | o `CALL`/`RET` da PubVM empilha/desempilha um endereço de retorno numa pilha que cresce **para baixo**; o `CALL`/`RET` do 8051 empilha/desempilha byte-baixo-depois-byte-alto numa pilha que cresce **para cima** (docs/8051.md); o `BL`/`BX LR` do Cortex-M3 não tocam **nenhuma** pilha — uma chamada aninhada que esquece o `PUSH {LR}` perde silenciosamente o endereço de retorno externo (docs/cortex-m3.md, "Registradores") |
| um valor do tamanho de um registrador movido por uma "porta" | o mesmo ciclo visível via `PRINT`, formas de registrador diferentes | o `X`/`Y` da PubVM são registradores de uso geral comuns; o `R0`-`R7` do 8051 é **bancado**, alias dentro da Internal Data Memory por `PSW.RS1:RS0` (docs/8051.md); o `R0`-`R12` do Cortex-M3 é um register file genuinamente **plano**, e o `GPIOA` só é alcançável pelo `MOV`, nunca por `ADD`/`SUB`/etc. (docs/cortex-m3.md) |

Três programas, não mais, para a etapa B — cada um reaproveitando uma
diferença que o projeto já provou real e já escreveu, em vez da fase 11
pesquisar novas. Uma quarta comparação (por exemplo, o `DPTR` do 8051 vs o
barramento de endereço da PubVM) é uma adição futura natural, não necessária
para a etapa B estar completa.

| item | real ou abstração |
|---|---|
| os programas de comparação | **reais, por arquitetura** — cada um é um programa comum, independentemente válido, na sua própria linguagem de montagem real; nada sobre rodá-lo muda o que as fases 9-10 já validaram |
| sincronização por Step entre três máquinas | **educacional** — o hardware real não tem esse conceito; existe só para que o estudante veja "o mesmo passo conceitual" em três telas ao mesmo tempo |
| o destaque de "o que é diferente aqui" | **apresentação educacional de fatos reais** — nomeia a diferença real já documentada na tabela acima, no ponto da execução em que ela é observável (por exemplo, o destaque do programa de convenção de chamada dispara logo depois da instrução de chamada de cada máquina), nunca uma afirmação nova sobre qualquer arquitetura |

## Explicitamente fora de escopo para a fase 11

- **Nenhuma instrução, registrador ou periférico novo** em nenhuma das três
  arquiteturas — a fase 11 não adiciona nenhuma linha a nenhuma das três
  tabelas de opcode.
- **Nenhuma compatibilidade binária ou tradução entre arquiteturas** — os
  três programas de um conjunto de comparação são escritos à mão por
  arquitetura, não gerados a partir de uma fonte só.
- **Nenhum Run sincronizado**, só Step sincronizado — as fases 1-10 já
  decidiram que a PubVM não tem Pause (`README.md`, "Uma ausência... é
  deliberada"); rodar três máquinas sem supervisão em lockstep precisaria
  exatamente do timer que o runtime de UI em JS do Kof não tem. O Run
  continua existindo por máquina, independentemente.
- **Nenhuma preocupação nova de exportação ou direcionamento a hardware** —
  isso é da fase 12.

## Testes

Etapa A: um arquivo de teste por aba nova, seguindo o padrão já existente
adjacente à UI (a forma do `tests/explain_test.kf`) — verificando o
conteúdo do painel/explicação contra estados de máquina conhecidos, não
exercitando o toolkit de UI em si. Etapa B: um arquivo de teste por programa
de comparação, verificando que cada uma das três fontes de um conjunto
monta, roda, e chega à diferença real documentada (por exemplo, o teste do
programa de overflow verifica que as flags das três máquinas terminam nos
estados que a tabela acima afirma).
