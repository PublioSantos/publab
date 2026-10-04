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
| 3 | PubVM-16 (mesmo núcleo, palavra maior) | não iniciada |
| 4 | PubVM-32 (mesmo núcleo, palavra maior) | não iniciada |
| 5 | UI mínima | não iniciada |
| 6 | Debugger | não iniciada |
| 7 | Camada educacional | não iniciada |
| 8 | Advanced Mode — X, Y, SP, FP, stack, shifts, saltos extras | não iniciada |
| 9 | Modelo educacional do 8051 | não iniciada |
| 10 | Modelo educacional do Cortex-M3 | não iniciada |
| 11 | Comparação entre arquiteturas | não iniciada |
| 12 | Export | não iniciada |

O núcleo da máquina é **parametrizado pelo tamanho da palavra** desde o
começo: PubVM-8, -16 e -32 são uma implementação configurada de formas
diferentes, nunca três cópias. As fases 1-2 expõem e validam somente a
configuração de 8 bits.

**Ainda não existe interface de usuário.** A máquina é acionada pela suíte de
testes e por código Kof.

As instruções do Advanced Mode (`PUSH`, `POP`, `CALL`, `RET`, `SHL`, `SHR`,
`ROL`, `ROR`, `JN`, `JO`, `JNZ`, `JNC`, `ENTER`, `LEAVE`) e os registradores
`X`, `Y`, `SP`, `FP` **não estão implementados**. O assembler os reconhece e
diz isso, em vez de reportá-los como desconhecidos.

## Atribuição na tela

O PubLab exibe **Powered by: Kof**, com link para
<https://github.com/KofLang/Kof4j>, ao lado do nome do produto.

Ainda não existe interface (fase 5), então a atribuição vive em
`publab/app/Brand.kf` como fonte única que a interface vai renderizar —
`poweredByLabel()` e `poweredByUrl()` — em vez de uma string que a UI poderia
esquecer. Está coberta por `tests/brand_test.kf`.

## Rodando os testes

Precisa da toolchain Kof (construído contra a 0.5.0-beta):

```bash
kof test tests
```

## Documentação

- [docs/architecture.pt_BR.md](docs/architecture.pt_BR.md) — camadas e como são mantidas separadas
- [docs/pubvm.pt_BR.md](docs/pubvm.pt_BR.md) — a máquina: registradores, flags, memória, encoding
- [docs/pubasm.pt_BR.md](docs/pubasm.pt_BR.md) — a linguagem: sintaxe, instruções, diagnostics
- [docs/8051.pt_BR.md](docs/8051.pt_BR.md) — modelo educacional (não implementado)
- [docs/cortex-m3.pt_BR.md](docs/cortex-m3.pt_BR.md) — modelo educacional (não implementado)
- [examples/](examples/) — programas que realmente rodam

A documentação de ensino da seção 38 da especificação (o que é uma CPU, o que
é um registrador, o que é overflow) chega com a camada educacional na fase 7.
