[English](architecture.md) | [Português](architecture.pt_BR.md)

# Arquitetura

## Camadas

```
┌─────────────────────────────┐
│             UI              │  fase 5   — não implementada
├─────────────────────────────┤
│      Educational Layer      │  fase 7   — não implementada
├─────────────────────────────┤
│       Debugger / State      │  fase 6   — o MachineState existe; o
│                             │             debugger em si, não
├─────────────────────────────┤
│      Execution Engine       │  publab/machine/Engine.kf
├─────────────────────────────┤
│         Assembler           │  publab/assembler/
├─────────────────────────────┤
│   Architecture Interface    │  publab/machine/MachineConfig.kf + Opcodes.kf
├─────────────────────────────┤
│  PubVM / 8051 / Cortex-M3   │  só PubVM; os outros dois são as fases 9-10
└─────────────────────────────┘
```

O que está garantido hoje:

- A máquina não sabe nada sobre interface. Nada em `publab/machine` imprime,
  formata para tela ou carrega conceito de UI.
- A máquina não sabe nada sobre **código-fonte**. A instrução atual é
  desmontada a partir dos bytes na memória, não lembrada do assembler. Mapear
  um endereço de volta para uma linha é o source map do assembler, e juntar os
  dois é tarefa do debugger (fase 6).
- O assembler não sabe nada sobre interface, e produz **códigos**, não frases:
  o idioma de um diagnóstico é escolhido quando ele é renderizado.
- As flags são calculadas em um lugar só, `Alu.kf`, junto com o valor.
- A tabela de instruções vive uma vez, em `Opcodes.kf`. O assembler codifica a
  partir dela e o engine decodifica a partir dela.
- O tamanho da palavra é um valor de configuração. Não existe classe
  `PubVM8`/`PubVM16`/`PubVM32` — só `MachineConfig`.

Como a máquina é um objeto Kof comum com um `snapshot()`, ela pode ser
acionada headless: a suíte de testes inteira faz exatamente isso, e uma CLI ou
uma UI é apenas mais um chamador.

## Layout de diretórios

Em Kof um diretório **é** um pacote, então a árvore também é a árvore de
pacotes.

```
publab/
├── kof.toml                 manifesto do projeto (faz da raiz o module root)
├── publab/
│   ├── app/                 identidade do produto, incl. a atribuição ao Kof
│   ├── machine/             PubVM: palavra, memória, registradores, flags,
│   │                        ALU, tabela de opcodes, decoder, engine
│   └── assembler/           PubASM: lexer, parser, assembler, diagnostics
├── tests/                   um programa por arquivo, rodados por `kof test tests`
├── examples/                programas PubASM, executados pela suíte
└── docs/
```

## Testes

O `kof test` compila **cada arquivo independentemente** como seu próprio
programa, então todo arquivo de teste é autocontido e importa os pacotes de
que precisa. Rodando a suíte inteira:

```bash
kof test tests
```

Os exemplos fazem parte da suíte: `tests/examples_test.kf` lê cada
`examples/*.pasm` do disco, monta para a PubVM-8, executa e verifica a saída.
Um exemplo que parasse de funcionar quebraria o build.

## Notas sobre construir isso em Kof

Escrito contra o **Kof 0.5.0-beta**. Decisões e workarounds que vale conhecer
antes de editar o código:

- **Os valores são `Long`, não `Int`.** Uma palavra de 32 bits sem sinal não
  cabe em um `Int` de 32 bits com sinal, então registradores, palavras de
  memória e resultados da ALU são `Long`. As *células* de memória são `Int` em
  0..255.
- **Kof não tem `~`.** O complemento de bits é `x ^ mask` (`aluNot`).
- **Kof não tem literal long.** Uma constante larga se escreve
  `4294967295 as Long`.
- **Tipos primitivos não têm campos estáticos** (`Int.MAX_VALUE` não existe),
  então os limites são calculados a partir do tamanho da palavra.
- **Um `throw` mora em função própria** (`memoryFault`, `registerFault`,
  `decodeFault`). O backend JS do Kof já tratou errado um `throw` aninhado
  dentro de uma cadeia if/else, e o núcleo da máquina deve compilar para o
  target JS mais adiante, para a UI.
- **Operadores bitwise em `Long` são usados para máscara e para as instruções
  lógicas.** Estão verificados no target JVM; a especificação da linguagem
  marca a semântica bitwise como não especificada entre targets (SG-002),
  então esta é a área a reverificar quando o target JS entrar para a UI. Está
  deliberadamente confinada a `Word.kf` e `Alu.kf`.
- **`List<T>` de um `record` local do pacote não pode ser anotada vazia**
  (`var l: List<OpSpec> = listOf()` dá SEM010 dentro do próprio pacote). Ou se
  semeia a lista com o primeiro elemento, ou se escreve o nome totalmente
  qualificado uma vez num helper — que é para isso que existem
  `emptyDiagnostics()`, `emptyTokens()` e companhia.
- **O narrowing de nulidade só vale dentro do `if`**, então um `String?` vindo
  de `File.readText()` é usado dentro de `if (source != null) { … }`, e não
  depois de um return antecipado.
- **Nenhum retorno sentinela.** Uma busca que pode falhar devolve um record
  pequeno com flag `found` (`OpLookup`, `RegisterLookup`, `SymbolLookup`,
  `LineLookup`), não `-1`.
