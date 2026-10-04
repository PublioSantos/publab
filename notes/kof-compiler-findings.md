# Achados do compilador Kof durante o PubLab

Notas locais. **Nada aqui foi reportado como issue** — registro para decidir
depois se entra no fluxo do `kofbughunter`, com repro mínimo próprio e
seguindo o template de issue.

Toolchain: `kof-toolchain/current` → `kof-beta-tip`, VERSION `0.5.0-beta`.
Target usado: `jvm`.

---

## 1. `List<T>` de record local do pacote não aceita anotação vazia (SEM010)

Dentro do **mesmo pacote** onde o `record` é declarado, anotar um local como
`List<Record>` e atribuir `listOf()` é rejeitado, enquanto o tipo de retorno da
mesma função é aceito:

```kof
package publab.machine

record OpSpec(Int opcode, String mnemonic, Int form)

List<OpSpec> opcodeTable() {
    var table: List<OpSpec> = listOf()    // SEM010
    return table
}
```

```
Opcodes.kf:51:5: error: Return type mismatch:
  expected 'List<publab.machine.OpSpec>' but got 'List<OpSpec>' [SEM010]
```

O tipo de **retorno** `List<OpSpec>` é qualificado para
`List<publab.machine.OpSpec>`; o tipo **declarado do local** não é, e os dois
não unificam. Erro em tempo de compilação, não silencioso.

Dois workarounds, ambos usados no projeto:

```kof
var table = listOf(OpSpec(0x00, "HALT", formNone()))     // semear e inferir
var l: List<publab.machine.OpSpec> = listOf()            // qualificar à mão
```

Os helpers `emptyDiagnostics()`, `emptyTokens()`, `emptyOperands()`,
`emptyInstructions()`, `emptyLabels()`, `emptyPlaced()`, `emptySymbols()` e
`emptySourceMap()` existem por causa disto — isolam a forma qualificada em uma
linha por tipo.

**Antes de abrir qualquer coisa:** conferir `grammar.md` e `DECISIONS.md`
(regra de qualificação de nomes simples, `qualifyDeep`/`CompilerTypes`) para
saber se isso é comportamento decidido e não um bug.

---

## 2. `kof check <dir>` não enxerga subdiretórios

`kof check .` na raiz do projeto responde `no .kf/.kof files found`, e
`kof check publab/machine` falha com `PKG004` porque trata o diretório passado
como module root:

```
publab/machine/Alu.kf:0:0: error: package 'publab.machine' does not match
  the directory ('') — a directory is a package [PKG004]
```

Consequência prática: **não existe passo de type-check do projeto inteiro**. O
type-check acontece via `kof test tests`, porque cada arquivo de teste importa
os pacotes e o compilador expande o diretório. Não é bug confirmado — pode ser
só a superfície do CLI.

---

## 3. Confirmados funcionando (sem surpresa, mas foram probados antes de usar)

Probados no 0.5.0-beta/jvm antes de escrever a máquina, para não construir
sobre suposição:

- bitwise `& | ^ << >> >>>` em `Long`, incluindo máscaras de 8/16/32 bits
- `4294967295 as Long` (não existe literal long)
- `Char` com `>=`/`<=`, escapes `'\n'`/`'\t'`, `c as Int`
- `else if` em cadeia
- `new Long[n]` / `new Int[n]` como campo de classe
- `record` com campo `List<T>`; `enum` em campo de classe
- `try`/`catch (String e)` com `throw "msg"` em função própria
- `String.toUpperCase/indexOf/trim/compareTo/substring(a)/charAt`
- import cross-diretório com `kof.toml` na raiz como module root
- `kof test` por arquivo: vários arquivos de teste no mesmo diretório sem
  colidir em `PKG002`, e sem precisar de `main()`
- leitura de arquivo relativa ao cwd dentro de `kof test` (`File(p).readText()`)

---

# Fase 5A — divergências JVM × JS (04/10/2026)

Validação do mesmo núcleo Kof nos dois targets, antes de construir a UI.
Toolchain `0.5.0-beta`. **Nada reportado como issue** — notas locais.

**Conclusão de cabeçalho: o SG-002 não era o problema.** Toda a semântica
bitwise e numérica do núcleo é idêntica nos dois targets. As duas divergências
encontradas são bugs de geração de código de **fluxo de controle**, sem relação
com bitwise, e ambas estavam no assembler, não na máquina.

---

## D-1. `return` aninhado em ramo `else` descarta o `return` final (JS)

Uma função cujo ramo `else` contém um `if` com `return` antecipado, **seguido
de mais statements nesse mesmo `else`**, perde o `return` final no target JS: a
função devolve `undefined`.

Repro mínimo (`V1`/`V3` da bateria de caracterização):

