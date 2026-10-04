[English](README.md) | [Português](README.pt_BR.md)

# PubLab

**Laboratório Interativo de Arquitetura de Computadores**

> See the machine.

[![Deploy to GitHub Pages](https://github.com/PublioSantos/publab/actions/workflows/pages.yml/badge.svg)](https://github.com/PublioSantos/publab/actions/workflows/pages.yml)
**Powered by: [Kof](https://github.com/KofLang/Kof4j)**

### 👉 [Experimente o PubLab agora — sem instalar nada](https://publiosantos.github.io/publab/)

Ela é reconstruída e republicada automaticamente a cada push na `main`,
então aquela página sempre roda a versão atual — e um push nunca é
publicado sem passar primeiro pela suíte de testes completa nos dois
targets. O que você vê ali é exatamente este repositório.

---

O PubLab é um laboratório para aprender como um computador funciona por
dentro. Você escreve algumas linhas de assembly, aperta **Step**, e vê
acontecer de verdade: os registradores mudam, uma flag vira, um byte cai na
memória, o program counter avança para a próxima instrução — na máquina
real, em execução, não num diagrama.

Abra a página e carregue o `overflow.pasm`, o exemplo com que ela já começa:

```asm
    LOAD A, 250
    LOAD B, 20
    ADD A, B
    PRINT A
    HALT
```

Rode na `PubVM-8` e `A` termina em `14` com o carry ligado. Troque o
seletor de máquina para `PubVM-16` sem mudar mais nada, rode de novo, e `A`
agora é `270` — mesma fonte, mesmas instruções, resposta diferente, porque
270 não cabe num registrador de 8 bits. Essa diferença *é* a lição, e o
laboratório deixa você assistir ela acontecer em vez de só confiar na
palavra de alguém.

```
PubLab
├── PubASM        a linguagem assembly educacional
├── PubVM         a máquina virtual educacional
│   ├── PubVM-8
│   ├── PubVM-16
│   └── PubVM-32
├── 8051          arquitetura histórica        (modelo educacional, planejado)
└── Cortex-M3     arquitetura ARM moderna      (modelo educacional, planejado)
```

## Rodando localmente

Precisa da [toolchain Kof](https://github.com/KofLang/Kof4j) (construída
contra a `0.5.0-beta`):

```bash
kof run Main.kf --target js    # abre o laboratório no webview do Kof
kof test tests                 # a suíte completa, target JVM
kof test tests --target js     # a mesma suíte, target JS
```

## O que tem por dentro

- **PubVM**, um núcleo configurado de três formas (`PubVM-8`/`-16`/`-32`) —
  mesmos registradores, mesmo conjunto de instruções, mesma lógica de
  encoding, só a largura da palavra muda. O `tests/matrix_test.kf` roda o
  conjunto de instruções inteiro, o encoding, imediatos, memória, labels,
  branches e as quatro flags em cada variante, a partir da mesma fonte
  PubASM, então as três variantes não conseguem se desalinhar em silêncio.
- **PubASM**, um assembler de dois passes pequeno, com labels, diagnósticos
  em inglês e português, e um source map que o debugger usa para destacar a
  linha em que a máquina está.
- **Um debugger de verdade**: um dump de memória (hex/dec/bin) com o program
  counter e as escritas da última instrução marcados, uma lista
  antes/depois de tudo o que aquela instrução mudou, e um painel STACK
  acompanhando `SP`/`FP` em tempo real.
- **Um painel EXPLANATION em linguagem natural**: o que o último Step ou Run
  realmente fez, numa frase, construído a partir do mesmo estado
  antes/depois que o debugger já lê — não uma segunda interpretação separada
  do programa, que poderia divergir do que de fato aconteceu.
- **Advanced Mode**, totalmente implementado: registradores gerais `X`/`Y`,
  uma pilha real (`SP`/`FP`, `PUSH`/`POP` com falhas explícitas de
  overflow/underflow, nunca um wrap silencioso), `CALL`/`RET`/`ENTER`/
  `LEAVE`, shifts e rotates, e o conjunto completo de saltos condicionais.

O desenvolvimento segue a ordem da especificação: máquina → testes →
assembler → debugger → UI → camada educacional → Advanced Mode. Toda linha
abaixo é garantida pela suíte de testes.

| Fase | Área | Situação |
|---|---|---|
| 1 | Núcleo PubVM — registradores, memória, flags, ALU, execution engine | **concluída** |
| 2 | PubASM — lexer, parser, labels, diagnostics, assembler | **concluída** |
| 3 | PubVM-16 (mesmo núcleo, palavra maior) | **concluída** |
| 4 | PubVM-32 (mesmo núcleo, palavra maior) | **concluída** |
| 5A | Paridade do núcleo no target JS | **concluída** |
| 5B | UI mínima | **concluída** |
| 6 | Debugger | **concluída** |
| 7 | Camada educacional | **concluída** |
| 8 | Advanced Mode — X, Y, SP, FP, stack, shifts, saltos extras | **concluída** |
| 9 | Modelo educacional do 8051 | não iniciada |
| 10 | Modelo educacional do Cortex-M3 | não iniciada |
| 11 | Comparação entre arquiteturas | não iniciada |
| 12 | Export | não iniciada |

Uma ausência nas fases 1-8 é deliberada, não pendência: não existe botão
**Pause**, porque o runtime de UI JS do Kof não tem timer, então um `Run`
não pode ser interrompido por um clique enquanto está executando. O que
existe no lugar é real: o `Run` é limitado por um orçamento de ciclos,
informa honestamente quando não terminou, e continua exatamente de onde
parou no próximo clique.

## Mais duas arquiteturas estão chegando — 8051 e Cortex-M3

As fases 9 e 10 vão acrescentar mais dois modelos educacionais, e é
importante deixar claro desde já o que isso vai e não vai ser:

- O PubLab **não** é um emulador e **não** é uma ferramenta de
  desenvolvimento para hardware 8051 ou ARM Cortex-M3 real. Um programa que
  roda no PubLab **não** tem garantia de se comportar igual num chip
  físico — nunca o use como referência para firmware, certificação, análise
  de temporização ou qualquer decisão de produção.
- Só um subconjunto explicitamente documentado das instruções e periféricos
  de cada arquitetura será modelado, escolhido pelo que ensina. O que
  estiver fora desse subconjunto estará ausente, não aproximado — e onde um
  nome ou endereço real de registrador for usado, o MCU específico será
  nomeado. O PubLab não vai inventar endereços de periféricos, registradores
  ou comportamentos e apresentá-los como hardware real.

Para trabalho real nessas arquiteturas, use a documentação e a toolchain do
fabricante. Nenhum dos dois módulos está implementado ainda — veja
[docs/8051.pt_BR.md](docs/8051.pt_BR.md) e
[docs/cortex-m3.pt_BR.md](docs/cortex-m3.pt_BR.md) para o que está planejado.

## Atribuição na tela

O PubLab exibe **Powered by: Kof** no rodapé da janela, como uma linha
simples com link para <https://github.com/KofLang/Kof4j> — sem estilo
aplicado.

O texto e a URL vivem em `publab/app/Brand.kf` como fonte única que a
interface lê — `poweredByLabel()` e `poweredByUrl()` — em vez de uma string
que a UI poderia esquecer ou deixar divergir. Coberta por
`tests/brand_test.kf`.

## Licença

MIT — veja [LICENSE](LICENSE).

## Documentação

- [docs/architecture.pt_BR.md](docs/architecture.pt_BR.md) — camadas e como são mantidas separadas
- [docs/pubvm.pt_BR.md](docs/pubvm.pt_BR.md) — a máquina: registradores, flags, memória, encoding
- [docs/pubasm.pt_BR.md](docs/pubasm.pt_BR.md) — a linguagem: sintaxe, instruções, diagnostics
- [docs/8051.pt_BR.md](docs/8051.pt_BR.md) — modelo educacional (não implementado)
- [docs/cortex-m3.pt_BR.md](docs/cortex-m3.pt_BR.md) — modelo educacional (não implementado)
- [examples/](examples/) — programas que realmente rodam, com comentários em inglês e português

A documentação de ensino da seção 38 da especificação (o que é uma CPU, o que
é um registrador, o que é overflow) chega com as fases 9-10.

## Targets

O núcleo roda nos dois targets do Kof a partir da mesma fonte — não existe uma
segunda implementação da máquina em JavaScript:

```
                  ┌── jvm   (testes, e uma CLI futura)
Núcleo PubVM ─────┤
                  └── js    (a UI no navegador, e a página ao vivo acima)
```

O `tests/js_parity_test.kf` é a bateria de paridade: as operações bitwise e
numéricas de que o núcleo depende (SG-002), mais guardas contra os dois
defeitos de geração de código do target JS achados na fase 5A. Veja
[docs/architecture.pt_BR.md](docs/architecture.pt_BR.md) e
[notes/kof-compiler-findings.md](notes/kof-compiler-findings.md).
