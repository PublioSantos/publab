[English](architecture.md) | [Português](architecture.pt_BR.md)

# Arquitetura

## Camadas

```
┌─────────────────────────────┐
│             UI              │  Main.kf + publab/ui/ (fase 5B)
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
  partir dela e o engine decodifica a partir dela (veja a regra abaixo).
- O tamanho da palavra é um valor de configuração. Não existe classe
  `PubVM8`/`PubVM16`/`PubVM32` — só `MachineConfig`.

## Regra arquitetural: um encoding, uma definição

**Nunca pode existir uma tabela de opcodes no assembler e outra no engine.**
Uma definição única — `publab/machine/Opcodes.kf` — carrega o caminho inteiro:

```
PubASM
   ↓   Assembler   (codifica a partir da tabela)
bytes
   ↓
Memory
   ↓
PC
   ↓   Decoder     (decodifica a partir da mesma tabela)
Execution
```

Tudo o que vem depois depende disso valer: a visão de memória mostra código de
máquina real, a desmontagem da instrução atual é lida de volta da memória em
vez de lembrada da fonte, e o debugger (fase 6) pode confiar que os bytes no
PC significam exatamente o que o assembler escreveu. Uma segunda tabela
deixaria as duas metades divergirem em silêncio — o tipo de defeito que
aparece como um laboratório ensinando algo falso.

Acrescentar uma instrução é acrescentar uma linha em `opcodeTable()`. Se
alguma mudança exigir editar um número de opcode em dois lugares, a mudança
está errada.

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
  lógicas.** A especificação da linguagem marca a semântica bitwise como não
  especificada entre targets (SG-002), então eles foram verificados nos
  **dois** targets antes de qualquer trabalho de UI:
  `tests/js_parity_test.kf` roda as máscaras, os shifts, as operações lógicas
  acima de 2^31, as flags e a palavra de 32 bits na memória em `jvm` e em
  `js`, e os resultados são idênticos. O SG-002 não é problema para este
  núcleo. O uso continua confinado a `Word.kf`, `Alu.kf`, `Memory.kf` e um
  helper em `Assembler.kf`.
- **Dois defeitos de geração de código do target JS determinam como o fluxo de
  controle é escrito aqui**, ambos achados na fase 5A e documentados com
  repro mínimo em `notes/kof-compiler-findings.md`:
  - **Nunca colocar `return` antecipado dentro de um `if` aninhado no ramo
    `else`** quando há mais statements depois dele nesse ramo — o target JS
    descarta o `return` final da função e ela devolve `undefined`. Usar ponto
    de saída único. (`resolveAddressOperand`, `parseMemoryOperand`.)
  - **Nunca proteger uma indexação com `&&` na mesma condição** —
    `list.size > 0 && list.get(list.size - 1)` avalia o lado direito no target
    JS mesmo com o esquerdo falso. Usar `if` aninhado. (Pass 1 do assembler.)
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