```kof
Int v1(Int kind, Int value) {
    var address = 0
    if (kind == 1) {
        address = value
    } else {
        if (value < 0) { return 0 }
        address = value + 1
    }
    return address
}
```

```
JVM:  v1(1, 128) = 128
JS:   v1(1, 128) = undefined
```

Sintoma a jusante: `TypeError: Cannot convert undefined to a BigInt` quando o
`undefined` encontra a primeira operação que espera `Long` (o backend JS
modela `Long` como `BigInt`).

### Formatos que NÃO quebram (verificados um a um)

| forma | JS |
|---|---|
| `return` direto no `else`, sem statements depois | ok |
| `return` aninhado em `if` no ramo **then** | ok |
| guard clause de topo + `return` final | ok |
| cadeia de `if`s independentes, cada um com `return` | ok |
| cadeia `if`/`else if`/`else`, cada ramo com `return` | ok |
| `return` dentro de `while` no ramo `else` | ok |
| ponto de saída único | ok |

É especificamente o `return` aninhado em `if` **dentro do `else`**.

### Onde estava no PubLab

Auditoria dos 20 blocos `else` do núcleo encontrou **duas** ocorrências:

1. `publab/assembler/Assembler.kf` → `resolveAddressOperand` — **quebrado**.
   Todo operando de memória e todo destino de salto passa por ela, então
   qualquer `STORE [addr]`, `LOAD r, [addr]`, `JMP`, `JZ` e `JC` montados pelo
   assembler falhavam no JS. 7 de 18 testes da matriz, 5 de 20 do assembler e
   2 de 7 dos exemplos.
2. `publab/assembler/Parser.kf` → `parseMemoryOperand` — mesma forma, **latente**:
   o caminho só é alcançado por um nome reservado entre colchetes (`[X]`,
   `[SP]`), que nenhum teste cobria.

Correção: as duas funções reescritas para ponto de saída único / flag, sem
alterar a semântica (a suíte JVM inteira continua idêntica). Nenhum workaround
espalhado — duas funções, com comentário apontando para esta nota.

---

## D-2. Indexação à direita de `&&`/`||` não respeita curto-circuito (JS)

Uma expressão de **indexação** (`List.get(i)` ou `array[i]`) do lado direito de
`&&`/`||` é avaliada mesmo quando o lado esquerdo já decide o resultado. Uma
guarda de tamanho na mesma condição não protege o acesso.

```kof
Bool t3() {
    var l: List<Int> = listOf()
    if (l.size > 0 && l.get(l.size - 1) == 5) { return true }
    return false
}
```

```
JVM:  false
JS:   Error: Index out of bounds: -1 (size 0)
```

### O curto-circuito em si funciona

| lado direito de `&&` | JS |
|---|---|
| chamada de função com efeito colateral | **não** é avaliada — ok |
| `s.charAt(0)` em String vazia | ok |
| `l.get(0)` / `l.get(size-1)` em lista vazia | **avaliado** — quebra |
| `arr[n - 1]` | **avaliado** — quebra |
| `if` aninhado explícito em vez de `&&` | ok |

Ou seja: o curto-circuito do SG-006 está correto para chamadas; o que é
levantado cedo é a indexação.

### Onde estava no PubLab

Um sítio real: `publab/assembler/Assembler.kf`, pass 1,
`placed.size > 0 && placed.get(placed.size - 1).index() == index`. Disparava
sempre que a **primeira** instrução do programa não resolvia, deixando `placed`
vazia — isto é, em todo teste de diagnóstico (`ASM001`, `ASM002`, `ASM003`,
`ASM010`). Corrigido com `if` aninhado.

O segundo sítio encontrado pela auditoria,
`allFormsShareOperandCount(accepted, formOperandCount(accepted.get(0))) && formOperandCount(accepted.get(0)) != given`,
**não é bug**: o ramo só executa quando `mnemonicExists` é verdadeiro, então
`accepted` nunca está vazia, e o mesmo `accepted.get(0)` já aparece do lado
esquerdo.

---

## Regressão

`tests/js_parity_test.kf` guarda os dois formatos (`D-1`, `D-2`) junto com a
bateria SG-002, e roda nos dois targets. Reintroduzir qualquer um dos dois
quebra a suíte.

## Antes de abrir issue

Checar `grammar.md`, `DECISIONS.md` e `training/anti-patterns/` — o repro do
D-1 é parente do anti-padrão já catalogado de `throw` aninhado em cadeia
if/else no backend JS, e pode ser o mesmo defeito com outra cara. O D-2 toca o
SG-006 (curto-circuito), que está marcado como corrigido desde 09/09, então
vale confirmar se indexação está fora do escopo daquela correção por decisão
ou por omissão.
