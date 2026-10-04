[English](export.md) | [Português](export.pt_BR.md)

# Exportação — escopo

## Situação: não iniciada — esta página é o escopo, aguardando aprovação

Esta página é o escopo da fase 12, escrita antes de qualquer código, a
mesma disciplina que as fases 8-11 usaram. A fase 12 é diferente de todas
as anteriores: não é uma arquitetura, e não é um recurso de UI construído
sobre fatos já estabelecidos — é o único lugar onde o próprio aviso do
PubLab ("não é um emulador, não é uma ferramenta de desenvolvimento para
hardware real") está diretamente em jogo, então a decisão de escopo
precisa ser explícita, não presumida.

## A tensão central, dita sem rodeios

As tabelas de opcode da PubVM, do 8051 e do Cortex-M3
(`publab/machine/Opcodes.kf`, `publab/i8051/Opcodes8051.kf`,
`publab/cm3/OpcodesM3.kf`) são **codificações inventadas pelo próprio
PubLab**, escolhidas pelo que é simples de ensinar — não os opcodes
binários reais que um chip 8051 ou Cortex-M3 de verdade decodifica.
`docs/8051.md` e `docs/cortex-m3.md` dizem isso desde o primeiro
parágrafo, e `docs/cortex-m3.md` já nomeia a consequência: "Qualquer
exportação futura para hardware real (fase 12) precisa declarar o MCU e o
alvo explicitamente."

Isso significa que **"exportar" não pode significar "produzir um binário
que um chip real consegue rodar"** sem um empreendimento inteiramente
separado: um codificador real para uma peça específica e nomeada (por
exemplo, a codificação de instruções real de um AT89C51 de verdade, ou a
codificação Thumb-2 real de um STM32F103 de verdade), construído e
verificado contra o datasheet daquela peça — não derivado de
`Opcodes.kf`/`Opcodes8051.kf`/`OpcodesM3.kf` de forma alguma, porque essas
tabelas nunca foram reais para começo de conversa. Isso é um projeto do
tamanho aproximado das fases 9 ou 10 de novo, por arquitetura, e muda o que
o PubLab é: uma segunda toolchain real, de verdade, vivendo ao lado da
educacional, para uma peça nomeada, com sua própria barra de correção (um
byte errado ali não é uma simplificação didática, é um bug em algo que
alguém pode gravar em silício real).

## O que a fase 12 de fato escopa: duas opções honestas

**Opção A — exportação de sessão (padrão recomendado).** O PubLab exporta
o que já tem, rotulado honestamente pelo que é: o fonte PubASM/8051-asm/
Cortex-M3-asm, os bytes montados no formato próprio do PubLab, o estado
final de registradores/flags/memória, e o rastro de explicações — como um
arquivo de texto ou JSON que o estudante pode salvar, imprimir, ou entregar
a um professor. Nenhuma alegação de compatibilidade com hardware em lugar
nenhum dele; o próprio cabeçalho do arquivo repete o aviso. É um recurso
de UI/IO em cima do que já existe (o `snapshot()` do `MachineState`/
`MachineState8051`/`MachineStateM3`), não um codificador novo, e cabe no
tamanho de uma etapa normal.

**Opção B — exportação binária real para um MCU nomeado.** Um segundo
codificador genuinamente real para uma peça específica e nomeada,
construído a partir do datasheet daquela peça, mantido inteiramente
separado das tabelas de opcode educacionais, com sua própria página de
escopo sob a Regra 7, sua própria suíte de testes verificada contra saída
de montagem real conhecida como correta, e seu próprio escopo explícito de
aviso (que subconjunto do conjunto de instruções real da peça ele cobre,
já que o subconjunto educacional do PubLab já é mais estreito que o de
qualquer chip real). É um empreendimento muito maior — mais perto de uma
nova fase 9/10 do que de uma etapa da fase 12 — e **não** é proposto como
parte do escopo desta página.

Esta página propõe **só a Opção A** para a fase 12. A Opção B, se um dia
for desejada, precisa de sua própria página de escopo futura, nomeando uma
peça real específica, escrita com o mesmo cuidado que as fases 9 e 10
deram aos modelos educacionais — exportação para hardware real não é um
recurso para se chegar de trás, estendendo os codificadores didáticos.

## Etapa A — a exportação de sessão (Opção A)

| item | real ou abstração |
|---|---|
| o fonte exportado | **real** — exatamente o texto do editor no momento da exportação, byte a byte |
| os bytes montados exportados | **reais para o formato próprio do PubLab** — a saída de fato de `assembleSource`/`assembleSource8051`/`assembleSourceM3`, rotulada explicitamente como a codificação educacional do PubLab, não a de um chip real |
| o estado de registrador/flag/memória exportado | **real** — lido do mesmo `snapshot()` que a UI e os testes já usam, nada re-derivado |
| o formato do arquivo em si | **escolha educacional/de ferramenta** — texto simples ou JSON, próprio do PubLab, não um formato padrão de objeto/hex (ver "Explicitamente fora de escopo") |

Conteúdo de uma exportação, por máquina que o estudante montou (PubVM,
8051, Cortex-M3, ou o conjunto da visão de comparação — o que quer que a
exportação tenha vindo):

```
Exportação do PubLab — <nome da máquina> — <timestamp ISO 8601>
Codificação educacional própria do PubLab — NÃO são os opcodes binários
reais de um <arquitetura> de verdade. Ver docs/<página>.md. Nunca grave
isto em hardware real.

--- fonte ---
<o texto exato PubASM/8051-asm/Cortex-M3-asm>

--- bytes montados (formato próprio do PubLab) ---
<dump hex, a mesma renderização que o painel de memória já usa>

--- estado final ---
<registradores, flags, ciclos, situação, saída — os mesmos campos que o snapshot() carrega>
```

O parágrafo de aviso não é opcional nem encurtável — é a única linha que
separa "o arquivo salvo de uma ferramenta de ensino" de "algo que parece
ter saído de uma toolchain real", e vai nos dois idiomas que a UI já
suporta.

## Explicitamente fora de escopo para a fase 12

- **Qualquer binário que um chip real pudesse executar** — ver "A tensão
  central" acima; isso é a Opção B, não proposta aqui.
- **Formatos de objeto padrão da indústria** (Intel HEX, SREC, ELF) — esses
  formatos carregam uma alegação implícita de que podem ser levados a
  hardware, que a codificação própria do PubLab não cumpre; um dump hex
  simples num arquivo de texto não faz essa alegação.
- **Importação** — a fase 12 é só exportação; ler de volta um arquivo
  `.hex`/`.elf` é um recurso diferente, não pedido.
- **Qualquer mudança nas três tabelas de opcode educacionais** — a fase 12
  não adiciona nenhuma instrução, registrador ou periférico a nenhuma
  arquitetura.

## Testes

Um arquivo de teste por exportação de máquina (`tests/export_test.kf` ou
dividido por arquitetura), verificando que o texto exportado contém o
fonte real ao pé da letra, a contagem real de bytes montados, os valores
reais finais de registrador/flag de um programa conhecido — e que o
parágrafo de aviso está presente nos dois idiomas. A mesma regra "construído
a partir do estado real, não re-derivado" que todo outro painel de
explicação da fase 7/11 já segue.
