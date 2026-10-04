[English](README.md) | [Português](README.pt_BR.md)

# PubLab

**Laboratório Interativo de Arquitetura de Computadores**

> See the machine.

**Powered by: [Kof](https://github.com/KofLang/Kof4j)**

O PubLab é um laboratório para aprender como um computador funciona por
dentro: você escreve um programa pequeno, executa instrução por instrução e vê
os registradores, as flags, a memória e o program counter mudarem de verdade.

```
PubLab
├── PubASM        a linguagem assembly educacional
├── PubVM         a máquina virtual educacional
│   ├── PubVM-8
│   ├── PubVM-16
│   └── PubVM-32
├── 8051          arquitetura histórica        (modelo educacional)
└── Cortex-M3     arquitetura ARM moderna      (modelo educacional)
```

---

## ⚠️ 8051 e Cortex-M3: modelos educacionais simplificados

**Implementação simplificada para aprendizado, não código compatível com
produção.**

Os módulos 8051 e Cortex-M3 do PubLab são **modelos de ensino**. Quando forem
implementados, cobrirão um subconjunto documentado de cada arquitetura,
escolhido pelo que ensina, e todo periférico que for abstração em vez de
silício real dirá isso na própria página onde aparece.

O que isso significa na prática:

- O PubLab **não** é um emulador e **não** é ferramenta de desenvolvimento
  para hardware 8051 ou ARM Cortex-M3 real.
- Um programa que roda no PubLab **não** tem garantia de se comportar igual
  em um chip físico, e nunca deve ser usado como referência para firmware,
  certificação, análise de temporização ou qualquer decisão de produção.
- Apenas um subconjunto explicitamente documentado das instruções e dos
  periféricos é modelado. O que está fora desse subconjunto está ausente, não
  aproximado.
- Quando nomes ou endereços reais de registradores forem usados, o MCU
  específico será nomeado. O PubLab não inventa endereços de periféricos,
  registradores, instruções ou comportamentos e os apresenta como hardware
  real.

Para trabalho real nessas arquiteturas, use a documentação e a toolchain do
fabricante.

**Situação atual: nenhum dos dois módulos está implementado.** Estão previstos
para as fases 9 e 10. Veja [docs/8051.pt_BR.md](docs/8051.pt_BR.md) e
[docs/cortex-m3.pt_BR.md](docs/cortex-m3.pt_BR.md).

---

## O que está implementado hoje

O desenvolvimento segue a ordem da especificação: máquina → testes →
assembler → debugger → UI → camada educacional. Nada abaixo é afirmado sem
estar coberto pela suíte de testes.

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
| 8 | Advanced Mode — X, Y, SP, FP, stack, shifts, saltos extras | em andamento (etapa A: X, Y, SP, FP, PUSH, POP) |
| 9 | Modelo educacional do 8051 | não iniciada |
| 10 | Modelo educacional do Cortex-M3 | não iniciada |
| 11 | Comparação entre arquiteturas | não iniciada |
| 12 | Export | não iniciada |

O núcleo da máquina é **parametrizado pelo tamanho da palavra**: PubVM-8, -16
e -32 são uma implementação configurada de formas diferentes, nunca três
cópias. As três estão validadas ponta a ponta — `tests/matrix_test.kf` roda o
conjunto de instruções inteiro do Basic Mode, o encoding, imediatos, memória,
PC, labels, branches e as quatro flags sobre cada variante, a partir de fonte
PubASM idêntica.

A janela do laboratório é a interface mínima da fase 5B: um editor PubASM, um
seletor de máquina, um seletor de exemplos, um seletor de idioma, os quatro
controles, os registradores em decimal/hexadecimal/binário, as flags, o estado
com PC e contagem de ciclos, a instrução atual lida de volta da memória, a
saída e os diagnósticos. Ela renderiza no navegador a partir do mesmo núcleo
que os testes exercitam.

```bash
kof run Main.kf --target js
```

O debugger da fase 6 acrescenta: o dump de memória em hexadecimal, decimal ou
binário com o PC e as células escritas pela última instrução marcados, uma
lista antes/depois de tudo o que aquela instrução mudou, um marcador de uma
coluna nos registradores e nas flags, e a linha da fonte em que o PC está,
pelo source map do assembler.

A camada educacional (fase 7) acrescenta um painel EXPLANATION em linguagem
natural: o que o último Step ou Run realmente fez, construído a partir dos
mesmos snapshots antes/depois que a lista de mudanças do debugger já lê —
nunca uma segunda interpretação do programa.

O Advanced Mode (fase 8) está sendo implementado em etapas. A etapa A está
concluída: `X` e `Y` são registradores gerais comuns; `SP` e `FP` estão
implementados como endereços ao lado do `PC` (não como registradores do
tamanho da palavra — o valor inicial do `SP`, um endereço além do topo da
memória, não cabe numa palavra de 8 ou 16 bits); `PUSH` e `POP` movem a
pilha, com falhas explícitas de overflow/underflow, nunca um wrap silencioso.
O painel STACK do debugger mostra SP/FP e as palavras que o PUSH escreveu,
lidas da memória real através do SP. `CALL`, `RET`, `ENTER`, `LEAVE`, os
shifts, rotates e os saltos condicionais restantes (`JN`, `JO`, `JNZ`,
`JNC`) são etapas posteriores — o assembler reconhece esses mnemônicos e diz
que pertencem ao Advanced Mode, em vez de reportá-los como desconhecidos.

Uma ausência é deliberada, não pendência:

- **Sem botão Pause.** O runtime de UI JS do Kof não tem timer, então uma
  execução não pode ser interrompida por um botão — o clique não chegaria
  enquanto o run executa. O que existe no lugar é real: o `Run` é limitado
  por um orçamento de ciclos, informa que não terminou e continua de onde
  parou. O engine mantém o `requestPause()` para um chamador capaz de
  acionar a máquina em fatias.

## Atribuição na tela

O PubLab exibe **Powered by: Kof** no rodapé da janela, como uma linha
simples com link para <https://github.com/KofLang/Kof4j> — sem estilo
aplicado.

O texto e a URL vivem em `publab/app/Brand.kf` como fonte única que a
interface lê — `poweredByLabel()` e `poweredByUrl()` — em vez de uma string
que a UI poderia esquecer ou deixar divergir. Coberta por
`tests/brand_test.kf`.

## Rodando os testes

Precisa da toolchain Kof (construído contra a 0.5.0-beta):

```bash
kof test tests
```

## Licença

MIT — veja [LICENSE](LICENSE).

## Documentação

- [docs/architecture.pt_BR.md](docs/architecture.pt_BR.md) — camadas e como são mantidas separadas
- [docs/pubvm.pt_BR.md](docs/pubvm.pt_BR.md) — a máquina: registradores, flags, memória, encoding
- [docs/pubasm.pt_BR.md](docs/pubasm.pt_BR.md) — a linguagem: sintaxe, instruções, diagnostics
- [docs/8051.pt_BR.md](docs/8051.pt_BR.md) — modelo educacional (não implementado)
- [docs/cortex-m3.pt_BR.md](docs/cortex-m3.pt_BR.md) — modelo educacional (não implementado)
- [examples/](examples/) — programas que realmente rodam

A documentação de ensino da seção 38 da especificação (o que é uma CPU, o que
é um registrador, o que é overflow) chega com a camada educacional na fase 7.

## Targets

O núcleo roda nos dois targets do Kof a partir da mesma fonte — não existe uma
segunda implementação da máquina em JavaScript:

```
                  ┌── jvm   (testes, e uma CLI futura)
Núcleo PubVM ─────┤
                  └── js    (a UI no navegador, fase 5B)
```

Os dois estão verdes na suíte inteira:

```bash
kof test tests
kof test tests --target js
```

O `tests/js_parity_test.kf` é a bateria de paridade: as operações bitwise e
numéricas de que o núcleo depende (SG-002), mais guardas contra os dois
defeitos de geração de código do target JS achados na fase 5A. Veja
[docs/architecture.pt_BR.md](docs/architecture.pt_BR.md) e
[notes/kof-compiler-findings.md](notes/kof-compiler-findings.md).
